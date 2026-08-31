from unittest.mock import patch

from app import create_app


def test_business_access_requires_authentication():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get("/businesses/4/analytics")

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "authentication required"
    }


def test_business_access_denied_for_other_business():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 1

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=False,
    ):
        response = client.get("/businesses/1/analytics")

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "business access denied"
    }


def test_business_access_allowed():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 1

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_analytics",
        return_value=(
            (0, 0, 0, 0, 0, 0),
            [],
            [],
            [],
        ),
    ):
        response = client.get("/businesses/4/analytics")

    assert response.status_code == 200


def test_business_access_denied_for_unassigned_business():
    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 2

    routes = [
        "/businesses/5/analytics",
        "/businesses/5/cards",
        "/businesses/5/waiters",
    ]

    for route in routes:
        response = client.get(route)

        assert response.status_code == 403
        assert response.get_json() == {
            "error": "business access denied"
        }
