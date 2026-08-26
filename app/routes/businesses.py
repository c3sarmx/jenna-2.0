from flask import Blueprint, jsonify, request

from app.services.businesses import create_business


businesses_bp = Blueprint("businesses", __name__)


@businesses_bp.post("/businesses")
def create_business_route():
    data = request.get_json()

    name = data.get("name")
    google_review_url = data.get("google_review_url")

    if not name:
        return jsonify({
            "error": "name is required"
        }), 400

    business = create_business(
        name=name,
        google_review_url=google_review_url
    )

    return jsonify({
        "id": business[0],
        "name": business[1],
        "google_review_url": business[2],
        "created_at": business[3].isoformat()
    }), 201
