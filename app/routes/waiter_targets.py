from datetime import date

from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.waiter_targets import (
    get_waiter_targets_by_business,
    set_waiter_target,
)


waiter_targets_bp = Blueprint("waiter_targets", __name__)


@waiter_targets_bp.get(
    "/businesses/<int:business_id>/waiter-targets"
)
@require_business_access
def get_waiter_targets_route(business_id):
    target_date = request.args.get("date")

    if target_date:
        try:
            parsed_target_date = date.fromisoformat(target_date)
        except ValueError:
            return jsonify({
                "error": "invalid date"
            }), 400
    else:
        parsed_target_date = date.today()

    targets = get_waiter_targets_by_business(
        business_id=business_id,
        target_date=parsed_target_date,
    )

    return jsonify([
        {
            "id": target[0],
            "waiter_id": target[1],
            "waiter_name": target[2],
            "weekly_target": target[3],
            "effective_from": target[4].isoformat(),
            "created_at": target[5].isoformat(),
        }
        for target in targets
    ]), 200


@waiter_targets_bp.post(
    "/businesses/<int:business_id>/waiter-targets"
)
@require_business_access
def set_waiter_target_route(business_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "request body is required"
        }), 400

    waiter_id = data.get("waiter_id")
    weekly_target = data.get("weekly_target")
    effective_from = data.get("effective_from")

    if waiter_id is None:
        return jsonify({
            "error": "waiter_id is required"
        }), 400

    if weekly_target is None:
        return jsonify({
            "error": "weekly_target is required"
        }), 400

    if not isinstance(weekly_target, int) or isinstance(
        weekly_target, bool
    ):
        return jsonify({
            "error": "weekly_target must be an integer"
        }), 400

    if weekly_target < 0:
        return jsonify({
            "error": "weekly_target must be greater than or equal to 0"
        }), 400

    if not effective_from:
        return jsonify({
            "error": "effective_from is required"
        }), 400

    try:
        parsed_effective_from = date.fromisoformat(
            effective_from
        )
    except ValueError:
        return jsonify({
            "error": "invalid effective_from date"
        }), 400

    try:
        target = set_waiter_target(
            business_id=business_id,
            waiter_id=waiter_id,
            weekly_target=weekly_target,
            effective_from=parsed_effective_from,
        )
    except ValueError as error:
        if str(error) == "waiter not found":
            return jsonify({
                "error": "waiter not found"
            }), 404
        raise

    return jsonify({
        "id": target[0],
        "waiter_id": target[1],
        "weekly_target": target[2],
        "effective_from": target[3].isoformat(),
        "created_at": target[4].isoformat(),
    }), 200
