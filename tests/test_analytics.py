from datetime import date
from unittest.mock import call, patch

from app import create_app


def make_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def login_session(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_analytics_requires_authentication():
    client = make_app().test_client()

    response = client.get("/api/businesses/4/analytics")

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "authentication required"
    }


def test_analytics_success():
    client = make_app().test_client()
    login_session(client)

    summary = (
        25,  # total_taps
        3,   # total_waiters
        120, # latest_review_count
        10,  # nfc
        12,  # qr
        3,   # web
    )

    taps_by_waiter = [
        (2, "Mesero Test", 15),
        (3, "Otro Mesero", 10),
    ]

    taps_by_card = [
        (1, "card-public-1", 2, "Mesero Test", 15),
        (2, "card-public-2", 3, "Otro Mesero", 10),
    ]

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_analytics",
        return_value=(
            summary,
            taps_by_waiter,
            taps_by_card,
            [
                (date(2026, 8, 27), 3),
                (date(2026, 8, 28), 5),
                (date(2026, 8, 29), 7),
            ],
        ),
    ), patch(
        "app.routes.analytics.get_review_analytics",
        return_value={
            "total_review_evidence": 0,
            "attributed_reviews": 0,
            "unattributed_reviews": 0,
            "reviews_by_waiter": [],
        },
    ):
        response = client.get("/api/businesses/4/analytics")

    assert response.status_code == 200

    body = response.get_json()

    assert body["business_id"] == 4
    assert body["total_taps"] == 25
    assert body["total_waiters"] == 3
    assert body["latest_review_count"] == 120

    assert body["taps_by_source"] == {
        "nfc": 10,
        "qr": 12,
        "web": 3,
    }

    assert body["daily_taps"] == [
        {
            "date": "2026-08-27",
            "total_taps": 3,
        },
        {
            "date": "2026-08-28",
            "total_taps": 5,
        },
        {
            "date": "2026-08-29",
            "total_taps": 7,
        },
    ]

    assert body["taps_by_waiter"][0] == {
        "waiter_id": 2,
        "waiter_name": "Mesero Test",
        "total_taps": 15,
    }

    assert body["taps_by_card"][0] == {
        "card_id": 1,
        "public_id": "card-public-1",
        "waiter_id": 2,
        "waiter_name": "Mesero Test",
        "total_taps": 15,
    }


def test_analytics_passes_date_filters():
    client = make_app().test_client()
    login_session(client)

    summary = (10, 2, 50, 4, 5, 1)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_analytics",
        return_value=(summary, [], [], []),
    ) as analytics_mock, patch(
        "app.routes.analytics.get_review_analytics",
        return_value={
            "total_review_evidence": 0,
            "attributed_reviews": 0,
            "unattributed_reviews": 0,
            "reviews_by_waiter": [],
        },
    ):
        response = client.get(
            "/api/businesses/4/analytics"
            "?date_from=2026-08-01&date_to=2026-08-29"
        )

    assert response.status_code == 200

    assert analytics_mock.call_args_list == [
        call(
            business_id=4,
            date_from="2026-08-01",
            date_to="2026-08-29",
        ),
        call(
            business_id=4,
            date_from="2026-07-03",
            date_to="2026-07-31",
        ),
    ]


def test_analytics_includes_review_analytics():
    client = make_app().test_client()
    login_session(client)

    summary = (
        25,
        3,
        120,
        10,
        12,
        3,
    )

    review_analytics = {
        "total_review_evidence": 3,
        "attributed_reviews": 2,
        "unattributed_reviews": 1,
        "reviews_by_waiter": [
            {
                "waiter_id": 2,
                "waiter_name": "Mesero Test",
                "total_reviews": 2,
            },
            {
                "waiter_id": 3,
                "waiter_name": "Otro Mesero",
                "total_reviews": 1,
            },
        ],
    }

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_analytics",
        return_value=(
            summary,
            [],
            [],
            [],
        ),
    ), patch(
        "app.routes.analytics.get_review_analytics",
        return_value=review_analytics,
    ) as review_analytics_mock:
        response = client.get("/api/businesses/4/analytics")

    assert response.status_code == 200

    body = response.get_json()

    assert body["review_analytics"] == review_analytics

    review_analytics_mock.assert_called_once_with(
        business_id=4,
        date_from=None,
        date_to=None,
    )


