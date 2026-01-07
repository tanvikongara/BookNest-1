from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import UserBook, Book

user_books_bp = Blueprint("user_books", __name__, url_prefix="/api/user-books")

VALID_SHELVES = {
    "want_to_read",
    "currently_reading",
    "read",
    "dnf",
    "private"
}

# Add a book to a shelf or move an existing book to a different shelf
@user_books_bp.route("", methods=["POST"])
@jwt_required()
def add_or_update_book():
    user_id = get_jwt_identity()
    data = request.get_json()

    book_id = data.get("book_id")
    shelf = data.get("shelf")

    if not book_id or shelf not in VALID_SHELVES:
        return jsonify({"error": "Invalid book_id or shelf"}), 400

    user_book = UserBook.query.filter_by(
        user_id=user_id,
        book_id=book_id
    ).first()

    if user_book:
        user_book.shelf = shelf
    else:
        user_book = UserBook(
            user_id=user_id,
            book_id=book_id,
            shelf=shelf
        )
        db.session.add(user_book)

    db.session.commit()

    return jsonify({"message": "Shelf updated"}), 200

# Get all books for the logged-in user on a specific shelf
@user_books_bp.route("", methods=["GET"])
@jwt_required()
def get_shelf():
    user_id = get_jwt_identity()
    shelf = request.args.get("shelf")

    if shelf not in VALID_SHELVES:
        return jsonify({"error": "Invalid shelf"}), 400

    user_books = UserBook.query.filter_by(
        user_id=user_id,
        shelf=shelf
    ).all()

    results = []
    for ub in user_books:
        book = ub.book
        results.append({
            "user_book_id": ub.id,
            "book_id": book.id,
            "title": book.title,
            "authors": book.authors,
            "thumbnail_url": book.thumbnail_url,
            "rating": ub.rating
        })

    return jsonify(results), 200

# Update shelf or rating for a specific user-book entry
@user_books_bp.route("/<int:user_book_id>", methods=["PATCH"])
@jwt_required()
def update_user_book(user_book_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    user_book = UserBook.query.filter_by(
        id=user_book_id,
        user_id=user_id
    ).first()

    if not user_book:
        return jsonify({"error": "Book not found"}), 404

    if "shelf" in data:
        if data["shelf"] not in VALID_SHELVES:
            return jsonify({"error": "Invalid shelf"}), 400
        user_book.shelf = data["shelf"]

    if "rating" in data:
        user_book.rating = data["rating"]

    db.session.commit()

    return jsonify({"message": "Book updated"}), 200


# Remove a book from the user's library entirely
@user_books_bp.route("/<int:user_book_id>", methods=["DELETE"])
@jwt_required()
def remove_book(user_book_id):
    user_id = get_jwt_identity()

    user_book = UserBook.query.filter_by(
        id=user_book_id,
        user_id=user_id
    ).first()

    if not user_book:
        return jsonify({"error": "Book not found"}), 404

    db.session.delete(user_book)
    db.session.commit()

    return jsonify({"message": "Book removed"}), 200
