#udacity FSND: Item Catalog
Item Catalog project for the Udacity Full Stack Web Development Nanodegree

This project runs a local web server and allows CRUD operations on a database through an API.

This project involves setting up a local web server with 3rd party authentication. Any user is able to view data on the server, but a user must be authenticated and authorized in order to edit or delete any fields.
The application provides API endpoints for a user to interact with the database. 

To run this website:
 1. Run: python application.py
 2. View the homepage at: http://localhost:5000/authors/
   a. Here you can perform CRUD operations with a successful Google login
 4. View the JSON endpoint at: http://localhost:5000/all_entries_catalog.json


To pre-populate the database with some sample data:
 1. Run: python create_db.py
 2. Run: python populate_db.py
