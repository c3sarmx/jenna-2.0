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


def test_create_card_requires_authentication():
    client = make_app().test_client()

    response = client.post(
        "/api/businesses/4/cards",
        json={"waiter_id": 2},
    )

    assert response.status_code == 401


def test_create_card_requires_waiter_id():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/cards",
            json={},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "waiter_id is required"
    }


def test_create_card_rejects_waiter_from_other_business():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.cards.create_card",
        side_effect=ValueError(
            "waiter does not belong to this business"
        ),
    ):
        response = client.post(
            "/api/businesses/4/cards",
            json={"waiter_id": 99},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "waiter does not belong to this business"
    }


def test_create_card_success():
    client = make_app().test_client()
    login_session(client)

    created_at = datetime.now()

    card = (
        10,
        4,
        2,
        "public-card-123",
        True,
        created_at,
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.cards.create_card",
        return_value=card,
    ):
        response = client.post(
            "/api/businesses/4/cards",
            json={"waiter_id": 2},
        )

    assert response.status_code == 201

    body = response.get_json()

    assert body["id"] == 10
    assert body["business_id"] == 4
    assert body["waiter_id"] == 2
    assert body["public_id"] == "public-card-123"
    assert body["active"] is True


def test_resolve_card_not_found():
    client = make_app().test_client()

    with patch(
        "app.routes.cards.get_card_by_public_id",
        return_value=None,
    ):
        response = client.get("/api/r/not-found")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "card not found"
    }


def test_resolve_inactive_card():
    client = make_app().test_client()

    card = (
        10,
        4,
        "Business",
        "https://example.com/review",
        2,
        "Mesero Test",
        "public-card-123",
        False,
        datetime.now(),
    )

    with patch(
        "app.routes.cards.get_card_by_public_id",
        return_value=card,
    ):
        response = client.get("/api/r/public-card-123")

    assert response.status_code == 410
    assert response.get_json() == {
        "error": "card inactive"
    }


def test_resolve_card_invalid_source():
    client = make_app().test_client()

    card = (
        10,
        4,
        "Business",
        "https://example.com/review",
        2,
        "Mesero Test",
        "public-card-123",
        True,
        datetime.now(),
        True,
    )

    with patch(
        "app.routes.cards.get_card_by_public_id",
        return_value=card,
    ):
        response = client.get(
            "/api/r/public-card-123?source=invalid"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid source"
    }


def test_resolve_card_success():
    client = make_app().test_client()

    card = (
        10,
        4,
        "Business",
        "https://example.com/review",
        2,
        "Mesero Test",
        "public-card-123",
        True,
        datetime.now(),
        True,
    )

    with patch(
        "app.routes.cards.get_card_by_public_id",
        return_value=card,
    ), patch(
        "app.routes.cards.create_tap",
        return_value=(1, 4, 2, "qr", datetime.now(), 10),
    ) as create_tap_mock:
        response = client.get(
            "/api/r/public-card-123?source=qr"
        )

    assert response.status_code == 302
    assert response.headers["Location"] == (
        "https://example.com/review"
    )

    create_tap_mock.assert_called_once_with(
        business_id=4,
        waiter_id=2,
        source="qr",
        card_id=10,
    )


def test_update_card_status_success():
    client = make_app().test_client()
    login_session(client)

    card = (
        10,
        4,
        2,
        "public-card-123",
        False,
        datetime.now(),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.cards.update_card_status",
        return_value=card,
    ):
        response = client.patch(
            "/api/businesses/4/cards/10",
            json={"active": False},
        )

    assert response.status_code == 200
    assert response.get_json()["active"] is False


def test_update_card_status_not_found():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.cards.update_card_status",
        return_value=None,
    ):
        response = client.patch(
            "/api/businesses/4/cards/999",
            json={"active": False},
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "card not found"
    }


def test_resolve_card_inactive_waiter():
    client = make_app().test_client()

    card = (
        10,
        4,
        "Business",
        "https://example.com/review",
        2,
        "Mesero Test",
        "public-card-123",
        True,
        datetime.now(),
        False,
    )

    with patch(
        "app.routes.cards.get_card_by_public_id",
        return_value=card,
    ), patch(
        "app.routes.cards.create_tap",
    ) as create_tap_mock:
        response = client.get(
            "/api/r/public-card-123?source=nfc"
        )

    assert response.status_code == 410
    assert response.get_json() == {
        "error": "card inactive"
    }

    create_tap_mock.assert_not_called()
