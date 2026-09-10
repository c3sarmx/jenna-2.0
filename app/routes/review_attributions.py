from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.review_attributions import (
    create_review_attribution,
    get_review_attributions_by_business,
)


review_attributions_bp = Blueprint(
    "review_attributions",
    __name__,
)


@review_attributions_bp.post(
    "/businesses/<int:business_id>/review-attributions"
)
@require_business_access
def create_review_attribution_route(business_id):
    data = request.get_json()

    review_evidence_id = data.get("review_evidence_id")
    waiter_id = data.get("waiter_id")
    method = data.get("method")
    confidence = data.get("confidence")
    reason = data.get("reason")

    if review_evidence_id is None:
        return jsonify({
            "error": "review_evidence_id is required"
        }), 400

    if waiter_id is None:
        return jsonify({
            "error": "waiter_id is required"
        }), 400

    if method not in ("manual", "name_match", "assisted"):
        return jsonify({
            "error": "invalid method"
        }), 400

    if confidence not in (
        "confirmed",
        "high",
        "medium",
        "low",
    ):
        return jsonify({
            "error": "invalid confidence"
        }), 400

    attribution = create_review_attribution(
        business_id=business_id,
        review_evidence_id=review_evidence_id,
        waiter_id=waiter_id,
        method=method,
        confidence=confidence,
        reason=reason,
    )

    return jsonify({
        "id": attribution[0],
        "review_evidence_id": attribution[1],
        "waiter_id": attribution[2],
        "method": attribution[3],
        "confidence": attribution[4],
        "reason": attribution[5],
        "created_at": attribution[6].isoformat(),
    }), 201


@review_attributions_bp.get(
    "/businesses/<int:business_id>/review-attributions"
)
@require_business_access
def get_review_attributions_route(business_id):
    attributions = get_review_attributions_by_business(
        business_id
    )

    return jsonify([
        {
            "id": attribution[0],
            "review_evidence_id": attribution[1],
            "waiter_id": attribution[2],
            "method": attribution[3],
            "confidence": attribution[4],
            "reason": attribution[5],
            "created_at": attribution[6].isoformat(),
        }
        for attribution in attributions
    ]), 200
