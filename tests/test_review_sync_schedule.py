from datetime import datetime

from app.services.review_sync_schedule import (
    is_review_sync_due,
)


def test_sync_is_due_when_never_run():
    now = datetime(
        2026,
        9,
        24,
        12,
        0,
    )

    assert is_review_sync_due(
        last_run_at=None,
        interval_minutes=5,
        timezone="America/Mexico_City",
        now=now,
    ) is True


def test_sync_is_not_due_before_interval():
    last_run_at = datetime(
        2026,
        9,
        24,
        11,
        58,
    )

    now = datetime(
        2026,
        9,
        24,
        12,
        0,
    )

    assert is_review_sync_due(
        last_run_at=last_run_at,
        interval_minutes=5,
        timezone="America/Mexico_City",
        now=now,
    ) is False


def test_sync_is_due_when_interval_has_elapsed():
    last_run_at = datetime(
        2026,
        9,
        24,
        11,
        55,
    )

    now = datetime(
        2026,
        9,
        24,
        12,
        0,
    )

    assert is_review_sync_due(
        last_run_at=last_run_at,
        interval_minutes=5,
        timezone="America/Mexico_City",
        now=now,
    ) is True


def test_sync_is_due_exactly_at_interval_boundary():
    last_run_at = datetime(
        2026,
        9,
        24,
        11,
        55,
    )

    now = datetime(
        2026,
        9,
        24,
        12,
        0,
    )

    assert is_review_sync_due(
        last_run_at=last_run_at,
        interval_minutes=5,
        timezone="America/Mexico_City",
        now=now,
    ) is True


def test_sync_due_handles_aware_last_run_in_different_timezone():
    from datetime import timezone

    last_run_at = datetime(
        2026,
        9,
        24,
        17,
        55,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        9,
        24,
        12,
        0,
    )

    assert is_review_sync_due(
        last_run_at=last_run_at,
        interval_minutes=5,
        timezone="America/Mexico_City",
        now=now,
    ) is True
