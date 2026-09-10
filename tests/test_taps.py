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


def test_create_tap_requires_authentication():
    client = make_app().test_client()

    response = client.post(
        "/api/businesses/4/taps",
        json={
            "waiter_id": 2,
            "source": "nfc",
        },
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "authentication required"
    }


def test_create_tap_success():
    client = make_app().test_client()
    login_session(client)

    created_at = datetime.now()

    tap = (
        1,
        4,
        2,
        "nfc",
        created_at,
        None,
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.taps.create_tap",
        return_value=tap,
    ) as create_tap_mock:
        response = client.post(
            "/api/businesses/4/taps",
            json={
                "waiter_id": 2,
                "source": "nfc",
            },
        )

    assert response.status_code == 201

    body = response.get_json()

    assert body["id"] == 1
    assert body["business_id"] == 4
    assert body["waiter_id"] == 2
    assert body["source"] == "nfc"
    assert body["card_id"] is None

    create_tap_mock.assert_called_once_with(
        business_id=4,
        waiter_id=2,
        source="nfc",
    )


def test_get_taps_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/taps"
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "authentication required"
    }


def test_get_taps_success():
    client = make_app().test_client()
    login_session(client)

    taps = [
        (
            1,
            4,
            2,
            "nfc",
            datetime.now(),
            None,
        ),
        (
            2,
            4,
            2,
            "qr",
            datetime.now(),
            1,
        ),
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.taps.get_taps_by_business",
        return_value=taps,
    ):
        response = client.get(
            "/api/businesses/4/taps"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 2
    assert body[0]["source"] == "nfc"
    assert body[1]["source"] == "qr"
    assert body[1]["card_id"] == 1