def test_analytics_rejects_invalid_from_format():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.get(
            "/api/businesses/4/analytics?date_from=hola"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid from date"
    }


def test_analytics_rejects_invalid_to_date():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ):
        response = client.get(
            "/api/businesses/4/analytics?date_to=2026-99-99"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid to date"
    }


def test_analytics_rejects_reversed_date_range():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_analytics",
    ) as analytics_mock, patch(
        "app.routes.analytics.get_review_analytics",
    ) as review_analytics_mock:
        response = client.get(
            "/api/businesses/4/analytics"
            "?date_from=2026-08-31&date_to=2026-08-01"
        )

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "invalid date range"
    }

    analytics_mock.assert_not_called()
    review_analytics_mock.assert_not_called()


def test_analytics_accepts_valid_date_range():
    client = make_app().test_client()
    login_session(client)

    summary = (10, 2, 50, 4, 5, 1)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_analytics",
        return_value=(summary, [], [], []),
    ) as analytics_mock, patch(
        "app.routes.analytics.get_review_analytics",
        return_value={
            "total_review_evidence": 0,
            "attributed_reviews": 0,
            "unattributed_reviews": 0,
            "reviews_by_waiter": [],
        },
    ) as review_analytics_mock:
        response = client.get(
            "/api/businesses/4/analytics"
            "?date_from=2026-08-01&date_to=2026-08-29"
        )

    assert response.status_code == 200

    assert analytics_mock.call_args_list == [
        call(
            business_id=4,
            date_from="2026-08-01",
            date_to="2026-08-29",
        ),
        call(
            business_id=4,
            date_from="2026-07-03",
            date_to="2026-07-31",
        ),
    ]

    assert review_analytics_mock.call_args_list == [
        call(
            business_id=4,
            date_from="2026-08-01",
            date_to="2026-08-29",
        ),
        call(
            business_id=4,
            date_from="2026-07-03",
            date_to="2026-07-31",
        ),
    ]


def test_analytics_includes_growth_for_selected_period():
    client = make_app().test_client()
    login_session(client)

    current_summary = (30, 3, 120, 10, 15, 5)
    previous_summary = (20, 3, 110, 7, 10, 3)

    current_reviews = {
        "total_review_evidence": 6,
        "attributed_reviews": 4,
        "unattributed_reviews": 2,
        "reviews_by_waiter": [],
    }

    previous_reviews = {
        "total_review_evidence": 4,
        "attributed_reviews": 3,
        "unattributed_reviews": 1,
        "reviews_by_waiter": [],
    }

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.analytics.get_business_analytics",
        side_effect=[
            (current_summary, [], [], []),
            (previous_summary, [], [], []),
        ],
    ) as analytics_mock, patch(
        "app.routes.analytics.get_review_analytics",
        side_effect=[
            current_reviews,
            previous_reviews,
        ],
    ) as review_analytics_mock:
        response = client.get(
            "/api/businesses/4/analytics"
            "?date_from=2026-08-01&date_to=2026-08-30"
        )

    assert response.status_code == 200

    body = response.get_json()

    assert body["growth"] == {
        "taps": 50.0,
        "reviews": 50.0,
    }

    assert analytics_mock.call_args_list[1].kwargs == {
        "business_id": 4,
        "date_from": "2026-07-02",
        "date_to": "2026-07-31",
    }

    assert review_analytics_mock.call_args_list[1].kwargs == {
        "business_id": 4,
        "date_from": "2026-07-02",
        "date_to": "2026-07-31",
    }
