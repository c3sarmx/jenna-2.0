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


def test_update_waiter_status_requires_authentication():
    client = make_app().test_client()

    response = client.patch(
        "/api/businesses/4/waiters/2",
        json={"active": False},
    )

    assert response.status_code == 401


def test_update_waiter_status_requires_active():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.patch(
            "/api/businesses/4/waiters/2",
            json={},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "active is required"
    }


def test_update_waiter_status_requires_boolean():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.patch(
            "/api/businesses/4/waiters/2",
            json={"active": "false"},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "active must be boolean"
    }


def test_update_waiter_status_success():
    client = make_app().test_client()
    login_session(client)

    waiter = (
        2,
        4,
        "Mesero Test",
        False,
        datetime.now(),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.waiters.update_waiter_status",
        return_value=waiter,
    ):
        response = client.patch(
            "/api/businesses/4/waiters/2",
            json={"active": False},
        )

    assert response.status_code == 200
    assert response.get_json()["active"] is False


def test_update_waiter_status_not_found():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.waiters.update_waiter_status",
        return_value=None,
    ):
        response = client.patch(
            "/api/businesses/4/waiters/999",
            json={"active": False},
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "waiter not found"
    }
