from datetime import date

from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.analytics import (
    get_business_analytics,
    get_review_analytics,
    get_waiter_weekly_analytics,
)


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/businesses/<int:business_id>/analytics")
@require_business_access
def get_business_analytics_route(business_id):
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    parsed_date_from = None
    parsed_date_to = None

    if date_from:
        try:
            parsed_date_from = date.fromisoformat(date_from)
        except ValueError:
            return jsonify({
                "error": "invalid from date"
            }), 400

    if date_to:
        try:
            parsed_date_to = date.fromisoformat(date_to)
        except ValueError:
            return jsonify({
                "error": "invalid to date"
            }), 400

    if (
        parsed_date_from is not None
        and parsed_date_to is not None
        and parsed_date_from > parsed_date_to
    ):
        return jsonify({
            "error": "invalid date range"
        }), 400

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


@analytics_bp.get(
    "/businesses/<int:business_id>/analytics/waiters/weekly"
)
@require_business_access
def get_waiter_weekly_analytics_route(business_id):
    week_start = request.args.get("week_start")

    if not week_start:
        return jsonify({
            "error": "week_start is required"
        }), 400

    try:
        parsed_week_start = date.fromisoformat(week_start)
    except ValueError:
        return jsonify({
            "error": "invalid week_start date"
        }), 400

    analytics = get_waiter_weekly_analytics(
        business_id=business_id,
        week_start=parsed_week_start,
    )

    return jsonify([
        {
            **item,
            "week_start": item["week_start"].isoformat(),
            "week_end": item["week_end"].isoformat(),
        }
        for item in analytics
    ]), 200
