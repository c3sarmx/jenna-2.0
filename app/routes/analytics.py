from flask import Blueprint, jsonify, request, session

from app.services.analytics import get_business_analytics
from app.services.business_users import user_has_business_access


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/businesses/<int:business_id>/analytics")
def get_business_analytics_route(business_id):
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "authentication required"
        }), 401

    if not user_has_business_access(user_id, business_id):
        return jsonify({
            "error": "business access denied"
        }), 403

    date_from = request.args.get("from")
    date_to = request.args.get("to")

    summary, taps_by_waiter, taps_by_card = get_business_analytics(
        business_id=business_id,
        date_from=date_from,
        date_to=date_to,
    )

    return jsonify({
        "business_id": business_id,
        "total_taps": summary[0],
        "total_waiters": summary[1],
        "latest_review_count": summary[2],
        "taps_by_source": {
            "nfc": summary[3],
            "qr": summary[4],
            "web": summary[5],
        },
        "taps_by_waiter": [
            {
                "waiter_id": waiter[0],
                "waiter_name": waiter[1],
                "total_taps": waiter[2],
            }
            for waiter in taps_by_waiter
        ],
        "taps_by_card": [
            {
                "card_id": card[0],
                "public_id": card[1],
                "waiter_id": card[2],
                "waiter_name": card[3],
                "total_taps": card[4],
            }
            for card in taps_by_card
        ],
    }), 200
