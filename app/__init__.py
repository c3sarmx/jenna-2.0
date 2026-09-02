import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, send_from_directory

load_dotenv()


def create_app():
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"

    app = Flask(
        __name__,
        static_folder=str(frontend_dist),
        static_url_path="",
    )

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

    api_prefix = "/api"

    app.register_blueprint(health_bp, url_prefix=api_prefix)
    app.register_blueprint(businesses_bp, url_prefix=api_prefix)
    app.register_blueprint(waiters_bp, url_prefix=api_prefix)
    app.register_blueprint(review_snapshots_bp, url_prefix=api_prefix)
    app.register_blueprint(analytics_bp, url_prefix=api_prefix)
    app.register_blueprint(taps_bp, url_prefix=api_prefix)
    app.register_blueprint(cards_bp, url_prefix=api_prefix)
    app.register_blueprint(auth_bp, url_prefix=api_prefix)
    app.register_blueprint(business_users_bp, url_prefix=api_prefix)

    @app.get("/")
    def serve_frontend():
        return send_from_directory(frontend_dist, "index.html")

    @app.get("/<path:path>")
    def serve_frontend_path(path):
        file_path = frontend_dist / path

        if file_path.is_file():
            return send_from_directory(frontend_dist, path)

        return send_from_directory(frontend_dist, "index.html")

    return app
