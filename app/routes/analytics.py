from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.analytics import (
    get_business_analytics,
    get_review_analytics,
)


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/businesses/<int:business_id>/analytics")
@require_business_access
def get_business_analytics_route(business_id):
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    summary, taps_by_waiter, taps_by_card, daily_taps = get_business_analytics(
        business_id=business_id,
        date_from=date_from,
        date_to=date_to,
    )

    review_analytics = get_review_analytics(
        business_id=business_id,
        date_from=date_from,
        date_to=date_to,
    )

    return jsonify({
        "business_id": business_id,
        "total_taps": summary[0],
        "total_waiters": summary[1],
        "latest_review_count": summary[2],
        "review_analytics": review_analytics,
        "taps_by_source": {
            "nfc": summary[3],
            "qr": summary[4],
            "web": summary[5],
        },
        "daily_taps": [
            {
                "date": day.isoformat(),
                "total_taps": total_taps,
            }
            for day, total_taps in daily_taps
        ],
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
