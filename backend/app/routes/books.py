import requests
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Book
from flask_jwt_extended import jwt_required

books_bp = Blueprint("books", __name__, url_prefix="/api/books")


@books_bp.route("/search")
@jwt_required()
def search_books():
    query = request.args.get("q")

    if not query:
        return jsonify({"error": "Query parameter required"}), 400

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": 10
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []

    for item in data.get("items", []):
        volume = item.get("volumeInfo", {})
        results.append({
            "google_books_id": item.get("id"),
            "title": volume.get("title"),
            "authors": volume.get("authors", []),
            "thumbnail_url": volume.get("imageLinks", {}).get("thumbnail")
        })

    return jsonify(results), 200


@books_bp.route("", methods=["POST"])
@jwt_required()
def save_book():
    data = request.get_json()
    google_books_id = data.get("google_books_id")

    if not google_books_id:
        return jsonify({"error": "google_books_id required"}), 400

    existing = Book.query.filter_by(google_books_id=google_books_id).first()
    if existing:
        return jsonify({"book_id": existing.id}), 200

    url = f"https://www.googleapis.com/books/v1/volumes/{google_books_id}"
    response = requests.get(url)
    volume = response.json().get("volumeInfo", {})

    book = Book(
        google_books_id=google_books_id,
        title=volume.get("title"),
        authors=volume.get("authors"),
        description=volume.get("description"),
        page_count=volume.get("pageCount"),
        categories=volume.get("categories"),
        thumbnail_url=volume.get("imageLinks", {}).get("thumbnail"),
        published_date=volume.get("publishedDate")
    )

    for identifier in volume.get("industryIdentifiers", []):
        if identifier["type"] == "ISBN_10":
            book.isbn_10 = identifier["identifier"]
        if identifier["type"] == "ISBN_13":
            book.isbn_13 = identifier["identifier"]

    db.session.add(book)
    db.session.commit()

    return jsonify({"book_id": book.id}), 201
