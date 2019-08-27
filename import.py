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
            isbn INTEGER NOT NULL, \
            title VARCHAR NOT NULL, \
            author VARCHAR NOT NULL, \
            year INTEGER NOT NULL\
            )")
        print("Table 'books' created")
    except exc.ProgrammingError as err:
        print("Table 'books' already exists")
    db.commit()


# def create_passengers_table():
#     """Create passengers table if doesn't already exist"""
#     try:
#         print("Creating 'passengers' table..")
#         db.execute("CREATE TABLE passengers (\
#             id SERIAL PRIMARY KEY, \
#             name VARCHAR NOT NULL, \
#             flight_id INTEGER REFERENCES flights\
#             )")
#         print("Table 'passengers' created")
#     except exc.ProgrammingError as err:
#         print("Table 'passengers' already exists")
#     db.commit()
#
#
# def insert_flight_data():
#     """Insert data from csv into flights table"""
#     # Get data from csv file
#     print("Getting data from csv..")
#     file = open("flight-info.csv")
#     reader = csv.reader(file)
#
#     # Insert csv data into table
#     print("Inserting data into 'flights' table..")
#     for csv_origin, csv_destination, csv_duration in reader:
#         db.execute("INSERT INTO flights (origin, destination, duration)\
#             VALUES (:origin, :destination, :duration)", {
#             "origin": csv_origin,
#             "destination": csv_destination,
#             "duration": csv_duration
#             })
#     print("Data inserted")
#     db.commit()
#
#
# def delete_flights_table():
#     """Delete flights table"""
#     try:
#         print("Attempting to delete table 'flights'")
#         db.execute("DROP TABLE flights")
#     except exc.ProgrammingError as err:
#         print("Table 'flights' does not exist")
#     else:
#         print("Deleted table 'flights'")
#
#     db.commit()
#
#
# def delete_passengers_table():
#     """Delete passengers table"""
#     try:
#         print("Attempting to delete table 'passengers'")
#         db.execute("DROP TABLE passengers")
#     except exc.ProgrammingError as err:
#         print("Table 'passengers' does not exist")
#     else:
#         print("Deleted table 'passengers'")
#     db.commit()


def main():
    """
    delete_passengers_table()
    delete_flights_table()
    create_flights_table()
    create_passengers_table()
    insert_flight_data()
    """
    create_users_table()
    create_books_table()

if __name__ == "__main__":
    main()
