from app.services.businesses import create_business
from app.services.cards import create_card, get_card_by_public_id
from app.services.waiters import create_waiter


def test_business_waiter_card_flow(test_database_url, monkeypatch, clean_database):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Integration Café",
        google_review_url="https://example.com/review",
    )

    business_id = business[0]

    assert business[1] == "Integration Café"

    waiter = create_waiter(
        business_id=business_id,
        name="Integration Waiter",
    )

    waiter_id = waiter[0]

    assert waiter[1] == business_id
    assert waiter[2] == "Integration Waiter"

    card = create_card(
        business_id=business_id,
        waiter_id=waiter_id,
    )

    assert card[0] is not None
    assert card[1] == business_id
    assert card[2] == waiter_id
    assert card[3]
    assert card[4] is True

    saved_card = get_card_by_public_id(card[3])

    assert saved_card is not None
    assert saved_card[0] == card[0]
    assert saved_card[1] == business_id
    assert saved_card[4] == waiter_id


def test_public_card_flow_records_tap_and_redirects(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    from app import create_app
    from app.services.taps import get_taps_by_business

    business = create_business(
        name="Public Card Café",
        google_review_url="https://example.com/review",
    )

    business_id = business[0]

    waiter = create_waiter(
        business_id=business_id,
        name="Public Card Waiter",
    )

    waiter_id = waiter[0]

    card = create_card(
        business_id=business_id,
        waiter_id=waiter_id,
    )

    public_id = card[3]

    app = create_app()
    app.config["TESTING"] = True

    client = app.test_client()

    response = client.get(
        f"/api/r/{public_id}?source=qr"
    )

    assert response.status_code == 302
    assert response.headers["Location"] == (
        "https://example.com/review"
    )

    taps = get_taps_by_business(business_id)

    assert len(taps) == 1

    tap = taps[0]

    assert tap[1] == business_id
    assert tap[2] == waiter_id
    assert tap[3] == "qr"
    assert tap[5] == card[0]
