from unittest.mock import patch

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

    response = client.get("/businesses/4/analytics")

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
        ),
    ):
        response = client.get("/businesses/4/analytics")

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
        return_value=(summary, [], []),
    ) as analytics_mock:
        response = client.get(
            "/businesses/4/analytics"
            "?from=2026-08-01&to=2026-08-29"
        )

    assert response.status_code == 200

    analytics_mock.assert_called_once_with(
        business_id=4,
        date_from="2026-08-01",
        date_to="2026-08-29",
    )
