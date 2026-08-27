from flask import Blueprint, jsonify, request

from app.services.review_snapshots import (
    create_review_snapshot,
    get_review_snapshots_by_business,
)


review_snapshots_bp = Blueprint("review_snapshots", __name__)


@review_snapshots_bp.post("/businesses/<int:business_id>/review-snapshots")
def create_review_snapshot_route(business_id):
    data = request.get_json()

    snapshot_date = data.get("snapshot_date")
    total_reviews = data.get("total_reviews", 0)

    if not snapshot_date:
        return jsonify({
            "error": "snapshot_date is required"
        }), 400

    try:
        snapshot = create_review_snapshot(
            business_id=business_id,
            snapshot_date=snapshot_date,
            total_reviews=total_reviews,
        )
    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 409

    return jsonify({
        "id": snapshot[0],
        "business_id": snapshot[1],
        "snapshot_date": snapshot[2].isoformat(),
        "total_reviews": snapshot[3],
    }), 201


@review_snapshots_bp.get("/businesses/<int:business_id>/review-snapshots")
def get_review_snapshots_route(business_id):
    snapshots = get_review_snapshots_by_business(business_id)

    return jsonify([
        {
            "id": snapshot[0],
            "business_id": snapshot[1],
            "snapshot_date": snapshot[2].isoformat(),
            "total_reviews": snapshot[3],
        }
        for snapshot in snapshots
    ]), 200
