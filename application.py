import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Set up database
#engine = create_engine(os.getenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if ("user_id" in session):
        user = User.query.get(session["user_id"])
        return render_template("user.html", name=user.name)
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():

    # Get form information.
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    # Add user.
    if (not User.query.filter_by(username=username).all() and not User.query.filter_by(email=email).all()):
        user = User(name=name, username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return render_template("user.html", name= user.name)
    else:
        return render_template("error.html", message="The username or passwrod is used by another user")


@app.route("/signin", methods=["POST"])
def signin():

    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).one()

    if (user):
        if (user.password == password):
            session["user_id"] = user.id
            return render_template("user.html", name= user.name)
        else:
            return render_template("error.html", message= "Authentication Error Invalid Password")
    else:
        return render_template("error.html", message= "User not registered")

@app.route("/books/<int:book_id>")
def book(book_id):
    """List details about a single Book."""

    # Make sure book exists.
    book = Book.query.get(book_id)
    if book is None:
        return render_template("error.html", message="No such Book.")

    return render_template("book.html", book=book)

@app.route("/search", methods=["POST"])
def search():
    search = request.form.get("search")
    books = Book.query.filter(or_(Book.isbn.ilike("%" + search +"%"), Book.title.ilike("%" + search +"%"), Book.author.ilike("%" + search +"%"))).all()
    return render_template("books.html", books=books)
