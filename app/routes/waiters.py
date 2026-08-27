from flask import Blueprint, jsonify, request

from app.services.waiters import create_waiter, get_waiters_by_business


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


@waiters_bp.get("/businesses/<int:business_id>/waiters")
def get_waiters_route(business_id):
    waiters = get_waiters_by_business(business_id)

    return jsonify([
        {
            "id": waiter[0],
            "business_id": waiter[1],
            "name": waiter[2],
            "active": waiter[3],
            "created_at": waiter[4].isoformat(),
        }
        for waiter in waiters
    ]), 200
