from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_db import Base, Author, Book, User

engine = create_engine('sqlite:///library_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create initial admin user
adminUser = User(
    name="admin",
    email="theLibrarian@congress.org",
    picture="anyPicturefound",
)
session.add(adminUser)
session.commit()

# Create authors
auth1 = Author(
    user=adminUser,
    name="Patrick Rothfuss",
)
session.add(auth1)
session.commit()

auth2 = Author(
    name="John Steinbeck",
    user=adminUser,
)
session.add(auth2)
session.commit()

auth3 = Author(
    name="Andy Weir",
    user=adminUser,
)
session.add(auth3)
session.commit()


# Create books
book_1_1 = Book(
    title="The Name of the Wind",
    blurb="Told in Kvothe's own voice, this is the tale of the magically\
        gifted young man who grows to be the most notorious wizard his\
        world has ever seen. The intimate narrative of his childhood in\
        a troupe of traveling players, his years spent as a near-feral\
        orphan in a crime-ridden city, his daringly brazen yet successful\
        bid to enter a legendary school of magic, and his life as a\
        fugitive after the murder of a king form a gripping coming-of-age\
        story unrivaled in recent literature.",
    pub_Year=2007,
    user=adminUser,
    author=auth1
)
session.add(book_1_1)
session.commit()

book_1_2 = Book(
    title="The Wise Man's Fear",
    blurb="'There are three things all wise men fear: the sea in storm, a\
    night with no moon, and the anger of a gentle man.' My name is Kvothe.\
    You may have heard of me.",
    pub_Year=2011,
    user=adminUser,
    author=auth1
)
session.add(book_1_2)
session.commit()

book_2_1 = Book(
    title="East of Eden",
    blurb="Each working day from January 29 to November 1, 1951, John\
    Steinbeck warmed up to the work of writing East of Eden with a letter\
    to the late Pascal Covici, his friend and editor at The Viking Press.\
    It was his way, he said, of 'getting my mental arm in shape to pitch\
    a good game.'",
    pub_Year=1952,
    user=adminUser,
    author=auth2
)
session.add(book_2_1)
session.commit()

book_3_1 = Book(
    title="The Martian",
    blurb="Six days ago, astronaut Mark Watney became one of the first\
    people to walk on Mars. Now, he's sure he'll be the first person\
    to die there.",
    pub_Year=2014,
    user=adminUser,
    author=auth3
)
session.add(book_3_1)
session.commit()

book_3_2 = Book(
    title="Artemis",
    blurb="Artemis is a 2017 science fiction novel written by Andy Weir.\
    The novel takes place in the late 2080s and is set in Artemis, the first\
    and only city on the Moon. It follows the life of porter and smuggler\
    Jasmine 'Jazz' Bashara as she gets caught up in a conspiracy for control\
    of the city.",
    pub_Year=2017,
    user=adminUser,
    author=auth3
)
session.add(book_3_2)
session.commit()
