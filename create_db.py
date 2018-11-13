import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    # Creates a user object used for authorizing CRUD operations

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=True)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
        }


class Author(Base):
    # Top level object for the library, it has a list of books

    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    book = relationship('Book', cascade='all, delete-orphan')

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id,
        }


class Book(Base):
    # bottom level object, it contains data that we display

    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    blurb = Column(String(250), nullable=True)
    pub_Year = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    author_id = Column(Integer, ForeignKey('author.id'))
    user = relationship(User)
    author = relationship(Author)

    @property
    def serialize(self):
        return {
            'author_id': self.author_id,
            'title': self.title,
            'id': self.id,
            'blurb': self.blurb,
            'pub_Year': self.pub_Year,
            'user_id': self.user_id,
        }


engine = create_engine('sqlite:///library_catalog.db')
Base.metadata.create_all(engine)
