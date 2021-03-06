import os
import requests

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
from goodreads_api_key import KEY

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def home():
    """Initial landing page; logs off last user"""
    session.clear()
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """GET: Display registration page
       POST: Register new user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Handle if username already exists
        check_username = db.execute("SELECT username FROM users \
            WHERE username=:username", {"username": username}).fetchone()
        db.commit()
        if check_username != None:
            return render_template("register.html", message="Username already taken!")

        # Add username and password to table and send user to login page
        db.execute("INSERT INTO users (username, password) \
        VALUES (:username, :password)", {"username": username, "password": password})
        db.commit()
        return render_template("login.html", new_user="Thanks for registering!")

    elif request.method == "GET":
        return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    """GET: Display login page
       POST: Log user in"""

    if request.method == "POST":
        form_username = request.form.get("username")
        form_password = request.form.get("password")

        # Find username in database
        user = db.execute("SELECT id, username, password FROM users WHERE username=:username",
            {"username": form_username}).fetchone()

        # Handle case where username does not exist
        if user == None:
            return render_template("login.html", message="We don't know this Book Worm!")

        # Handle incorrect password
        if user.password != form_password:
            return render_template("login.html", message="Incorrect password!")

        # Handle correct password, i.e. log in user
        session["user_id"] = user.id
        return redirect("/index")

    elif request.method == "GET":
        return render_template("login.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    """GET: Display user's initial page after logging in
       POST: Display search results"""

    if request.method == "GET":
        # Ensure user is logged in
        user_id = session.get("user_id")
        if user_id is None:
            return render_template("login.html", message="Please log in!")
        else:
            return render_template("index.html")
    elif request.method == "POST":
        title = request.form.get("title").title()
        author = request.form.get("author").title()
        isbn = request.form.get("isbn")

        # Handle blank queries
        if title == "" and author == "" and isbn == "":
            return render_template("index.html")

        # Get books that match queries
        books = search(title, author, isbn)
        return render_template("index.html", books=books, count=len(books))


def search(title, author, isbn):
    """Search for books based on user query"""
    # Collect unique results from each query option (title, author, isbn)
    books = set()
    if title != "":
        title_matches = db.execute("SELECT * FROM books WHERE title LIKE :title", {"title": '%' + title + '%'}).fetchall()
        for book in title_matches:
            books.add(tuple(book))
    if author != "":
        author_matches = db.execute("SELECT * FROM books WHERE author LIKE :author", {"author": '%' + author + '%'}).fetchall()
        for book in author_matches:
            books.add(tuple(book))
    if isbn != "":
        isbn_matches = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": '%' + isbn + '%'}).fetchall()
        for book in isbn_matches:
            books.add(tuple(book))
    return books


@app.route("/logout")
def logout():
    """Log user out and send user to initial landing page"""
    session.clear()
    return redirect("/")


@app.route("/book/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    """GET: List details about a single book
       POST: Add user review to database and update page"""
    # Ensure user is logged in
    user_id = session.get("user_id")
    if user_id is None:
        return render_template("login.html", message="Please log in!")
    if request.method == "POST":
        rating = request.form.get("rating")
        review = request.form.get("review")

        # Check if current user has already made a review on current book
        existing_row = db.execute("SELECT * FROM reviews \
            WHERE user_id=:user_id AND book_id=:book_id",
            {"user_id": user_id, "book_id": book_id}).fetchone()
        if existing_row == None:
            db.execute("INSERT INTO reviews (user_id, book_id, review, rating) \
                VALUES (:user_id, :book_id, :review, :rating)",
                {"user_id": user_id, "book_id": book_id, "review": review, "rating": rating})
        else:
            db.execute("UPDATE reviews SET review=:review, rating=:rating \
                WHERE user_id=:user_id AND book_id=:book_id",
                {"review": review, "rating": rating, "user_id": user_id, "book_id": book_id})

    # Display most current details and reviews for current book
    book = db.execute("SELECT * FROM books WHERE id=:book_id", {"book_id": book_id}).fetchone()
    reviews = db.execute("SELECT * FROM reviews JOIN users ON users.id=reviews.user_id WHERE book_id=:book_id",
        {"book_id": book_id}).fetchall()
    avg_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id=:book_id", {"book_id": book_id}).fetchone()
    print(avg_rating)
    if avg_rating[0] != None:
        avg_rating = round(float(avg_rating[0]), 2)
    else:
        avg_rating = None
    num_ratings = db.execute("SELECT COUNT(*) FROM reviews GROUP BY book_id HAVING book_id=:book_id", {"book_id": book_id}).fetchone()
    if num_ratings != None:
        num_ratings = num_ratings[0]
    else:
        num_ratings = None
    goodreads = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": book.isbn}).json()
    print(goodreads['books'][0]['average_rating'])
    db.commit()
    return render_template("book.html", book=book, reviews=reviews, goodreads=goodreads['books'][0], avg_rating=avg_rating, num_ratings=num_ratings)


@app.route("/api/<isbn>")
def book_api(isbn):
    """Return book title, author, publication date, ISBN number, review count,
       and average rating in JSON format"""

    # Get book details based on isbn in http request
    book_details = db.execute("SELECT id, title, author, year FROM books WHERE isbn=:isbn",
        {"isbn": isbn}).fetchone()
    print("book_details")
    if book_details == None:
        print("heyo")
        return render_template("error.html"), 404

    # Get number of reviews
    review_count = db.execute("SELECT COUNT(*) FROM reviews GROUP BY book_id HAVING book_id=:book_id",
        {"book_id": book_details['id']}).fetchone()

    # Get average book rating
    average_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id=:book_id",
        {"book_id": book_details['id']}).fetchone()
    # Convert to float so can be put in JSON format
    average_rating = round(float(average_rating[0]), 2)

    return jsonify({
            "title": book_details['title'],
            "author": book_details['author'],
            "year": book_details['year'],
            "isbn": isbn,
            "review_count": review_count[0],
            "average_rating": average_rating
        })
