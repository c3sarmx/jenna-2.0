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


def test_get_business_settings_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/settings"
    )

    assert response.status_code == 401


def test_get_business_settings_without_existing_settings():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_settings.get_business_settings",
        return_value=None,
    ):
        response = client.get(
            "/api/businesses/4/settings"
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "business_id": 4,
        "weekly_reviews_per_waiter": None,
        "review_sync": None,
    }


def test_get_business_settings_success():
    client = make_app().test_client()
    login_session(client)

    settings = (
        1,
        4,
        150,
        datetime(2026, 9, 18, 12, 0),
        datetime(2026, 9, 18, 12, 0),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_settings.get_business_settings",
        return_value=settings,
    ):
        response = client.get(
            "/api/businesses/4/settings"
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": 1,
        "business_id": 4,
        "weekly_reviews_per_waiter": 150,
        "review_sync": None,
        "created_at": "2026-09-18T12:00:00",
        "updated_at": "2026-09-18T12:00:00",
    }


def test_update_business_settings_requires_authentication():
    client = make_app().test_client()

    response = client.put(
        "/api/businesses/4/settings",
        json={
            "weekly_reviews_per_waiter": 150,
        },
    )

    assert response.status_code == 401


def test_update_business_settings_success():
    client = make_app().test_client()
    login_session(client)

    settings = (
        1,
        4,
        150,
        datetime(2026, 9, 18, 12, 0),
        datetime(2026, 9, 18, 12, 0),
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_settings.set_weekly_reviews_per_waiter",
        return_value=settings,
    ) as settings_mock:
        response = client.put(
            "/api/businesses/4/settings",
            json={
                "weekly_reviews_per_waiter": 150,
            },
        )

    assert response.status_code == 200

    assert response.get_json() == {
        "id": 1,
        "business_id": 4,
        "weekly_reviews_per_waiter": 150,
        "review_sync": None,
        "created_at": "2026-09-18T12:00:00",
        "updated_at": "2026-09-18T12:00:00",
    }

    settings_mock.assert_called_once_with(
        business_id=4,
        weekly_reviews_per_waiter=150,
    )


def test_update_business_settings_rejects_missing_target():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.put(
            "/api/businesses/4/settings",
            json={},
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "weekly_reviews_per_waiter is required"
    }


def test_update_business_settings_rejects_negative_target():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.put(
            "/api/businesses/4/settings",
            json={
                "weekly_reviews_per_waiter": -1,
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": (
            "weekly_reviews_per_waiter "
            "must be greater than or equal to 0"
        )
    }


def test_update_business_settings_rejects_non_integer_target():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.put(
            "/api/businesses/4/settings",
            json={
                "weekly_reviews_per_waiter": "150",
            },
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": (
            "weekly_reviews_per_waiter "
            "must be an integer"
        )
    }


def test_update_business_settings_returns_404_for_missing_business():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_settings.set_weekly_reviews_per_waiter",
        side_effect=ValueError("business not found"),
    ):
        response = client.put(
            "/api/businesses/999/settings",
            json={
                "weekly_reviews_per_waiter": 150,
            },
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "business not found"
    }


def test_get_business_settings_includes_review_sync():
    client = make_app().test_client()
    login_session(client)

    settings = (
        1,
        4,
        150,
        datetime(2026, 9, 18, 12, 0),
        datetime(2026, 9, 18, 12, 0),
        True,
        5,
        "America/Mexico_City",
        {
            "mon": {"start": "08:00", "end": "22:00"},
            "fri": {"start": "08:00", "end": "23:00"},
        },
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_settings.get_business_settings",
        return_value=settings,
    ):
        response = client.get(
            "/api/businesses/4/settings"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body["weekly_reviews_per_waiter"] == 150
    assert body["review_sync"] == {
        "enabled": True,
        "interval_minutes": 5,
        "timezone": "America/Mexico_City",
        "schedule": {
            "mon": {"start": "08:00", "end": "22:00"},
            "fri": {"start": "08:00", "end": "23:00"},
        },
    }


def test_update_review_sync_settings_success():
    client = make_app().test_client()
    login_session(client)

    settings = (
        1,
        4,
        150,
        datetime(2026, 9, 18, 12, 0),
        datetime(2026, 9, 18, 12, 0),
        True,
        5,
        "America/Mexico_City",
        {
            "mon": {"start": "08:00", "end": "22:00"},
        },
    )

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_settings.set_review_sync_settings",
        return_value=settings,
    ) as settings_mock:
        response = client.put(
            "/api/businesses/4/settings/review-sync",
            json={
                "enabled": True,
                "interval_minutes": 5,
                "timezone": "America/Mexico_City",
                "schedule": {
                    "mon": {
                        "start": "08:00",
                        "end": "22:00",
                    },
                },
            },
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body["review_sync"] == {
        "enabled": True,
        "interval_minutes": 5,
        "timezone": "America/Mexico_City",
        "schedule": {
            "mon": {
                "start": "08:00",
                "end": "22:00",
            },
        },
    }

    settings_mock.assert_called_once_with(
        business_id=4,
        enabled=True,
        interval_minutes=5,
        timezone="America/Mexico_City",
        schedule={
            "mon": {
                "start": "08:00",
                "end": "22:00",
            },
        },
    )


def test_update_review_sync_settings_requires_body():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.put(
            "/api/businesses/4/settings/review-sync",
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "request body is required"
    }


def test_update_review_sync_settings_returns_404_for_missing_business():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.business_settings.set_review_sync_settings",
        side_effect=ValueError("business not found"),
    ):
        response = client.put(
            "/api/businesses/999/settings/review-sync",
            json={
                "enabled": True,
                "interval_minutes": 5,
                "timezone": "America/Mexico_City",
                "schedule": {},
            },
        )

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "business not found"
    }
