from flask import Blueprint, jsonify, request

from app.services.analytics import get_business_analytics


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/businesses/<int:business_id>/analytics")
def get_business_analytics_route(business_id):
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    analytics = get_business_analytics(
        business_id=business_id,
        date_from=date_from,
        date_to=date_to,
    )

    return jsonify({
        "business_id": business_id,
        "total_taps": analytics[0],
        "total_waiters": analytics[1],
        "latest_review_count": analytics[2],
    }), 200
