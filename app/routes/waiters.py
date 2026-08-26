from flask import Blueprint, jsonify, request

from app.services.waiters import create_waiter


waiters_bp = Blueprint("waiters", __name__)


@waiters_bp.post("/businesses/<int:business_id>/waiters")
def create_waiter_route(business_id):
    data = request.get_json()

    name = data.get("name")

    if not name:
        return jsonify({
            "error": "name is required"
        }), 400

    waiter = create_waiter(
        business_id=business_id,
        name=name
    )

    return jsonify({
        "id": waiter[0],
        "business_id": waiter[1],
        "name": waiter[2],
        "active": waiter[3],
        "created_at": waiter[4].isoformat()
    }), 201
