
from unittest.mock import patch

from app.jobs.google_reviews import sync_all_google_reviews


def test_sync_all_google_reviews_syncs_all_businesses():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
        (2, "Olivia Café", "https://example.com/review", None),
    ]

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
        side_effect=[
            {"imported": 2},
            {"imported": 3},
        ],
    ):
        results = sync_all_google_reviews()

    assert len(results) == 2
    assert results[0]["business_id"] == 1
    assert results[0]["business_name"] == "Dukkah"
    assert results[0]["status"] == "ok"
    assert results[0]["result"]["imported"] == 2

    assert results[1]["business_id"] == 2
    assert results[1]["business_name"] == "Olivia Café"
    assert results[1]["status"] == "ok"
    assert results[1]["result"]["imported"] == 3


def test_sync_all_google_reviews_continues_after_business_error():
    businesses = [
        (1, "Dukkah", "https://example.com/review", None),
        (2, "Olivia Café", "https://example.com/review", None),
    ]

    with patch(
        "app.jobs.google_reviews.get_businesses_with_google_reviews",
        return_value=businesses,
    ), patch(
        "app.jobs.google_reviews.sync_google_reviews",
        side_effect=[
            RuntimeError("Google API failed"),
            {"imported": 3},
        ],
    ):
        results = sync_all_google_reviews()

    assert len(results) == 2

    assert results[0]["business_id"] == 1
    assert results[0]["status"] == "error"
    assert results[0]["error"] == "Google API failed"

    assert results[1]["business_id"] == 2
    assert results[1]["status"] == "ok"
    assert results[1]["result"]["imported"] == 3
