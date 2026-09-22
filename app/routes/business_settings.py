from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.business_settings import (
    get_business_settings,
    set_weekly_reviews_per_waiter,
)


business_settings_bp = Blueprint(
    "business_settings",
    __name__,
)


@business_settings_bp.get(
    "/businesses/<int:business_id>/settings"
)
@require_business_access
def get_business_settings_route(business_id):
    settings = get_business_settings(business_id)

    if settings is None:
        return jsonify({
            "business_id": business_id,
            "weekly_reviews_per_waiter": None,
        }), 200

    return jsonify({
        "id": settings[0],
        "business_id": settings[1],
        "weekly_reviews_per_waiter": settings[2],
        "created_at": settings[3].isoformat(),
        "updated_at": settings[4].isoformat(),
    }), 200


@business_settings_bp.put(
    "/businesses/<int:business_id>/settings"
)
@require_business_access
def update_business_settings_route(business_id):
    data = request.get_json()

    if data is None:
        return jsonify({
            "error": "request body is required"
        }), 400

    weekly_reviews_per_waiter = data.get(
        "weekly_reviews_per_waiter"
    )

    if weekly_reviews_per_waiter is None:
        return jsonify({
            "error": "weekly_reviews_per_waiter is required"
        }), 400

    if not isinstance(weekly_reviews_per_waiter, int) or isinstance(
        weekly_reviews_per_waiter, bool
    ):
        return jsonify({
            "error": (
                "weekly_reviews_per_waiter "
                "must be an integer"
            )
        }), 400

    if weekly_reviews_per_waiter < 0:
        return jsonify({
            "error": (
                "weekly_reviews_per_waiter "
                "must be greater than or equal to 0"
            )
        }), 400

    try:
        settings = set_weekly_reviews_per_waiter(
            business_id=business_id,
            weekly_reviews_per_waiter=weekly_reviews_per_waiter,
        )
    except ValueError as error:
        if str(error) == "business not found":
            return jsonify({
                "error": "business not found"
            }), 404
        raise

    return jsonify({
        "id": settings[0],
        "business_id": settings[1],
        "weekly_reviews_per_waiter": settings[2],
        "created_at": settings[3].isoformat(),
        "updated_at": settings[4].isoformat(),
    }), 200
