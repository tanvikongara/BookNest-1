from datetime import datetime
from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    google_books_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    authors = db.Column(db.ARRAY(db.String))
    description = db.Column(db.Text)
    page_count = db.Column(db.Integer)
    categories = db.Column(db.ARRAY(db.String))
    thumbnail_url = db.Column(db.String)
    published_date = db.Column(db.String)
    isbn_10 = db.Column(db.String(20))
    isbn_13 = db.Column(db.String(20))


class UserBook(db.Model):
    __tablename__ = "user_books"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)

    shelf = db.Column(db.String(30), nullable=False)
    rating = db.Column(db.Float)
    date_started = db.Column(db.Date)
    date_finished = db.Column(db.Date)

    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="user_books")
    book = db.relationship("Book", backref="user_books")
