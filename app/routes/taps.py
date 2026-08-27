from flask import Blueprint, jsonify, request

from app.services.taps import create_tap, get_taps_by_business


taps_bp = Blueprint("taps", __name__)


@taps_bp.post("/businesses/<int:business_id>/taps")
def create_tap_route(business_id):
    data = request.get_json()

    waiter_id = data.get("waiter_id")
    source = data.get("source", "nfc")

    tap = create_tap(
        business_id=business_id,
        waiter_id=waiter_id,
        source=source,
    )

    return jsonify({
        "id": tap[0],
        "business_id": tap[1],
        "waiter_id": tap[2],
        "source": tap[3],
        "created_at": tap[4].isoformat(),
        "card_id": tap[5],
    }), 201


@taps_bp.get("/businesses/<int:business_id>/taps")
def get_taps_route(business_id):
    taps = get_taps_by_business(business_id)

    return jsonify([
        {
            "id": tap[0],
            "business_id": tap[1],
            "waiter_id": tap[2],
            "source": tap[3],
            "created_at": tap[4].isoformat(),
            "card_id": tap[5],
        }
        for tap in taps
    ]), 200
