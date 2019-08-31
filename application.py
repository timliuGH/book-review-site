import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
    session.clear()
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user with username and password"""
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
        return redirect("/login")

    # Display default register page
    elif request.method == "GET":
        return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        # Save submitted username and password
        form_username = request.form.get("username")
        form_password = request.form.get("password")

        # Find username in database
        user = db.execute("SELECT id, username, password FROM users WHERE username=:username",
            {"username": form_username}).fetchone()

        # Handle case where username does not exist
        if user == None:
            return render_template("login.html", message="We don't know this Glow Worm!")

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
    """Display page after user logs in"""
    user_id = session.get("user_id")
    if user_id is None:
        return render_template("home.html")
    else:
        return render_template("index.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/")


@app.route("/search", methods=["POST"])
def search():
    """Display search results"""
    title = request.form.get("title").title()
    author = request.form.get("author").title()
    isbn = request.form.get("isbn")

    if title == "" and author == "" and isbn == "":
        return render_template("index.html")

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
    print("num books:")
    print(len(books))

    return render_template("index.html", books=books, count=len(books))
