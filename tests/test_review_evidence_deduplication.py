from unittest.mock import patch

from app import create_app


def make_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def login_session(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_create_review_evidence_returns_conflict_for_duplicate():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_evidence.create_review_evidence",
        side_effect=ValueError(
            "review evidence already exists"
        ),
    ):
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "manual_import",
                "external_id": "google-review-001",
                "reviewer_name": "Juan Pérez",
                "rating": 5,
                "content": "Excelente atención.",
            },
        )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "review evidence already exists"
    }
