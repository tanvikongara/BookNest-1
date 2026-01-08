from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserBook, Book

stats_bp = Blueprint("stats", __name__, url_prefix="/api/stats")

# All statistics
@stats_bp.route("/summary")
@jwt_required()
def stats_summary():
    user_id = get_jwt_identity()

    # Books marked as read
    read_books = UserBook.query.filter_by(
        user_id=user_id,
        shelf="read"
    ).all()

    books_read = len(read_books)

    pages_read = 0
    author_count = {}
    genre_count = {}

    for ub in read_books:
        book = ub.book
        if book.page_count:
            pages_read += book.page_count

        for author in book.authors or []:
            author_count[author] = author_count.get(author, 0) + 1

        for genre in book.categories or []:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    top_authors = sorted(
        author_count, key=author_count.get, reverse=True
    )[:5]

    top_genres = sorted(
        genre_count, key=genre_count.get, reverse=True
    )[:5]

    return jsonify({
        "books_read": books_read,
        "pages_read": pages_read,
        "top_authors": top_authors,
        "top_genres": top_genres
    }), 200
