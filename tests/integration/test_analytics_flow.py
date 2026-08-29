from datetime import date

from app.services.analytics import get_business_analytics
from app.services.businesses import create_business
from app.services.cards import create_card
from app.services.review_snapshots import create_review_snapshot
from app.services.taps import create_tap
from app.services.waiters import create_waiter


def test_tap_snapshot_analytics_flow(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Analytics Café",
        google_review_url="https://example.com/review",
    )

    business_id = business[0]

    waiter = create_waiter(
        business_id=business_id,
        name="Analytics Waiter",
    )

    waiter_id = waiter[0]

    card = create_card(
        business_id=business_id,
        waiter_id=waiter_id,
    )

    card_id = card[0]

    create_tap(
        business_id=business_id,
        waiter_id=waiter_id,
        source="nfc",
        card_id=card_id,
    )

    create_tap(
        business_id=business_id,
        waiter_id=waiter_id,
        source="qr",
        card_id=card_id,
    )

    create_tap(
        business_id=business_id,
        waiter_id=waiter_id,
        source="qr",
        card_id=card_id,
    )

    create_tap(
        business_id=business_id,
        waiter_id=waiter_id,
        source="web",
        card_id=card_id,
    )

    create_review_snapshot(
        business_id=business_id,
        snapshot_date=date.today(),
        total_reviews=25,
    )

    summary, taps_by_waiter, taps_by_card = get_business_analytics(
        business_id=business_id,
    )

    assert summary[0] == 4
    assert summary[1] == 1
    assert summary[2] == 25

    assert summary[3] == 1
    assert summary[4] == 2
    assert summary[5] == 1

    assert taps_by_waiter[0][0] == waiter_id
    assert taps_by_waiter[0][1] == "Analytics Waiter"
    assert taps_by_waiter[0][2] == 4

    assert taps_by_card[0][0] == card_id
    assert taps_by_card[0][1] == card[3]
    assert taps_by_card[0][2] == waiter_id
    assert taps_by_card[0][3] == "Analytics Waiter"
    assert taps_by_card[0][4] == 4
