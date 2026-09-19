from datetime import date

import pytest

from app.services.businesses import create_business
from app.services.waiter_targets import (
    get_waiter_target,
    get_waiter_targets_by_business,
    set_waiter_target,
)
from app.services.waiters import create_waiter


def test_set_and_get_waiter_target(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Target Test Business",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    target = set_waiter_target(
        business_id=business[0],
        waiter_id=waiter[0],
        weekly_target=50,
        effective_from=date(2026, 9, 1),
    )

    assert target[1] == waiter[0]
    assert target[2] == 50
    assert target[3] == date(2026, 9, 1)

    current = get_waiter_target(
        waiter_id=waiter[0],
        target_date=date(2026, 9, 18),
    )

    assert current[1] == waiter[0]
    assert current[2] == 50
    assert current[3] == date(2026, 9, 1)


def test_waiter_target_uses_latest_effective_date(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Historical Target Business",
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
        weekly_target=60,
        effective_from=date(2026, 10, 1),
    )

    september_target = get_waiter_target(
        waiter_id=waiter[0],
        target_date=date(2026, 9, 18),
    )

    october_target = get_waiter_target(
        waiter_id=waiter[0],
        target_date=date(2026, 10, 10),
    )

    assert september_target[2] == 50
    assert october_target[2] == 60


def test_waiter_targets_are_scoped_to_business(
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
        effective_from=date(2026, 9, 1),
    )

    set_waiter_target(
        business_id=business_b[0],
        waiter_id=waiter_b[0],
        weekly_target=80,
        effective_from=date(2026, 9, 1),
    )

    targets_a = get_waiter_targets_by_business(
        business_id=business_a[0],
        target_date=date(2026, 9, 18),
    )

    targets_b = get_waiter_targets_by_business(
        business_id=business_b[0],
        target_date=date(2026, 9, 18),
    )

    assert len(targets_a) == 1
    assert targets_a[0][1] == waiter_a[0]
    assert targets_a[0][3] == 50

    assert len(targets_b) == 1
    assert targets_b[0][1] == waiter_b[0]
    assert targets_b[0][3] == 80


def test_setting_same_effective_date_updates_target(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Update Target Business",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    effective_date = date(2026, 9, 1)

    first = set_waiter_target(
        business_id=business[0],
        waiter_id=waiter[0],
        weekly_target=50,
        effective_from=effective_date,
    )

    second = set_waiter_target(
        business_id=business[0],
        waiter_id=waiter[0],
        weekly_target=65,
        effective_from=effective_date,
    )

    assert second[0] == first[0]
    assert second[2] == 65

    current = get_waiter_target(
        waiter_id=waiter[0],
        target_date=date(2026, 9, 18),
    )

    assert current[2] == 65


def test_waiter_target_rejects_negative_value(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Invalid Target Business",
        google_review_url="https://example.com/review",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    with pytest.raises(Exception):
        set_waiter_target(
            business_id=business[0],
            waiter_id=waiter[0],
            weekly_target=-1,
            effective_from=date(2026, 9, 1),
        )
