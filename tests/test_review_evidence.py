from datetime import datetime
from unittest.mock import patch

from app import create_app


def make_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def login_session(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_create_review_evidence_requires_authentication():
    client = make_app().test_client()

    response = client.post(
        "/api/businesses/4/review-evidence",
        json={
            "source": "manual_import",
            "content": "Excelente atención de César.",
        },
    )

    assert response.status_code == 401


def test_create_review_evidence_requires_content():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "manual_import",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "content is required"
    }


def test_create_review_evidence_success():
    client = make_app().test_client()
    login_session(client)

    evidence = (
        1,
        4,
        "manual_import",
        None,
        "Juan Pérez",
        5,
        "Excelente atención de César.",
        datetime(2026, 9, 10, 20, 30),
        None,
        "a" * 64,
        datetime(2026, 9, 10, 21, 0),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_evidence.create_review_evidence",
        return_value=evidence,
    ):
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "manual_import",
                "reviewer_name": "Juan Pérez",
                "rating": 5,
                "content": "Excelente atención de César.",
            },
        )

    assert response.status_code == 201

    body = response.get_json()

    assert body["id"] == 1
    assert body["business_id"] == 4
    assert body["source"] == "manual_import"
    assert body["reviewer_name"] == "Juan Pérez"
    assert body["rating"] == 5
    assert body["content"] == "Excelente atención de César."
    assert body["fingerprint"] == "a" * 64
    assert body["imported_at"] == "2026-09-10T21:00:00"


def test_create_review_evidence_rejects_invalid_rating():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "manual_import",
                "rating": 6,
                "content": "Excelente atención.",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "rating must be between 1 and 5"
    }


def test_create_review_evidence_rejects_invalid_source():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "unknown",
                "content": "Excelente atención.",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid source"
    }

def test_get_review_evidence_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/review-evidence"
    )

    assert response.status_code == 401


def test_get_review_evidence_success():
    client = make_app().test_client()
    login_session(client)

    evidence = [
        (
            1,
            4,
            "manual_import",
            "review-001",
            "Juan Pérez",
            5,
            "Excelente atención de César.",
            datetime(2026, 9, 10, 20, 30),
            "https://example.com/review-001",
            "b" * 64,
            datetime(2026, 9, 10, 21, 0),
        ),
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_evidence.get_review_evidence_by_business",
        return_value=evidence,
    ):
        response = client.get(
            "/api/businesses/4/review-evidence"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == 1
    assert body[0]["business_id"] == 4
    assert body[0]["source"] == "manual_import"
    assert body[0]["external_id"] == "review-001"
    assert body[0]["reviewer_name"] == "Juan Pérez"
    assert body[0]["rating"] == 5
    assert body[0]["content"] == "Excelente atención de César."
    assert body[0]["fingerprint"] == "b" * 64
    assert body[0]["imported_at"] == "2026-09-10T21:00:00"


def test_create_review_evidence_parses_published_at():
    client = make_app().test_client()
    login_session(client)

    evidence = (
        1,
        4,
        "manual_import",
        None,
        "Juan Pérez",
        5,
        "Excelente atención.",
        datetime(2026, 9, 10, 20, 30),
        None,
        "a" * 64,
        datetime(2026, 9, 10, 21, 0),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_evidence.create_review_evidence",
        return_value=evidence,
    ) as create_mock:
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "manual_import",
                "reviewer_name": "Juan Pérez",
                "rating": 5,
                "content": "Excelente atención.",
                "published_at": "2026-09-10T20:30:00-06:00",
            },
        )

    assert response.status_code == 201

    create_mock.assert_called_once()

    call = create_mock.call_args.kwargs

    assert call["published_at"] == datetime.fromisoformat(
        "2026-09-10T20:30:00-06:00"
    )


def test_create_review_evidence_rejects_invalid_published_at():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "manual_import",
                "content": "Excelente atención.",
                "published_at": "not-a-date",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid published_at"
    }


def test_get_review_evidence_page_success():
    client = make_app().test_client()
    login_session(client)

    result = {
        "items": [
            (
                1,
                4,
                "manual_import",
                "review-001",
                "Juan Pérez",
                5,
                "Excelente atención de César.",
                datetime(2026, 9, 10, 20, 30),
                "https://example.com/review-001",
                "b" * 64,
                datetime(2026, 9, 10, 21, 0),
                "Excellent service.",
                True,
            ),
        ],
        "page": 1,
        "per_page": 20,
        "total": 41,
        "attributed_total": 28,
        "unattributed_total": 13,
        "total_pages": 3,
    }

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_evidence.get_review_evidence_page",
        return_value=result,
    ):
        response = client.get(
            "/api/businesses/4/review-evidence/page"
            "?page=1&per_page=20&status=all"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body["page"] == 1
    assert body["per_page"] == 20
    assert body["total"] == 41
    assert body["attributed_total"] == 28
    assert body["unattributed_total"] == 13
    assert body["total_pages"] == 3

    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == 1
    assert body["items"][0]["reviewer_name"] == "Juan Pérez"
    assert body["items"][0]["translated_content"] == "Excellent service."
    assert body["items"][0]["has_attribution"] is True
