import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app():
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")

    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is required")

    app.config["SECRET_KEY"] = secret_key
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    )

    from app.routes.health import health_bp
    from app.routes.businesses import businesses_bp
    from app.routes.waiters import waiters_bp
    from app.routes.review_snapshots import review_snapshots_bp
    from app.routes.analytics import analytics_bp
    from app.routes.taps import taps_bp
    from app.routes.cards import cards_bp
    from app.routes.auth import auth_bp
    from app.routes.business_users import business_users_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(businesses_bp)
    app.register_blueprint(waiters_bp)
    app.register_blueprint(review_snapshots_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(taps_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(business_users_bp)

    return app
