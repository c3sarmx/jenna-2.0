from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.business_settings import (
    get_business_settings,
    set_review_sync_settings,
    set_weekly_reviews_per_waiter,
)


business_settings_bp = Blueprint(
    "business_settings",
    __name__,
)


def _serialize_review_sync(settings):
    if len(settings) < 9:
        return None

    review_sync = {
        "enabled": settings[5],
        "interval_minutes": settings[6],
        "timezone": settings[7],
        "schedule": settings[8],
    }

    if len(settings) >= 13:
        review_sync.update({
            "last_run_at": (
                settings[9].isoformat()
                if settings[9] is not None
                else None
            ),
            "last_error_at": (
                settings[10].isoformat()
                if settings[10] is not None
                else None
            ),
            "last_error": settings[11],
            "consecutive_failures": settings[12],
        })

    return review_sync


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
            "review_sync": None,
        }), 200

    return jsonify({
        "id": settings[0],
        "business_id": settings[1],
        "weekly_reviews_per_waiter": settings[2],
        "review_sync": _serialize_review_sync(settings),
        "created_at": settings[3].isoformat(),
        "updated_at": settings[4].isoformat(),
    }), 200


@business_settings_bp.put(
    "/businesses/<int:business_id>/settings"
)
@require_business_access
def update_business_settings_route(business_id):
    data = request.get_json(silent=True)

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
        "review_sync": _serialize_review_sync(settings),
        "created_at": settings[3].isoformat(),
        "updated_at": settings[4].isoformat(),
    }), 200


@business_settings_bp.put(
    "/businesses/<int:business_id>/settings/review-sync"
)
@require_business_access
def update_review_sync_settings_route(business_id):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "request body is required"
        }), 400

    required_fields = (
        "enabled",
        "interval_minutes",
        "timezone",
        "schedule",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": (
                "missing required fields: "
                + ", ".join(missing_fields)
            )
        }), 400

    try:
        settings = set_review_sync_settings(
            business_id=business_id,
            enabled=data["enabled"],
            interval_minutes=data["interval_minutes"],
            timezone=data["timezone"],
            schedule=data["schedule"],
        )
    except ValueError as error:
        if str(error) == "business not found":
            return jsonify({
                "error": "business not found"
            }), 404

        return jsonify({
            "error": str(error)
        }), 400

    return jsonify({
        "id": settings[0],
        "business_id": settings[1],
        "weekly_reviews_per_waiter": settings[2],
        "review_sync": _serialize_review_sync(settings),
        "created_at": settings[3].isoformat(),
        "updated_at": settings[4].isoformat(),
    }), 200
