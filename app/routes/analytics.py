from flask import Blueprint, jsonify

from app.services.analytics import get_business_analytics


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/businesses/<int:business_id>/analytics")
def get_business_analytics_route(business_id):
    analytics = get_business_analytics(business_id)

    return jsonify({
        "business_id": business_id,
        "total_taps": analytics[0],
        "total_waiters": analytics[1],
        "latest_review_count": analytics[2],
    }), 200
