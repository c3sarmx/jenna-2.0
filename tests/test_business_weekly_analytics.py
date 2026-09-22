from datetime import date
from unittest.mock import patch

from app import create_app


def make_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def login_session(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_business_weekly_analytics_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/analytics/weekly"
        "?week_start=2026-09-14"
    )

    assert response.status_code == 401


def test_business_weekly_analytics_success():
    client = make_app().test_client()
    login_session(client)

    analytics = {
        "week_start": date(2026, 9, 14),
        "week_end": date(2026, 9, 20),
        "weekly_reviews_per_waiter": 12,
        "waiters": [
            {
                "waiter_id": 1,
                "waiter_name": "César",
                "daily": {
                    "monday": 2,
                    "tuesday": 1,
                    "wednesday": 0,
                    "thursday": 2,
                    "friday": 3,
                    "saturday": 1,
                    "sunday": 1,
                },
                "total": 10,
                "reach_percentage": 83.33,
            },
            {
                "waiter_id": 2,
                "waiter_name": "Julio",
                "daily": {
                    "monday": 2,
                    "tuesday": 2,
                    "wednesday": 2,
                    "thursday": 2,
                    "friday": 2,
                    "saturday": 1,
                    "sunday": 1,
                },
                "total": 12,
                "reach_percentage": 100.0,
            },
        ],
    }

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_weekly_analytics",
        return_value=analytics,
    ) as analytics_mock:
        response = client.get(
            "/api/businesses/4/analytics/weekly"
            "?week_start=2026-09-14"
        )

    assert response.status_code == 200

    assert response.get_json() == {
        "week_start": "2026-09-14",
        "week_end": "2026-09-20",
        "weekly_reviews_per_waiter": 12,
        "waiters": [
            {
                "waiter_id": 1,
                "waiter_name": "César",
                "daily": {
                    "monday": 2,
                    "tuesday": 1,
                    "wednesday": 0,
                    "thursday": 2,
                    "friday": 3,
                    "saturday": 1,
                    "sunday": 1,
                },
                "total": 10,
                "reach_percentage": 83.33,
            },
            {
                "waiter_id": 2,
                "waiter_name": "Julio",
                "daily": {
                    "monday": 2,
                    "tuesday": 2,
                    "wednesday": 2,
                    "thursday": 2,
                    "friday": 2,
                    "saturday": 1,
                    "sunday": 1,
                },
                "total": 12,
                "reach_percentage": 100.0,
            },
        ],
    }

    analytics_mock.assert_called_once_with(
        business_id=4,
        week_start=date(2026, 9, 14),
    )


def test_business_weekly_analytics_requires_week_start():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.get(
            "/api/businesses/4/analytics/weekly"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "week_start is required"
    }


def test_business_weekly_analytics_rejects_invalid_week_start():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.get(
            "/api/businesses/4/analytics/weekly"
            "?week_start=hola"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid week_start date"
    }


def test_business_weekly_analytics_allows_missing_target():
    client = make_app().test_client()
    login_session(client)

    analytics = {
        "week_start": date(2026, 9, 14),
        "week_end": date(2026, 9, 20),
        "weekly_reviews_per_waiter": None,
        "waiters": [
            {
                "waiter_id": 1,
                "waiter_name": "César",
                "daily": {
                    "monday": 0,
                    "tuesday": 0,
                    "wednesday": 0,
                    "thursday": 0,
                    "friday": 0,
                    "saturday": 0,
                    "sunday": 0,
                },
                "total": 0,
                "reach_percentage": None,
            }
        ],
    }

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_weekly_analytics",
        return_value=analytics,
    ):
        response = client.get(
            "/api/businesses/4/analytics/weekly"
            "?week_start=2026-09-14"
        )

    assert response.status_code == 200
    assert response.get_json() == {
        "week_start": "2026-09-14",
        "week_end": "2026-09-20",
        "weekly_reviews_per_waiter": None,
        "waiters": [
            {
                "waiter_id": 1,
                "waiter_name": "César",
                "daily": {
                    "monday": 0,
                    "tuesday": 0,
                    "wednesday": 0,
                    "thursday": 0,
                    "friday": 0,
                    "saturday": 0,
                    "sunday": 0,
                },
                "total": 0,
                "reach_percentage": None,
            }
        ],
    }
