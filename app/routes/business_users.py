from flask import Blueprint, jsonify, request
from psycopg.errors import UniqueViolation

from app.auth.decorators import (
    require_business_access,
    require_business_role,
)
from app.services.business_users import (
    assign_user_to_business,
    get_business_users,
)
from app.services.users import get_user_by_email


business_users_bp = Blueprint("business_users", __name__)


@business_users_bp.get("/businesses/<int:business_id>/users")
@require_business_access
def get_business_users_route(business_id):
    users = get_business_users(business_id)

    return jsonify([
        {
            "id": user[0],
            "email": user[1],
            "active": user[2],
            "role": user[3],
            "created_at": user[4].isoformat(),
        }
        for user in users
    ]), 200


@business_users_bp.post("/businesses/<int:business_id>/users")
@require_business_role("owner")
def add_business_user_route(business_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "request body is required"
        }), 400

    email = data.get("email")
    role = data.get("role")

    if not email:
        return jsonify({
            "error": "email is required"
        }), 400

    if role != "admin":
        return jsonify({
            "error": "role must be admin"
        }), 400

    user = get_user_by_email(email)

    if not user:
        return jsonify({
            "error": "user not found"
        }), 404

    try:
        business_user = assign_user_to_business(
            user_id=user[0],
            business_id=business_id,
            role=role,
        )
    except UniqueViolation:
        return jsonify({
            "error": "user already has access to this business"
        }), 409

    return jsonify({
        "id": business_user[0],
        "user_id": business_user[1],
        "business_id": business_user[2],
        "role": business_user[3],
        "created_at": business_user[4].isoformat(),
    }), 201
