from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash
    session as login_session
)
import random
import string

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from create_db import Base, Author, Book, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenInfo
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Library Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///library_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is\
            already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    userId = getUserID(login_session['email'])
    if not userId:
        userId = createUser(login_session)
    login_session['user_id'] = userId

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
        -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect/')
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    % login_session['access_token']
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# JSON APIs to view Catalog Information


@app.route('/author_catalog.json')
def authorsJSON():
    authors = session.query(Author).all()
    allAuthorsInCatalog = jsonify(catalog=[a.serialize for a in authors])
    return allAuthorsInCatalog


@app.route('/book_catalog.json')
def booksJSON():
    books = session.query(Book).all()
    allBooksInCatalog = jsonify(catalog=[a.serialize for a in books])
    return allBooksInCatalog


@app.route('/all_entries_catalog.json')
def allEntriesJSON():
    authors = session.query(Author).all()
    books = session.query(Book).all()
    allItemsInCatalog = jsonify(catalog=[a.serialize for a in authors + books])
    return allItemsInCatalog


# Show all authors
@app.route('/')
@app.route('/authors/')
@app.route('/home/')
def showAuthors():
    authors = session.query(Author).order_by(asc(Author.name))
    return render_template('authors.html', authors=authors)

# Create a new author entry


@app.route('/authors/new/', methods=['GET', 'POST'])
def newAuthor():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newAuthor = Author(
            name=request.form['name'], user_id=login_session['username'])
        session.add(newAuthor)
        flash('New Author %s successfully added to catalog' % newAuthor.name)
        session.commit()
        return redirect(url_for('showAuthors'))
    else:
        return render_template('newAuthor.html')

# Edit an Author's name


@app.route('/authors/<int:author_id>/edit/', methods=['GET', 'POST'])
def editAuthor(author_id):
    if 'username' not in login_session:
        return redirect('/login')
    authorToEdit = session.query(Author).filter_by(id=author_id).one()
    if request.method == 'POST':
        if authorToEdit.user_id != login_session['username']:
            return "<script>function invalidLogin() {alert('You are not\
            the user who created this entry. Please create entries of\
            your own to edit or delete.');window.location.href='/authors'}\
            </script><body onload='invalidLogin()'>"
        if request.form['name']:
            authorToEdit.name = request.form['name']
            session.commit()
            flash('Successfully changed authors name to: %s' %
                  authorToEdit.name)
        return redirect(url_for('showAuthors'))
    else:
        return render_template('editAuthor.html', author=authorToEdit)


# Delete an author
@app.route('/authors/<int:author_id>/delete/', methods=['GET', 'POST'])
def deleteAuthor(author_id):
    if 'username' not in login_session:
        return redirect('/login')
    authorToDelete = session.query(
        Author).filter_by(id=author_id).one()

    if authorToDelete.user_id != login_session['username']:
        return "<script>function invalidLogin() {alert('You are not\
            the user who created this entry. Please create entries of\
            your own to edit or delete.');window.location.href='/authors'}\
            </script><body onload='invalidLogin()'>"
    session.delete(authorToDelete)
    flash('%s Successfully Deleted' % authorToDelete.name)
    session.commit()
    return redirect(url_for('showAuthors', author_id=author_id))


# Show a list of author's books
@app.route('/authors/<int:author_id>/')
@app.route('/authors/<int:author_id>/bibliography/')
def showBooks(author_id):
    authorInContext = session.query(Author).filter_by(id=author_id).one()
    books = session.query(Book).filter_by(
        author_id=author_id).all()
    return render_template('books.html', books=books, author=authorInContext)


# Show a description of the book
@app.route('/authors/<int:author_id>/<string:book_title>')
def showBookInformation(author_id, book_title):
    authorInContext = session.query(Author).filter_by(id=author_id).one()
    bookInContext = session.query(Book).filter_by(
        author_id=author_id).filter_by(title=book_title).one()
    return render_template(
        'bookInformation.html', book=bookInContext, author=authorInContext)


# Add a new book entry using the form from the POST response
@app.route('/authors/<int:author_id>/new/', methods=['GET', 'POST'])
def newBookEntry(author_id):
    if 'username' not in login_session:
        return redirect('/login')
    authorInContext = session.query(Author).filter_by(id=author_id).one()
    if request.method == 'POST':
        newBook = Book(
            title=request.form['title'],
            blurb=request.form['description'],
            pub_Year=request.form['pub_Year'],
            author_id=author_id,
            user_id=login_session['username'])
        session.add(newBook)
        session.commit()
        flash('New Book %s Successfully Created' % (newBook.title))
        return redirect(url_for('showBookInformation',
                                author_id=author_id, book_title=newBook.title))
    else:
        return render_template('newBook.html', author=authorInContext)

# Edit information by setting the db for a single book


@app.route('/authors/<int:author_id>/\
    <string:book_title>/edit/', methods=['GET', 'POST'])
def editBookInformation(author_id, book_title):
    if 'username' not in login_session:
        return redirect('/login')
    authorInContext = session.query(Author).filter_by(id=author_id).one()
    bookToEdit = session.query(Book).filter_by(
        author_id=author_id).filter_by(title=book_title).one()
    if request.method == 'POST':
        if authorInContext.user_id != login_session['username']:
            return "<script>function invalidLogin() {alert('You are not\
                the user who created this entry. Please create entries of\
                your own to edit or delete.');window.location.href='/authors'}\
                </script><body onload='invalidLogin()'>"
        if request.form['title']:
            bookToEdit.title = request.form['title']
        if request.form['description']:
            bookToEdit.blurb = request.form['description']
        if request.form['pub_Year']:
            bookToEdit.pub_Year = request.form['pub_Year']
        session.commit()
        flash('Book Information Successfully Edited')
        return redirect(url_for('showBooks', author_id=author_id))
    else:
        return render_template(
            'editBook.html', author=authorInContext, bookToEdit=bookToEdit)


# Delete an author
@app.route('/authors/<int:author_id>/\
    <string:book_title>/delete/', methods=['GET', 'POST'])
def deleteBook(author_id, book_title):
    if 'username' not in login_session:
        return redirect('/login')
    authorInContext = session.query(Author).filter_by(id=author_id).one()
    bookInContext = session.query(Book).filter_by(
        author_id=author_id).filter_by(title=book_title).one()

    if authorInContext.user_id != login_session['username']:
        return "<script>function invalidLogin() {alert('You are not\
            the user who created this entry. Please create entries of\
            your own to edit or delete.');window.location.href='/authors'}\
            </script><body onload='invalidLogin()'>"
    session.delete(bookInContext)
    session.commit()
    flash('Book Information Successfully deleted')
    return redirect(url_for('showBooks', author_id=author_id))


if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
