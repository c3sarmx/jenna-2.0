from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.review_evidence import (
    create_review_evidence,
    get_review_evidence_by_business,
)


review_evidence_bp = Blueprint("review_evidence", __name__)


@review_evidence_bp.post("/businesses/<int:business_id>/review-evidence")
@require_business_access
def create_review_evidence_route(business_id):
    data = request.get_json()

    content = data.get("content")

    if not content:
        return jsonify({
            "error": "content is required"
        }), 400

    rating = data.get("rating")

    if rating is not None and not 1 <= rating <= 5:
        return jsonify({
            "error": "rating must be between 1 and 5"
        }), 400

    source = data.get("source")

    if source not in ("manual_import", "google_places"):
        return jsonify({
            "error": "invalid source"
        }), 400

    try:
        evidence = create_review_evidence(
            business_id=business_id,
            source=source,
            content=content,
            reviewer_name=data.get("reviewer_name"),
            rating=rating,
            external_id=data.get("external_id"),
            published_at=data.get("published_at"),
            source_url=data.get("source_url"),
        )
    except ValueError as exc:
        if str(exc) == "review evidence already exists":
            return jsonify({
                "error": str(exc)
            }), 409

        raise

    return jsonify({
        "id": evidence[0],
        "business_id": evidence[1],
        "source": evidence[2],
        "external_id": evidence[3],
        "reviewer_name": evidence[4],
        "rating": evidence[5],
        "content": evidence[6],
        "published_at": (
            evidence[7].isoformat()
            if evidence[7]
            else None
        ),
        "source_url": evidence[8],
        "fingerprint": evidence[9],
        "imported_at": evidence[10].isoformat(),
    }), 201


@review_evidence_bp.get("/businesses/<int:business_id>/review-evidence")
@require_business_access
def get_review_evidence_route(business_id):
    evidence = get_review_evidence_by_business(business_id)

    return jsonify([
        {
            "id": item[0],
            "business_id": item[1],
            "source": item[2],
            "external_id": item[3],
            "reviewer_name": item[4],
            "rating": item[5],
            "content": item[6],
            "published_at": (
                item[7].isoformat()
                if item[7]
                else None
            ),
            "source_url": item[8],
                "fingerprint": item[9],
                "imported_at": item[10].isoformat(),
        }
        for item in evidence
    ]), 200
