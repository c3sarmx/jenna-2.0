from datetime import datetime
from unittest.mock import patch

from app import create_app


def test_list_business_users_requires_access():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/api/businesses/4/users")

    assert response.status_code == 401


def test_list_business_users_allowed():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 1

    users = [
        (
            1,
            "test-auth@dukkah.local",
            True,
            "owner",
            datetime.now(),
        )
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_users.get_business_users",
        return_value=users,
    ):
        response = client.get("/api/businesses/4/users")

    assert response.status_code == 200
    assert response.get_json()[0]["role"] == "owner"


def test_admin_cannot_add_business_user():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 2

    with patch(
        "app.auth.decorators.get_user_business_role",
        return_value="admin",
    ):
        response = client.post(
            "/api/businesses/4/users",
            json={
                "email": "another@dukkah.local",
                "role": "admin",
            },
        )

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "insufficient permissions"
    }


def test_owner_can_add_business_user():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 1

    user = (
        2,
        "test-admin@dukkah.local",
        "password-hash",
        True,
        None,
    )

    business_user = (
        3,
        2,
        4,
        "admin",
        datetime.now(),
    )

    with patch(
        "app.auth.decorators.get_user_business_role",
        return_value="owner",
    ), patch(
        "app.routes.business_users.get_user_by_email",
        return_value=user,
    ), patch(
        "app.routes.business_users.assign_user_to_business",
        return_value=business_user,
    ):
        response = client.post(
            "/api/businesses/4/users",
            json={
                "email": "test-admin@dukkah.local",
                "role": "admin",
            },
        )

    assert response.status_code == 201
    assert response.get_json()["role"] == "admin"
