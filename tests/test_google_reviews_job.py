from datetime import datetime
from unittest.mock import patch

from app.jobs.google_reviews import sync_all_google_reviews


SCHEDULE = {
    "mon": {"start": "08:00", "end": "22:00"},
    "tue": {"start": "08:00", "end": "22:00"},
    "wed": {"start": "08:00", "end": "22:00"},
    "thu": {"start": "08:00", "end": "22:00"},
    "fri": {"start": "08:00", "end": "23:00"},
    "sat": {"start": "08:00", "end": "23:00"},
    "sun": {"start": "08:00", "end": "20:00"},
}


def make_settings(
    business_id,
    enabled=True,
    interval_minutes=5,
    timezone="America/Mexico_City",
    schedule=SCHEDULE,
    last_run_at=None,
):
    return (
        1,
        business_id,
        150,
        datetime(2026, 9, 18, 12, 0),
        datetime(2026, 9, 18, 12, 0),
        enabled,
        interval_minutes,
        timezone,
        schedule,
        last_run_at,
    )


def test_sync_all_google_reviews_syncs_businesses_inside_schedule():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
        (2, "Olivia Café", "https://example.com/review", None),
    ]

    now = datetime(
        2026,
        9,
        21,
        12,
        0,
    )

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.get_business_settings",
        side_effect=[
            make_settings(1),
            make_settings(2),
        ],
    ), patch(
        "app.jobs.google_reviews.is_review_sync_allowed",
        return_value=True,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
        side_effect=[
            {"imported": 2},
            {"imported": 3},
        ],
    ) as sync_mock, patch(
        "app.jobs.google_reviews.mark_review_sync_run",
    ) as mark_sync_mock, patch(
        "app.jobs.google_reviews.backfill_review_translations",
        side_effect=[
            {"translated": 5, "skipped": 0},
            {"translated": 2, "skipped": 1},
        ],
    ):
        results = sync_all_google_reviews(now=now)

    assert len(results) == 2

    assert results[0]["business_id"] == 1
    assert results[0]["status"] == "ok"
    assert results[0]["result"]["imported"] == 2

    assert results[1]["business_id"] == 2
    assert results[1]["status"] == "ok"
    assert results[1]["result"]["imported"] == 3

    assert sync_mock.call_count == 2
    assert mark_sync_mock.call_count == 2


def test_sync_all_google_reviews_skips_business_outside_schedule():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
    ]

    now = datetime(
        2026,
        9,
        21,
        7,
        59,
    )

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.get_business_settings",
        return_value=make_settings(1),
    ), patch(
        "app.jobs.google_reviews.is_review_sync_allowed",
        return_value=False,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
    ) as sync_mock, patch(
        "app.jobs.google_reviews.backfill_review_translations",
    ) as translation_mock:
        results = sync_all_google_reviews(now=now)

    assert len(results) == 1
    assert results[0]["business_id"] == 1
    assert results[0]["status"] == "skipped"
    assert results[0]["reason"] == "outside_schedule"

    sync_mock.assert_not_called()
    translation_mock.assert_not_called()


def test_sync_all_google_reviews_skips_disabled_business():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
    ]

    now = datetime(
        2026,
        9,
        21,
        12,
        0,
    )

    disabled_settings = make_settings(
        1,
        enabled=False,
    )

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.get_business_settings",
        return_value=disabled_settings,
    ), patch(
        "app.jobs.google_reviews.is_review_sync_allowed",
        return_value=False,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
    ) as sync_mock:
        results = sync_all_google_reviews(now=now)

    assert results[0]["status"] == "skipped"
    assert results[0]["reason"] == "outside_schedule"

    sync_mock.assert_not_called()


def test_sync_all_google_reviews_skips_business_without_settings():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
    ]

    now = datetime(
        2026,
        9,
        21,
        12,
        0,
    )

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.get_business_settings",
        return_value=None,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
    ) as sync_mock:
        results = sync_all_google_reviews(now=now)

    assert results[0]["status"] == "skipped"
    assert results[0]["reason"] == "settings_not_configured"

    sync_mock.assert_not_called()


def test_sync_all_google_reviews_continues_after_business_error():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
        (2, "Olivia Café", "https://example.com/review", None),
    ]

    now = datetime(
        2026,
        9,
        21,
        12,
        0,
    )

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.get_business_settings",
        side_effect=[
            make_settings(1),
            make_settings(2),
        ],
    ), patch(
        "app.jobs.google_reviews.is_review_sync_allowed",
        return_value=True,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
        side_effect=[
            RuntimeError("Google API failed"),
            {"imported": 3},
        ],
    ), patch(
        "app.jobs.google_reviews.mark_review_sync_run",
    ) as mark_sync_mock, patch(
        "app.jobs.google_reviews.backfill_review_translations",
        return_value={"translated": 2, "skipped": 0},
    ):
        results = sync_all_google_reviews(now=now)

    assert len(results) == 2

    assert results[0]["business_id"] == 1
    assert results[0]["status"] == "error"
    assert results[0]["error"] == "Google API failed"

    assert results[1]["business_id"] == 2
    assert results[1]["status"] == "ok"
    assert results[1]["result"]["imported"] == 3


def test_sync_all_google_reviews_skips_when_interval_has_not_elapsed():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
    ]

    now = datetime(
        2026,
        9,
        21,
        12,
        0,
    )

    last_run_at = datetime(
        2026,
        9,
        21,
        11,
        58,
    )

    settings = make_settings(
        1,
        interval_minutes=5,
        last_run_at=last_run_at,
    )

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.get_business_settings",
        return_value=settings,
    ), patch(
        "app.jobs.google_reviews.is_review_sync_allowed",
        return_value=True,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
    ) as sync_mock, patch(
        "app.jobs.google_reviews.mark_review_sync_run",
    ) as mark_sync_mock:
        results = sync_all_google_reviews(now=now)

    assert results == [{
        "business_id": 1,
        "business_name": "Dukkah",
        "status": "skipped",
        "reason": "interval_not_elapsed",
    }]

    sync_mock.assert_not_called()
    mark_sync_mock.assert_not_called()


def test_sync_all_google_reviews_syncs_when_interval_has_elapsed():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
    ]

    now = datetime(
        2026,
        9,
        21,
        12,
        0,
    )

    last_run_at = datetime(
        2026,
        9,
        21,
        11,
        55,
    )

    settings = make_settings(
        1,
        interval_minutes=5,
        last_run_at=last_run_at,
    )

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.get_business_settings",
        return_value=settings,
    ), patch(
        "app.jobs.google_reviews.is_review_sync_allowed",
        return_value=True,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
        return_value={"imported": 2},
    ) as sync_mock, patch(
        "app.jobs.google_reviews.mark_review_sync_run",
    ) as mark_sync_mock, patch(
        "app.jobs.google_reviews.backfill_review_translations",
        return_value={"translated": 2, "skipped": 0},
    ):
        results = sync_all_google_reviews(now=now)

    assert results[0]["status"] == "ok"
    assert results[0]["result"]["imported"] == 2

    sync_mock.assert_called_once_with(1)
    mark_sync_mock.assert_called_once_with(1)
