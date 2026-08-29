from unittest.mock import patch

from app import create_app


def test_login_success():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    user = {
        "id": 1,
        "email": "test-auth@dukkah.local",
        "active": True,
    }

    with patch(
        "app.routes.auth.authenticate_user",
        return_value=user,
    ):
        response = client.post(
            "/auth/login",
            json={
                "email": "test-auth@dukkah.local",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 200
    assert response.get_json() == user


def test_login_invalid_credentials():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with patch(
        "app.routes.auth.authenticate_user",
        return_value=None,
    ):
        response = client.post(
            "/auth/login",
            json={
                "email": "wrong@dukkah.local",
                "password": "wrong",
            },
        )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "invalid credentials"
    }
