from datetime import date
from unittest.mock import patch

from app import create_app


def make_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def login_session(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_create_snapshot_requires_authentication():
    client = make_app().test_client()

    response = client.post(
        "/api/businesses/4/review-snapshots",
        json={
            "snapshot_date": "2026-08-29",
            "total_reviews": 10,
        },
    )

    assert response.status_code == 401


def test_create_snapshot_requires_date():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-snapshots",
            json={
                "total_reviews": 10,
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "snapshot_date is required"
    }


def test_create_snapshot_success():
    client = make_app().test_client()
    login_session(client)

    snapshot = (
        1,
        4,
        date(2026, 8, 29),
        10,
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_snapshots.create_review_snapshot",
        return_value=snapshot,
    ):
        response = client.post(
            "/api/businesses/4/review-snapshots",
            json={
                "snapshot_date": "2026-08-29",
                "total_reviews": 10,
            },
        )

    assert response.status_code == 201

    body = response.get_json()

    assert body["id"] == 1
    assert body["business_id"] == 4
    assert body["snapshot_date"] == "2026-08-29"
    assert body["total_reviews"] == 10


def test_create_snapshot_duplicate():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_snapshots.create_review_snapshot",
        side_effect=ValueError(
            "A review snapshot already exists for this business on this date"
        ),
    ):
        response = client.post(
            "/api/businesses/4/review-snapshots",
            json={
                "snapshot_date": "2026-08-29",
                "total_reviews": 10,
            },
        )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": (
            "A review snapshot already exists for this business on this date"
        )
    }


def test_get_snapshots_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/review-snapshots"
    )

    assert response.status_code == 401


def test_get_snapshots_success():
    client = make_app().test_client()
    login_session(client)

    snapshots = [
        (
            1,
            4,
            date(2026, 8, 29),
            10,
        ),
        (
            2,
            4,
            date(2026, 8, 28),
            8,
        ),
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_snapshots.get_review_snapshots_by_business",
        return_value=snapshots,
    ):
        response = client.get(
            "/api/businesses/4/review-snapshots"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2
    assert body[0]["snapshot_date"] == "2026-08-29"
    assert body[0]["total_reviews"] == 10
    assert body[1]["snapshot_date"] == "2026-08-28"
    assert body[1]["total_reviews"] == 8
