import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    from app.routes.health import health_bp
    from app.routes.businesses import businesses_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(businesses_bp)

    return app
