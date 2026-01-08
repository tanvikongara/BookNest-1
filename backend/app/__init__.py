from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from .routes.auth import auth_bp
from .routes.books import books_bp
from .routes.user_books import user_books_bp
from .routes.reviews import reviews_bp
from .routes.stats import stats_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(user_books_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(stats_bp)


    return app
