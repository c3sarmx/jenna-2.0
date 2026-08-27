from flask import Blueprint, jsonify, request

from app.services.analytics import get_business_analytics


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/businesses/<int:business_id>/analytics")
def get_business_analytics_route(business_id):
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    summary, taps_by_waiter = get_business_analytics(
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
    }), 200
