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


def test_create_review_attribution_requires_authentication():
    client = make_app().test_client()

    response = client.post(
        "/api/businesses/4/review-attributions",
        json={
            "review_evidence_id": 1,
            "waiter_id": 2,
            "method": "name_match",
            "confidence": "high",
        },
    )

    assert response.status_code == 401


def test_create_review_attribution_requires_review_evidence_id():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-attributions",
            json={
                "waiter_id": 2,
                "method": "name_match",
                "confidence": "high",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "review_evidence_id is required"
    }


def test_create_review_attribution_requires_waiter_id():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-attributions",
            json={
                "review_evidence_id": 1,
                "method": "name_match",
                "confidence": "high",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "waiter_id is required"
    }


def test_create_review_attribution_rejects_invalid_method():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-attributions",
            json={
                "review_evidence_id": 1,
                "waiter_id": 2,
                "method": "automatic",
                "confidence": "high",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid method"
    }


def test_create_review_attribution_rejects_invalid_confidence():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/review-attributions",
            json={
                "review_evidence_id": 1,
                "waiter_id": 2,
                "method": "name_match",
                "confidence": "certain",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid confidence"
    }


def test_create_review_attribution_success():
    client = make_app().test_client()
    login_session(client)

    attribution = (
        1,
        10,
        2,
        "name_match",
        "high",
        "La reseña menciona explícitamente el nombre César.",
        datetime(2026, 9, 10, 21, 0),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_attributions.create_review_attribution",
        return_value=attribution,
    ):
        response = client.post(
            "/api/businesses/4/review-attributions",
            json={
                "review_evidence_id": 10,
                "waiter_id": 2,
                "method": "name_match",
                "confidence": "high",
                "reason": "La reseña menciona explícitamente el nombre César.",
            },
        )

    assert response.status_code == 201

    body = response.get_json()

    assert body["id"] == 1
    assert body["review_evidence_id"] == 10
    assert body["waiter_id"] == 2
    assert body["method"] == "name_match"
    assert body["confidence"] == "high"
    assert body["reason"] == (
        "La reseña menciona explícitamente el nombre César."
    )


def test_create_review_attribution_reason_is_optional():
    client = make_app().test_client()
    login_session(client)

    attribution = (
        1,
        10,
        2,
        "manual",
        "confirmed",
        None,
        datetime(2026, 9, 10, 21, 0),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_attributions.create_review_attribution",
        return_value=attribution,
    ):
        response = client.post(
            "/api/businesses/4/review-attributions",
            json={
                "review_evidence_id": 10,
                "waiter_id": 2,
                "method": "manual",
                "confidence": "confirmed",
            },
        )

    assert response.status_code == 201
    assert response.get_json()["reason"] is None


def test_get_review_attributions_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/review-attributions"
    )

    assert response.status_code == 401


def test_get_review_attributions_success():
    client = make_app().test_client()
    login_session(client)

    attributions = [
        (
            1,
            10,
            2,
            "name_match",
            "high",
            "La reseña menciona explícitamente el nombre César.",
            datetime(2026, 9, 10, 21, 0),
        ),
        (
            2,
            11,
            3,
            "assisted",
            "confirmed",
            "Confirmado por el encargado.",
            datetime(2026, 9, 10, 21, 5),
        ),
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_attributions.get_review_attributions_by_business",
        return_value=attributions,
    ):
        response = client.get(
            "/api/businesses/4/review-attributions"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2

    assert body[0]["id"] == 1
    assert body[0]["review_evidence_id"] == 10
    assert body[0]["waiter_id"] == 2
    assert body[0]["method"] == "name_match"
    assert body[0]["confidence"] == "high"
    assert body[0]["reason"] == (
        "La reseña menciona explícitamente el nombre César."
    )

    assert body[1]["id"] == 2
    assert body[1]["review_evidence_id"] == 11
    assert body[1]["waiter_id"] == 3
    assert body[1]["method"] == "assisted"
    assert body[1]["confidence"] == "confirmed"
