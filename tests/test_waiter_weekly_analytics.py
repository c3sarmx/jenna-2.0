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


def test_waiter_weekly_analytics_requires_authentication():
    client = make_app().test_client()

    response = client.get(
        "/api/businesses/4/analytics/waiters/weekly"
        "?week_start=2026-09-14"
    )

    assert response.status_code == 401


def test_waiter_weekly_analytics_success():
    client = make_app().test_client()
    login_session(client)

    analytics = [
        {
            "waiter_id": 2,
            "waiter_name": "Mesero Test",
            "week_start": date(2026, 9, 14),
            "week_end": date(2026, 9, 20),
            "total_taps": 35,
            "weekly_target": 50,
            "reach_percentage": 70.0,
        },
        {
            "waiter_id": 3,
            "waiter_name": "Otro Mesero",
            "week_start": date(2026, 9, 14),
            "week_end": date(2026, 9, 20),
            "total_taps": 34,
            "weekly_target": 40,
            "reach_percentage": 85.0,
        },
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_waiter_weekly_analytics",
        return_value=analytics,
    ) as analytics_mock:
        response = client.get(
            "/api/businesses/4/analytics/waiters/weekly"
            "?week_start=2026-09-14"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body == [
        {
            "waiter_id": 2,
            "waiter_name": "Mesero Test",
            "week_start": "2026-09-14",
            "week_end": "2026-09-20",
            "total_taps": 35,
            "weekly_target": 50,
            "reach_percentage": 70.0,
        },
        {
            "waiter_id": 3,
            "waiter_name": "Otro Mesero",
            "week_start": "2026-09-14",
            "week_end": "2026-09-20",
            "total_taps": 34,
            "weekly_target": 40,
            "reach_percentage": 85.0,
        },
    ]

    analytics_mock.assert_called_once_with(
        business_id=4,
        week_start=date(2026, 9, 14),
    )


def test_waiter_weekly_analytics_requires_week_start():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.get(
            "/api/businesses/4/analytics/waiters/weekly"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "week_start is required"
    }


def test_waiter_weekly_analytics_rejects_invalid_week_start():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.get(
            "/api/businesses/4/analytics/waiters/weekly"
            "?week_start=hola"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid week_start date"
    }
