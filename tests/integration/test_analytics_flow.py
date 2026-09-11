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

    summary, taps_by_waiter, taps_by_card, daily_taps = get_business_analytics(
        business_id=business_id,
    )

    assert len(daily_taps) == 30

    daily_by_date = {
        day: total_taps
        for day, total_taps in daily_taps
    }

    assert daily_by_date[date.today()] == 4

    for day, total_taps in daily_taps:
        if day != date.today():
            assert total_taps == 0

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


def test_review_analytics_flow(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    from app.services.review_attributions import (
        create_review_attribution,
    )
    from app.services.review_evidence import (
        create_review_evidence,
    )
    from app.services.analytics import (
        get_review_analytics,
    )

    business = create_business(
        name="Review Analytics Café",
        google_review_url="https://example.com/review",
    )

    business_id = business[0]

    waiter_cesar = create_waiter(
        business_id=business_id,
        name="César",
    )

    waiter_luis = create_waiter(
        business_id=business_id,
        name="Luis",
    )

    review_1 = create_review_evidence(
        business_id=business_id,
        source="manual_import",
        reviewer_name="Cliente 1",
        rating=5,
        content="Excelente atención de César.",
    )

    review_2 = create_review_evidence(
        business_id=business_id,
        source="manual_import",
        reviewer_name="Cliente 2",
        rating=5,
        content="César y Luis fueron excelentes.",
    )

    create_review_evidence(
        business_id=business_id,
        source="manual_import",
        reviewer_name="Cliente 3",
        rating=4,
        content="Buen servicio.",
    )

    create_review_attribution(
        business_id=business_id,
        review_evidence_id=review_1[0],
        waiter_id=waiter_cesar[0],
        method="name_match",
        confidence="high",
        reason="La reseña menciona explícitamente a César.",
    )

    create_review_attribution(
        business_id=business_id,
        review_evidence_id=review_2[0],
        waiter_id=waiter_cesar[0],
        method="name_match",
        confidence="high",
        reason="La reseña menciona explícitamente a César.",
    )

    create_review_attribution(
        business_id=business_id,
        review_evidence_id=review_2[0],
        waiter_id=waiter_luis[0],
        method="name_match",
        confidence="high",
        reason="La reseña menciona explícitamente a Luis.",
    )

    analytics = get_review_analytics(
        business_id=business_id,
    )

    assert analytics["total_review_evidence"] == 3
    assert analytics["attributed_reviews"] == 2
    assert analytics["unattributed_reviews"] == 1

    assert analytics["reviews_by_waiter"] == [
        {
            "waiter_id": waiter_cesar[0],
            "waiter_name": "César",
            "total_reviews": 2,
        },
        {
            "waiter_id": waiter_luis[0],
            "waiter_name": "Luis",
            "total_reviews": 1,
        },
    ]
