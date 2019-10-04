"""This program sets up the dabatase for the Book Worm Reviews website"""

import csv
import os

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def create_users_table():
    """Create users table if doesn't already exist"""
    try:
        print("Creating 'users' table..")
        db.execute("CREATE TABLE users (\
            id SERIAL PRIMARY KEY, \
            username VARCHAR NOT NULL, \
            password VARCHAR NOT NULL\
            )")
        print("Table 'users' created")
    except exc.ProgrammingError as err:
        print("Table 'users' already exists")
    db.commit()

def create_books_table():
    """Create books table if doesn't already exist"""
    try:
        print("Creating 'books' table..")
        db.execute("CREATE TABLE books (\
            id SERIAL PRIMARY KEY, \
            isbn VARCHAR NOT NULL, \
            title VARCHAR NOT NULL, \
            author VARCHAR NOT NULL, \
            year INTEGER NOT NULL\
            )")
        print("Table 'books' created")
    except exc.ProgrammingError as err:
        print("Table 'books' already exists")
    db.commit()

def insert_books_data():
    """Insert data from csv into books table"""
    # Get data from csv file
    print("Getting data from csv..")
    file = open("books.csv")
    reader = csv.reader(file)

    # Insert csv data into table
    print("Inserting data into 'books' table..")
    for isbn, title, author, year in reader:
        try:
            db.execute("INSERT INTO books (isbn, title, author, year)\
                VALUES (:isbn, :title, :author, :year)", {
                "isbn": isbn, "title": title, "author": author, "year": year })
        except exc.DataError as err:
            print("Invalid entry in csv file")
        db.commit()
    print("Data inserted")

def delete_users_table():
    """Delete users table"""
    try:
        print("Attempting to delete table 'users'")
        db.execute("DROP TABLE users")
    except exc.ProgrammingError as err:
        print("Table 'users' does not exist")
    else:
        print("Deleted table 'users'")

    db.commit()

def delete_books_table():
    """Delete books table"""
    try:
        print("Attempting to delete table 'books'")
        db.execute("DROP TABLE books")
    except exc.ProgrammingError as err:
        print("Table 'books' does not exist")
    else:
        print("Deleted table 'books'")

    db.commit()


def main():
    """
    delete_users_table()
    delete_books_table()
    create_users_table()
    create_books_table()
    insert_books_data()
    """

if __name__ == "__main__":
    main()
