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
