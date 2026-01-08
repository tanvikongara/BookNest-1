from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Review, UserBook

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")

# Create a review for a book
@reviews_bp.route("", methods=["POST"])
@jwt_required()
def create_review():
    user_id = get_jwt_identity()
    data = request.get_json()

    book_id = data.get("book_id")
    review_text = data.get("review_text")

    if not book_id or not review_text:
        return jsonify({"error": "book_id and review_text required"}), 400

    user_book = UserBook.query.filter_by(
        user_id=user_id,
        book_id=book_id
    ).first()

    if not user_book:
        return jsonify({"error": "Book not on user's shelf"}), 400

    review = Review(
        user_id=user_id,
        book_id=book_id,
        rating_snapshot=user_book.rating,
        review_text=review_text
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "Review created"}), 201


# Get all the reviews for a book
@reviews_bp.route("/<int:book_id>", methods=["GET"])
def get_reviews_for_book(book_id):
    reviews = Review.query.filter_by(book_id=book_id).order_by(
        Review.created_at.desc()
    ).all()

    results = []
    for r in reviews:
        results.append({
            "username": r.user.username,
            "rating": r.rating_snapshot,
            "review_text": r.review_text,
            "created_at": r.created_at.isoformat()
        })

    return jsonify(results), 200
