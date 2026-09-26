from flask import Blueprint, jsonify, redirect, request

from app.auth.decorators import require_business_access
from app.services.taps import create_tap

from app.services.cards import (
    create_card,
    get_card_by_public_id,
    get_cards_by_business,
    update_card_status,
)


cards_bp = Blueprint("cards", __name__)


@cards_bp.post("/businesses/<int:business_id>/cards")
@require_business_access
def create_card_route(business_id):
    data = request.get_json()

    waiter_id = data.get("waiter_id")

    if not waiter_id:
        return jsonify({
            "error": "waiter_id is required"
        }), 400

    try:
        card = create_card(
            business_id=business_id,
            waiter_id=waiter_id,
        )
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    return jsonify({
        "id": card[0],
        "business_id": card[1],
        "waiter_id": card[2],
        "public_id": card[3],
        "active": card[4],
        "created_at": card[5].isoformat(),
    }), 201


@cards_bp.get("/businesses/<int:business_id>/cards")
@require_business_access
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
    print(
        "CARD DEBUG:",
        repr(public_id),
        "length=",
        len(public_id),
        flush=True,
    )

    card = get_card_by_public_id(public_id)

    print(
        "CARD DEBUG RESULT:",
        repr(card),
        flush=True,
    )

    if not card:
        return jsonify({
            "error": "card not found"
        }), 404

    if not card[7] or not card[9]:
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
        waiter_id=card[4],
        source=source,
        card_id=card[0],
    )

    return redirect(card[3])


@cards_bp.patch("/businesses/<int:business_id>/cards/<int:card_id>")
@require_business_access
def update_card_status_route(business_id, card_id):
    data = request.get_json()

    if not data or "active" not in data:
        return jsonify({
            "error": "active is required"
        }), 400

    if not isinstance(data["active"], bool):
        return jsonify({
            "error": "active must be boolean"
        }), 400

    card = update_card_status(
        business_id=business_id,
        card_id=card_id,
        active=data["active"],
    )

    if not card:
        return jsonify({
            "error": "card not found"
        }), 404

    return jsonify({
        "id": card[0],
        "business_id": card[1],
        "waiter_id": card[2],
        "public_id": card[3],
        "active": card[4],
        "created_at": card[5].isoformat(),
    }), 200
