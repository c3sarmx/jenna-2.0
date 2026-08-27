import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    from app.routes.health import health_bp
    from app.routes.businesses import businesses_bp
    from app.routes.waiters import waiters_bp
    from app.routes.review_snapshots import review_snapshots_bp
    from app.routes.analytics import analytics_bp
    from app.routes.taps import taps_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(businesses_bp)
    app.register_blueprint(waiters_bp)
    app.register_blueprint(review_snapshots_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(taps_bp)

    return app
