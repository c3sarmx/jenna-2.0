from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.review_attributions import (
    create_review_attribution,
    get_review_attributions_by_business,
    get_review_attribution_evidence,
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

    try:
        attribution = create_review_attribution(
            business_id=business_id,
            review_evidence_id=review_evidence_id,
            waiter_id=waiter_id,
            method=method,
            confidence=confidence,
            reason=reason,
        )
    except ValueError as exc:
        error = str(exc)

        if error in (
            "review evidence not found",
            "review evidence does not belong to business",
            "waiter not found",
            "waiter does not belong to business",
        ):
            return jsonify({
                "error": error
            }), 404

        if error == "review attribution already exists":
            return jsonify({
                "error": error
            }), 409

        raise

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


@review_attributions_bp.get(
    "/businesses/<int:business_id>/review-attributions/evidence"
)
@require_business_access
def get_review_attribution_evidence_route(business_id):
    waiter_id = request.args.get("waiter_id", type=int)
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")

    evidence = get_review_attribution_evidence(
        business_id=business_id,
        waiter_id=waiter_id,
        date_from=date_from,
        date_to=date_to,
    )

    return jsonify([
        {
            "id": item[0],
            "review_evidence_id": item[1],
            "waiter_id": item[2],
            "waiter_name": item[3],
            "method": item[4],
            "confidence": item[5],
            "reason": item[6],
            "reviewer_name": item[7],
            "rating": item[8],
            "content": item[9],
            "translated_content": item[10],
            "published_at": (
                item[11].isoformat()
                if item[11]
                else None
            ),
            "source": item[12],
            "source_url": item[13],
        }
        for item in evidence
    ]), 200
