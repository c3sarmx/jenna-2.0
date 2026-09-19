from datetime import date, datetime, timezone

from app.database.connection import get_connection
from app.services.analytics import get_waiter_weekly_analytics
from app.services.businesses import create_business
from app.services.taps import create_tap
from app.services.waiter_targets import set_waiter_target
from app.services.waiters import create_waiter


def set_tap_date(tap_id, created_at):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE taps
                SET created_at = %s
                WHERE id = %s;
                """,
                (created_at, tap_id),
            )

        conn.commit()

    finally:
        conn.close()


def test_waiter_weekly_analytics_calculates_total_target_and_reach(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Weekly Analytics Café",
        google_review_url="https://example.com/review",
    )

    waiter_cesar = create_waiter(
        business_id=business[0],
        name="César",
    )

    waiter_aaron = create_waiter(
        business_id=business[0],
        name="Aaron",
    )

    set_waiter_target(
        business_id=business[0],
        waiter_id=waiter_cesar[0],
        weekly_target=50,
        effective_from=date(2026, 9, 14),
    )

    set_waiter_target(
        business_id=business[0],
        waiter_id=waiter_aaron[0],
        weekly_target=40,
        effective_from=date(2026, 9, 14),
    )

    for _ in range(5):
        tap = create_tap(
            business_id=business[0],
            waiter_id=waiter_cesar[0],
            source="nfc",
        )

        set_tap_date(
            tap[0],
            datetime(
                2026, 9, 15, 12, 0, tzinfo=timezone.utc
            ),
        )

    for _ in range(4):
        tap = create_tap(
            business_id=business[0],
            waiter_id=waiter_aaron[0],
            source="qr",
        )

        set_tap_date(
            tap[0],
            datetime(
                2026, 9, 16, 12, 0, tzinfo=timezone.utc
            ),
        )

    rows = get_waiter_weekly_analytics(
        business_id=business[0],
        week_start="2026-09-14",
    )

    assert rows == [
        {
            "waiter_id": waiter_cesar[0],
            "waiter_name": "César",
            "week_start": date(2026, 9, 14),
            "week_end": date(2026, 9, 20),
            "total_taps": 5,
            "weekly_target": 50,
            "reach_percentage": 10.0,
        },
        {
            "waiter_id": waiter_aaron[0],
            "waiter_name": "Aaron",
            "week_start": date(2026, 9, 14),
            "week_end": date(2026, 9, 20),
            "total_taps": 4,
            "weekly_target": 40,
            "reach_percentage": 10.0,
        },
    ]


def test_waiter_weekly_analytics_uses_target_at_week_start(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Weekly Target History Café",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    set_waiter_target(
        business_id=business[0],
        waiter_id=waiter[0],
        weekly_target=50,
        effective_from=date(2026, 9, 1),
    )

    set_waiter_target(
        business_id=business[0],
        waiter_id=waiter[0],
        weekly_target=70,
        effective_from=date(2026, 9, 17),
    )

    tap = create_tap(
        business_id=business[0],
        waiter_id=waiter[0],
        source="nfc",
    )

    set_tap_date(
        tap[0],
        datetime(
            2026, 9, 18, 12, 0, tzinfo=timezone.utc
        ),
    )

    rows = get_waiter_weekly_analytics(
        business_id=business[0],
        week_start="2026-09-14",
    )

    assert rows[0]["weekly_target"] == 50
    assert rows[0]["total_taps"] == 1
    assert rows[0]["reach_percentage"] == 2.0


def test_waiter_weekly_analytics_handles_missing_target(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="No Target Café",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    rows = get_waiter_weekly_analytics(
        business_id=business[0],
        week_start="2026-09-14",
    )

    assert rows == [
        {
            "waiter_id": waiter[0],
            "waiter_name": "César",
            "week_start": date(2026, 9, 14),
            "week_end": date(2026, 9, 20),
            "total_taps": 0,
            "weekly_target": None,
            "reach_percentage": None,
        },
    ]


def test_waiter_weekly_analytics_isolates_businesses(
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

    waiter_a = create_waiter(
        business_id=business_a[0],
        name="César",
    )

    waiter_b = create_waiter(
        business_id=business_b[0],
        name="Aaron",
    )

    set_waiter_target(
        business_id=business_a[0],
        waiter_id=waiter_a[0],
        weekly_target=50,
        effective_from=date(2026, 9, 14),
    )

    set_waiter_target(
        business_id=business_b[0],
        waiter_id=waiter_b[0],
        weekly_target=80,
        effective_from=date(2026, 9, 14),
    )

    rows = get_waiter_weekly_analytics(
        business_id=business_a[0],
        week_start="2026-09-14",
    )

    assert len(rows) == 1
    assert rows[0]["waiter_id"] == waiter_a[0]
    assert rows[0]["weekly_target"] == 50
