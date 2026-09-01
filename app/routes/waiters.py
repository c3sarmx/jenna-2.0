from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.waiters import (
    create_waiter,
    get_waiters_by_business,
    update_waiter_status,
)


waiters_bp = Blueprint("waiters", __name__)


@waiters_bp.post("/businesses/<int:business_id>/waiters")
@require_business_access
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
@require_business_access
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

@waiters_bp.patch("/businesses/<int:business_id>/waiters/<int:waiter_id>")
@require_business_access
def update_waiter_status_route(business_id, waiter_id):
    data = request.get_json()

    if not data or "active" not in data:
        return jsonify({
            "error": "active is required"
        }), 400

    if not isinstance(data["active"], bool):
        return jsonify({
            "error": "active must be boolean"
        }), 400

    waiter = update_waiter_status(
        business_id=business_id,
        waiter_id=waiter_id,
        active=data["active"],
    )

    if not waiter:
        return jsonify({
            "error": "waiter not found"
        }), 404

    return jsonify({
        "id": waiter[0],
        "business_id": waiter[1],
        "name": waiter[2],
        "active": waiter[3],
        "created_at": waiter[4].isoformat(),
    }), 200
