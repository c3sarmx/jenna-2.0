from datetime import datetime, timezone

from app.database.connection import get_connection
from app.services.analytics import get_business_weekly_analytics
from app.services.business_settings import (
    set_weekly_reviews_per_waiter,
)
from app.services.businesses import create_business
from app.services.review_attributions import (
    create_review_attribution,
)
from app.services.review_evidence import create_review_evidence
from app.services.waiters import create_waiter


WEEK_START = datetime(
    2026, 9, 14, 12, 0, tzinfo=timezone.utc
)


def create_review(
    business_id,
    reviewer_name,
    published_at,
):
    return create_review_evidence(
        business_id=business_id,
        source="manual_import",
        reviewer_name=reviewer_name,
        rating=5,
        content=f"Excelente atención de {reviewer_name}.",
        published_at=published_at,
    )


def attribute_review(
    business_id,
    review_id,
    waiter_id,
):
    return create_review_attribution(
        business_id=business_id,
        review_evidence_id=review_id,
        waiter_id=waiter_id,
        method="manual",
        confidence="confirmed",
        reason="Atribución de prueba.",
    )


def test_business_weekly_analytics_calculates_daily_reviews_and_reach(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Weekly Reviews Café",
        google_review_url="https://example.com/review",
    )

    business_id = business[0]

    cesar = create_waiter(
        business_id=business_id,
        name="César",
    )

    julio = create_waiter(
        business_id=business_id,
        name="Julio",
    )

    aaron = create_waiter(
        business_id=business_id,
        name="Aaron",
    )

    set_weekly_reviews_per_waiter(
        business_id=business_id,
        weekly_reviews_per_waiter=12,
    )

    # César = 10 reviews
    # Mon 2, Tue 1, Wed 0, Thu 2, Fri 3, Sat 1, Sun 1
    cesar_daily = [
        (0, 2),
        (1, 1),
        (3, 2),
        (4, 3),
        (5, 1),
        (6, 1),
    ]

    for day_offset, count in cesar_daily:
        for index in range(count):
            review = create_review(
                business_id,
                f"César {day_offset}-{index}",
                WEEK_START.replace(
                    day=WEEK_START.day + day_offset
                ),
            )

            attribute_review(
                business_id,
                review[0],
                cesar[0],
            )

    # Julio = 12 reviews
    # 2 reviews Monday through Saturday, 0 Sunday.
    for day_offset in range(6):
        for index in range(2):
            review = create_review(
                business_id,
                f"Julio {day_offset}-{index}",
                WEEK_START.replace(
                    day=WEEK_START.day + day_offset
                ),
            )

            attribute_review(
                business_id,
                review[0],
                julio[0],
            )

    # Aaron = 15 reviews
    # 3 reviews Monday through Friday.
    for day_offset in range(5):
        for index in range(3):
            review = create_review(
                business_id,
                f"Aaron {day_offset}-{index}",
                WEEK_START.replace(
                    day=WEEK_START.day + day_offset
                ),
            )

            attribute_review(
                business_id,
                review[0],
                aaron[0],
            )

    analytics = get_business_weekly_analytics(
        business_id=business_id,
        week_start="2026-09-14",
    )

    assert analytics["week_start"] == datetime(
        2026, 9, 14
    ).date()

    assert analytics["week_end"] == datetime(
        2026, 9, 20
    ).date()

    assert analytics["weekly_reviews_per_waiter"] == 12

    assert analytics["waiters"] == [
        {
            "waiter_id": aaron[0],
            "waiter_name": "Aaron",
            "daily": {
                "monday": 3,
                "tuesday": 3,
                "wednesday": 3,
                "thursday": 3,
                "friday": 3,
                "saturday": 0,
                "sunday": 0,
            },
            "total": 15,
            "reach_percentage": 125.0,
        },
        {
            "waiter_id": cesar[0],
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
            "waiter_id": julio[0],
            "waiter_name": "Julio",
            "daily": {
                "monday": 2,
                "tuesday": 2,
                "wednesday": 2,
                "thursday": 2,
                "friday": 2,
                "saturday": 2,
                "sunday": 0,
            },
            "total": 12,
            "reach_percentage": 100.0,
        },
    ]


