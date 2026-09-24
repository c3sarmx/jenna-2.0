from app.database.connection import get_connection
from app.services.business_settings import (
    get_business_settings,
    set_review_sync_settings,
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


def test_review_sync_settings_can_be_created_and_updated(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Sync Café",
        google_review_url="https://example.com/review",
    )

    schedule = {
        "mon": {"start": "08:00", "end": "22:00"},
        "tue": {"start": "08:00", "end": "22:00"},
        "wed": {"start": "08:00", "end": "22:00"},
        "thu": {"start": "08:00", "end": "22:00"},
        "fri": {"start": "08:00", "end": "23:00"},
        "sat": {"start": "08:00", "end": "23:00"},
        "sun": {"start": "08:00", "end": "20:00"},
    }

    settings = set_review_sync_settings(
        business_id=business[0],
        enabled=True,
        interval_minutes=5,
        timezone="America/Mexico_City",
        schedule=schedule,
    )

    assert settings[1] == business[0]
    assert settings[5] is True
    assert settings[6] == 5
    assert settings[7] == "America/Mexico_City"
    assert settings[8] == schedule

    stored = get_business_settings(business[0])

    assert stored[5] is True
    assert stored[6] == 5
    assert stored[7] == "America/Mexico_City"
    assert stored[8] == schedule


def test_review_sync_settings_are_isolated_between_businesses(
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

    schedule_a = {
        "mon": {"start": "08:00", "end": "22:00"},
    }

    schedule_b = {
        "mon": {"start": "10:00", "end": "18:00"},
    }

    set_review_sync_settings(
        business_id=business_a[0],
        enabled=True,
        interval_minutes=5,
        timezone="America/Mexico_City",
        schedule=schedule_a,
    )

    set_review_sync_settings(
        business_id=business_b[0],
        enabled=False,
        interval_minutes=15,
        timezone="America/Mexico_City",
        schedule=schedule_b,
    )

    settings_a = get_business_settings(business_a[0])
    settings_b = get_business_settings(business_b[0])

    assert settings_a[5] is True
    assert settings_a[6] == 5
    assert settings_a[8] == schedule_a

    assert settings_b[5] is False
    assert settings_b[6] == 15
    assert settings_b[8] == schedule_b


def test_review_sync_settings_rejects_invalid_interval(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Invalid Interval Café",
        google_review_url="https://example.com/review",
    )

    try:
        set_review_sync_settings(
            business_id=business[0],
            enabled=True,
            interval_minutes=0,
            timezone="America/Mexico_City",
            schedule={},
        )
    except ValueError as exc:
        assert str(exc) == "interval_minutes must be greater than 0"
    else:
        raise AssertionError("Expected ValueError")


def test_review_sync_settings_rejects_invalid_timezone(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Invalid Timezone Café",
        google_review_url="https://example.com/review",
    )

    try:
        set_review_sync_settings(
            business_id=business[0],
            enabled=True,
            interval_minutes=5,
            timezone="Invalid/Timezone",
            schedule={},
        )
    except ValueError as exc:
        assert str(exc) == "invalid timezone"
    else:
        raise AssertionError("Expected ValueError")


def test_review_sync_settings_rejects_invalid_schedule(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Invalid Schedule Café",
        google_review_url="https://example.com/review",
    )

    invalid_schedule = {
        "mon": {
            "start": "22:00",
            "end": "08:00",
        },
    }

    try:
        set_review_sync_settings(
            business_id=business[0],
            enabled=True,
            interval_minutes=5,
            timezone="America/Mexico_City",
            schedule=invalid_schedule,
        )
    except ValueError as exc:
        assert str(exc) == "schedule start must be before end"
    else:
        raise AssertionError("Expected ValueError")
