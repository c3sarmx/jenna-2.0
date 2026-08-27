from flask import Blueprint, jsonify, request

from app.services.taps import create_tap

from app.services.cards import (
    create_card,
    get_card_by_public_id,
    get_cards_by_business,
)


cards_bp = Blueprint("cards", __name__)


@cards_bp.post("/businesses/<int:business_id>/cards")
def create_card_route(business_id):
    data = request.get_json()

    waiter_id = data.get("waiter_id")

    if not waiter_id:
        return jsonify({
            "error": "waiter_id is required"
        }), 400

    card = create_card(
        business_id=business_id,
        waiter_id=waiter_id,
    )

    return jsonify({
        "id": card[0],
        "business_id": card[1],
        "waiter_id": card[2],
        "public_id": card[3],
        "active": card[4],
        "created_at": card[5].isoformat(),
    }), 201


@cards_bp.get("/businesses/<int:business_id>/cards")
def get_cards_route(business_id):
    cards = get_cards_by_business(business_id)

    return jsonify([
        {
            "id": card[0],
            "business_id": card[1],
            "waiter_id": card[2],
            "waiter_name": card[3],
            "public_id": card[4],
            "active": card[5],
            "created_at": card[6].isoformat(),
        }
        for card in cards
    ]), 200


@cards_bp.get("/r/<string:public_id>")
def resolve_card_route(public_id):
    card = get_card_by_public_id(public_id)

    if not card:
        return jsonify({
            "error": "card not found"
        }), 404

    if not card[6]:
        return jsonify({
            "error": "card inactive"
        }), 410

    source = request.args.get("source", "web")

    if source not in ("nfc", "qr", "web"):
        return jsonify({
            "error": "invalid source"
        }), 400

    tap = create_tap(
        business_id=card[1],
        waiter_id=card[3],
        source=source,
    )

    return jsonify({
        "card_id": card[0],
        "business_id": card[1],
        "business_name": card[2],
        "waiter_id": card[3],
        "waiter_name": card[4],
        "public_id": card[5],
        "active": card[6],
        "tap_id": tap[0],
        "tap_source": tap[3],
    }), 200
