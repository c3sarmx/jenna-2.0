from app.database.connection import get_connection
from app.services.business_settings import (
    get_business_settings,
    set_weekly_reviews_per_waiter,
)
from app.services.businesses import create_business


def test_business_settings_can_be_created_and_updated(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Settings Café",
        google_review_url="https://example.com/review",
    )

    settings = set_weekly_reviews_per_waiter(
        business_id=business[0],
        weekly_reviews_per_waiter=150,
    )

    assert settings[1] == business[0]
    assert settings[2] == 150

    stored = get_business_settings(business[0])

    assert stored[1] == business[0]
    assert stored[2] == 150

    updated = set_weekly_reviews_per_waiter(
        business_id=business[0],
        weekly_reviews_per_waiter=200,
    )

    assert updated[1] == business[0]
    assert updated[2] == 200


def test_business_settings_are_isolated_between_businesses(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business_a = create_business(
        name="Business A",
        google_review_url="https://example.com/a",
    )

    business_b = create_business(
        name="Business B",
        google_review_url="https://example.com/b",
    )

    set_weekly_reviews_per_waiter(
        business_id=business_a[0],
        weekly_reviews_per_waiter=150,
    )

    set_weekly_reviews_per_waiter(
        business_id=business_b[0],
        weekly_reviews_per_waiter=300,
    )

    settings_a = get_business_settings(business_a[0])
    settings_b = get_business_settings(business_b[0])

    assert settings_a[2] == 150
    assert settings_b[2] == 300


def test_business_settings_returns_none_when_not_configured(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="No Settings Café",
        google_review_url="https://example.com/review",
    )

    assert get_business_settings(business[0]) is None
