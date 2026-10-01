from datetime import datetime

from flask import Blueprint, jsonify, request

from app.auth.decorators import require_business_access
from app.services.review_evidence import (
    create_review_evidence,
    get_review_evidence_by_business,
    get_review_evidence_page,
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

    published_at = data.get("published_at")

    if published_at is not None:
        try:
            published_at = datetime.fromisoformat(published_at)
        except (TypeError, ValueError):
            return jsonify({
                "error": "invalid published_at"
            }), 400

    try:
        evidence = create_review_evidence(
            business_id=business_id,
            source=source,
            content=content,
            reviewer_name=data.get("reviewer_name"),
            rating=rating,
            external_id=data.get("external_id"),
            published_at=published_at,
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


@review_evidence_bp.get("/businesses/<int:business_id>/review-evidence/page")
@require_business_access
def get_review_evidence_page_route(business_id):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))
    except (TypeError, ValueError):
        return jsonify({
            "error": "page and per_page must be integers"
        }), 400

    status = request.args.get("status", "all")
    search = request.args.get("search")
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    try:
        result = get_review_evidence_page(
            business_id,
            page=page,
            per_page=per_page,
            status=status,
            search=search,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        return jsonify({
            "error": str(exc)
        }), 400

    return jsonify({
        "items": [
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
                "translated_content": (
                    item[11]
                    if len(item) > 11
                    else None
                ),
                "has_attribution": item[12],
            }
            for item in result["items"]
        ],
        "page": result["page"],
        "per_page": result["per_page"],
        "total": result["total"],
        "attributed_total": result["attributed_total"],
        "unattributed_total": result["unattributed_total"],
        "total_pages": result["total_pages"],
    }), 200


@review_evidence_bp.get("/businesses/<int:business_id>/review-evidence")
@require_business_access
def get_review_evidence_route(business_id):
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    evidence = get_review_evidence_by_business(
        business_id,
        date_from=date_from,
        date_to=date_to,
    )

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
            "translated_content": (
                item[11]
                if len(item) > 11
                else None
            ),
        }
        for item in evidence
    ]), 200
