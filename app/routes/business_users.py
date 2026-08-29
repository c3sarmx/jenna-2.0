from flask import Blueprint, jsonify

from app.auth.decorators import require_business_access
from app.services.business_users import get_business_users


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