def test_business_weekly_analytics_ignores_reviews_outside_week(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Weekly Range Café",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    set_weekly_reviews_per_waiter(
        business_id=business[0],
        weekly_reviews_per_waiter=12,
    )

    inside = create_review(
        business[0],
        "Inside",
        datetime(
            2026, 9, 18, 12, 0, tzinfo=timezone.utc
        ),
    )

    before = create_review(
        business[0],
        "Before",
        datetime(
            2026, 9, 13, 12, 0, tzinfo=timezone.utc
        ),
    )

    after = create_review(
        business[0],
        "After",
        datetime(
            2026, 9, 21, 12, 0, tzinfo=timezone.utc
        ),
    )

    attribute_review(
        business[0],
        inside[0],
        waiter[0],
    )

    attribute_review(
        business[0],
        before[0],
        waiter[0],
    )

    attribute_review(
        business[0],
        after[0],
        waiter[0],
    )

    analytics = get_business_weekly_analytics(
        business_id=business[0],
        week_start="2026-09-14",
    )

    waiter_data = analytics["waiters"][0]

    assert waiter_data["daily"]["friday"] == 1
    assert waiter_data["total"] == 1
    assert waiter_data["reach_percentage"] == 8.33


def test_business_weekly_analytics_excludes_inactive_waiters(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Active Waiters Café",
        google_review_url="https://example.com/review",
    )

    active_waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    inactive_waiter = create_waiter(
        business_id=business[0],
        name="Julio",
    )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE waiters
                SET active = FALSE
                WHERE id = %s;
                """,
                (inactive_waiter[0],),
            )

        conn.commit()

    finally:
        conn.close()

    set_weekly_reviews_per_waiter(
        business_id=business[0],
        weekly_reviews_per_waiter=12,
    )

    review = create_review(
        business[0],
        "Inactive",
        datetime(
            2026, 9, 15, 12, 0, tzinfo=timezone.utc
        ),
    )

    attribute_review(
        business[0],
        review[0],
        inactive_waiter[0],
    )

    analytics = get_business_weekly_analytics(
        business_id=business[0],
        week_start="2026-09-14",
    )

    assert len(analytics["waiters"]) == 1
    assert analytics["waiters"][0]["waiter_id"] == active_waiter[0]


def test_business_weekly_analytics_isolates_businesses(
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
        name="Luis",
    )

    set_weekly_reviews_per_waiter(
        business_id=business_a[0],
        weekly_reviews_per_waiter=12,
    )

    set_weekly_reviews_per_waiter(
        business_id=business_b[0],
        weekly_reviews_per_waiter=12,
    )

    review_a = create_review(
        business_a[0],
        "Business A",
        datetime(
            2026, 9, 15, 12, 0, tzinfo=timezone.utc
        ),
    )

    review_b = create_review(
        business_b[0],
        "Business B",
        datetime(
            2026, 9, 15, 12, 0, tzinfo=timezone.utc
        ),
    )

    attribute_review(
        business_a[0],
        review_a[0],
        waiter_a[0],
    )

    attribute_review(
        business_b[0],
        review_b[0],
        waiter_b[0],
    )

    analytics = get_business_weekly_analytics(
        business_id=business_a[0],
        week_start="2026-09-14",
    )

    assert len(analytics["waiters"]) == 1
    assert analytics["waiters"][0]["waiter_id"] == waiter_a[0]
    assert analytics["waiters"][0]["total"] == 1


def test_business_weekly_analytics_allows_missing_target(
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

    review = create_review(
        business[0],
        "No Target",
        datetime(
            2026, 9, 15, 12, 0, tzinfo=timezone.utc
        ),
    )

    attribute_review(
        business[0],
        review[0],
        waiter[0],
    )

    analytics = get_business_weekly_analytics(
        business_id=business[0],
        week_start="2026-09-14",
    )

    assert analytics["weekly_reviews_per_waiter"] is None
    assert analytics["waiters"][0]["total"] == 1
    assert analytics["waiters"][0]["reach_percentage"] is None


def test_business_weekly_analytics_does_not_use_taps(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Taps Do Not Matter Café",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    set_weekly_reviews_per_waiter(
        business_id=business[0],
        weekly_reviews_per_waiter=12,
    )

    from app.services.taps import create_tap

    for _ in range(20):
        create_tap(
            business_id=business[0],
            waiter_id=waiter[0],
            source="nfc",
        )

    analytics = get_business_weekly_analytics(
        business_id=business[0],
        week_start="2026-09-14",
    )

    assert analytics["waiters"][0]["total"] == 0
    assert analytics["waiters"][0]["reach_percentage"] == 0.0
