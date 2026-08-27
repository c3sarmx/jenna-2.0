from flask import Blueprint, jsonify, request, session

from app.services.businesses import create_business
from app.services.business_users import (
    assign_user_to_business,
    get_user_businesses,
)


businesses_bp = Blueprint("businesses", __name__)


@businesses_bp.post("/businesses")
def create_business_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "authentication required"
        }), 401

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

    assign_user_to_business(
        user_id=user_id,
        business_id=business[0],
        role="owner",
    )

    return jsonify({
        "id": business[0],
        "name": business[1],
        "google_review_url": business[2],
        "created_at": business[3].isoformat()
    }), 201


@businesses_bp.get("/businesses")
def get_businesses_route():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "authentication required"
        }), 401

    businesses = get_user_businesses(user_id)

    return jsonify([
        {
            "id": business[0],
            "name": business[1],
            "role": business[2],
        }
        for business in businesses
    ]), 200
