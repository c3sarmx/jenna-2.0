from datetime import date, datetime, timezone

from app.database.connection import get_connection
from app.services.analytics import get_waiter_daily_analytics
from app.services.businesses import create_business
from app.services.taps import create_tap
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


def test_waiter_daily_analytics_returns_zero_days(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Daily Analytics Café",
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

    tap_1 = create_tap(
        business_id=business[0],
        waiter_id=waiter_cesar[0],
        source="nfc",
    )

    tap_2 = create_tap(
        business_id=business[0],
        waiter_id=waiter_cesar[0],
        source="qr",
    )

    tap_3 = create_tap(
        business_id=business[0],
        waiter_id=waiter_aaron[0],
        source="nfc",
    )

    set_tap_date(
        tap_1[0],
        datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc),
    )

    set_tap_date(
        tap_2[0],
        datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc),
    )

    set_tap_date(
        tap_3[0],
        datetime(2026, 9, 14, 14, 0, tzinfo=timezone.utc),
    )

    rows = get_waiter_daily_analytics(
        business_id=business[0],
        date_from="2026-09-12",
        date_to="2026-09-14",
    )

    assert rows == [
        {
            "date": date(2026, 9, 12),
            "waiter_id": waiter_cesar[0],
            "waiter_name": "César",
            "total_taps": 1,
        },
        {
            "date": date(2026, 9, 12),
            "waiter_id": waiter_aaron[0],
            "waiter_name": "Aaron",
            "total_taps": 0,
        },
        {
            "date": date(2026, 9, 13),
            "waiter_id": waiter_cesar[0],
            "waiter_name": "César",
            "total_taps": 0,
        },
        {
            "date": date(2026, 9, 13),
            "waiter_id": waiter_aaron[0],
            "waiter_name": "Aaron",
            "total_taps": 0,
        },
        {
            "date": date(2026, 9, 14),
            "waiter_id": waiter_cesar[0],
            "waiter_name": "César",
            "total_taps": 1,
        },
        {
            "date": date(2026, 9, 14),
            "waiter_id": waiter_aaron[0],
            "waiter_name": "Aaron",
            "total_taps": 1,
        },
    ]


def test_waiter_daily_analytics_respects_date_range(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Date Range Analytics Café",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    tap_inside = create_tap(
        business_id=business[0],
        waiter_id=waiter[0],
        source="nfc",
    )

    tap_outside = create_tap(
        business_id=business[0],
        waiter_id=waiter[0],
        source="nfc",
    )

    set_tap_date(
        tap_inside[0],
        datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )

    set_tap_date(
        tap_outside[0],
        datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc),
    )

    rows = get_waiter_daily_analytics(
        business_id=business[0],
        date_from="2026-09-12",
        date_to="2026-09-14",
    )

    assert len(rows) == 3

    totals = {
        row["date"]: row["total_taps"]
        for row in rows
    }

    assert totals[date(2026, 9, 12)] == 0
    assert totals[date(2026, 9, 13)] == 1
    assert totals[date(2026, 9, 14)] == 0


def test_waiter_daily_analytics_isolates_businesses(
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

    tap_a = create_tap(
        business_id=business_a[0],
        waiter_id=waiter_a[0],
        source="nfc",
    )

    tap_b = create_tap(
        business_id=business_b[0],
        waiter_id=waiter_b[0],
        source="nfc",
    )

    set_tap_date(
        tap_a[0],
        datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )

    set_tap_date(
        tap_b[0],
        datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc),
    )

    rows = get_waiter_daily_analytics(
        business_id=business_a[0],
        date_from="2026-09-13",
        date_to="2026-09-13",
    )

    assert rows == [
        {
            "date": date(2026, 9, 13),
            "waiter_id": waiter_a[0],
            "waiter_name": "César",
            "total_taps": 1,
        },
    ]
