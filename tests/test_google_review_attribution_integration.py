from app.services.businesses import create_business
from app.services.review_attributions import get_review_attributions_by_business
from app.services.google_review_observer import sync_google_reviews
from app.services.waiters import create_waiter


def test_google_sync_auto_attributes_new_review(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Google Attribution Café",
        google_review_url=(
            "https://search.google.com/local/writereview"
            "?placeid=test-place-id"
        ),
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    def fake_get_place_reviews(place_id):
        assert place_id == "test-place-id"
        return [
            {
                "id": "google-review-1",
                "rating": 5,
                "text": "Excelente atención de César.",
                "author": {
                    "display_name": "Cliente",
                },
                "publish_time": "2026-09-20T12:00:00Z",
                "google_maps_uri": "https://maps.google.com/review/1",
            }
        ]

    monkeypatch.setattr(
        "app.services.google_review_observer.get_place_reviews",
        fake_get_place_reviews,
    )

    result = sync_google_reviews(business[0])

    assert result["imported"] == 1

    attributions = get_review_attributions_by_business(
        business[0],
    )

    assert len(attributions) == 1
    assert attributions[0][2] == waiter[0]
    assert attributions[0][3] == "name_match"
    assert attributions[0][4] == "high"


def test_google_sync_does_not_attribute_review_without_waiter_name(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="No Attribution Café",
        google_review_url=(
            "https://search.google.com/local/writereview"
            "?placeid=test-place-id"
        ),
    )

    create_waiter(
        business_id=business[0],
        name="César",
    )

    def fake_get_place_reviews(place_id):
        return [
            {
                "id": "google-review-2",
                "rating": 5,
                "text": "Todo estuvo excelente.",
                "author": {
                    "display_name": "Cliente",
                },
                "publish_time": "2026-09-20T12:00:00Z",
                "google_maps_uri": "https://maps.google.com/review/2",
            }
        ]

    monkeypatch.setattr(
        "app.services.google_review_observer.get_place_reviews",
        fake_get_place_reviews,
    )

    result = sync_google_reviews(business[0])

    assert result["imported"] == 1

    attributions = get_review_attributions_by_business(
        business[0],
    )

    assert attributions == []


def test_google_sync_auto_attributes_multiple_waiters(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Multiple Google Attribution Café",
        google_review_url=(
            "https://search.google.com/local/writereview"
            "?placeid=test-place-id"
        ),
    )

    waiter_a = create_waiter(
        business_id=business[0],
        name="César",
    )

    waiter_b = create_waiter(
        business_id=business[0],
        name="Aaron",
    )

    def fake_get_place_reviews(place_id):
        return [
            {
                "id": "google-review-3",
                "rating": 5,
                "text": "César y Aaron fueron excelentes.",
                "author": {
                    "display_name": "Cliente",
                },
                "publish_time": "2026-09-20T12:00:00Z",
                "google_maps_uri": "https://maps.google.com/review/3",
            }
        ]

    monkeypatch.setattr(
        "app.services.google_review_observer.get_place_reviews",
        fake_get_place_reviews,
    )

    result = sync_google_reviews(business[0])

    assert result["imported"] == 1

    attributions = get_review_attributions_by_business(
        business[0],
    )

    assert len(attributions) == 2

    waiter_ids = {
        attribution[2]
        for attribution in attributions
    }

    assert waiter_ids == {
        waiter_a[0],
        waiter_b[0],
    }
