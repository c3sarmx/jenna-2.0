from datetime import date, datetime
from unittest.mock import patch

from app import create_app


def make_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def login_session(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_get_waiter_targets_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/waiter-targets"
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "authentication required"
    }


def test_get_waiter_targets_success():
    client = make_app().test_client()
    login_session(client)

    targets = [
        (
            1,
            2,
            "Mesero Test",
            50,
            date(2026, 9, 1),
            datetime(2026, 9, 1, 12, 0),
        ),
        (
            2,
            3,
            "Otro Mesero",
            40,
            date(2026, 9, 1),
            datetime(2026, 9, 1, 12, 0),
        ),
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.waiter_targets.get_waiter_targets_by_business",
        return_value=targets,
    ) as targets_mock:
        response = client.get(
            "/api/businesses/4/waiter-targets"
            "?date=2026-09-18"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body == [
        {
            "id": 1,
            "waiter_id": 2,
            "waiter_name": "Mesero Test",
            "weekly_target": 50,
            "effective_from": "2026-09-01",
            "created_at": "2026-09-01T12:00:00",
        },
        {
            "id": 2,
            "waiter_id": 3,
            "waiter_name": "Otro Mesero",
            "weekly_target": 40,
            "effective_from": "2026-09-01",
            "created_at": "2026-09-01T12:00:00",
        },
    ]

    targets_mock.assert_called_once_with(
        business_id=4,
        target_date=date(2026, 9, 18),
    )


def test_get_waiter_targets_rejects_invalid_date():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.get(
            "/api/businesses/4/waiter-targets"
            "?date=hola"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid date"
    }


def test_set_waiter_target_requires_authentication():
    client = make_app().test_client()

    response = client.post(
        "/api/businesses/4/waiter-targets",
        json={
            "waiter_id": 2,
            "weekly_target": 50,
            "effective_from": "2026-09-01",
        },
    )

    assert response.status_code == 401


def test_set_waiter_target_success():
    client = make_app().test_client()
    login_session(client)

    target = (
        1,
        2,
        50,
        date(2026, 9, 1),
        datetime(2026, 9, 1, 12, 0),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.waiter_targets.set_waiter_target",
        return_value=target,
    ) as target_mock:
        response = client.post(
            "/api/businesses/4/waiter-targets",
            json={
                "waiter_id": 2,
                "weekly_target": 50,
                "effective_from": "2026-09-01",
            },
        )

    assert response.status_code == 200

    assert response.get_json() == {
        "id": 1,
        "waiter_id": 2,
        "weekly_target": 50,
        "effective_from": "2026-09-01",
        "created_at": "2026-09-01T12:00:00",
    }

    target_mock.assert_called_once_with(
        business_id=4,
        waiter_id=2,
        weekly_target=50,
        effective_from=date(2026, 9, 1),
    )


def test_set_waiter_target_rejects_negative_value():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/waiter-targets",
            json={
                "waiter_id": 2,
                "weekly_target": -1,
                "effective_from": "2026-09-01",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "weekly_target must be greater than or equal to 0"
    }


def test_set_waiter_target_rejects_invalid_date():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.post(
            "/api/businesses/4/waiter-targets",
            json={
                "waiter_id": 2,
                "weekly_target": 50,
                "effective_from": "hola",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid effective_from date"
    }


def test_set_waiter_target_rejects_cross_business_waiter():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.waiter_targets.set_waiter_target",
        side_effect=ValueError("waiter not found"),
    ):
        response = client.post(
            "/api/businesses/4/waiter-targets",
            json={
                "waiter_id": 999,
                "weekly_target": 50,
                "effective_from": "2026-09-01",
            },
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "waiter not found"
    }
