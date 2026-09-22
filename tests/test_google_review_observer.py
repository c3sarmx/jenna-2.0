from unittest.mock import patch

import pytest

from app.services.google_review_observer import (
    extract_place_id,
    get_new_reviews,
)


def test_extract_place_id_from_google_review_url():
    url = (
        "https://search.google.com/local/writereview"
        "?placeid=ChIJ1_fSGAD_0YURIFxtKjfW4r0"
    )

    assert (
        extract_place_id(url)
        == "ChIJ1_fSGAD_0YURIFxtKjfW4r0"
    )


def test_extract_place_id_ignores_other_query_parameters():
    url = (
        "https://example.com/review"
        "?placeid=PLACE123&foo=bar"
    )

    assert extract_place_id(url) == "PLACE123"


def test_extract_place_id_requires_url():
    with pytest.raises(
        ValueError,
        match="google_review_url is required",
    ):
        extract_place_id(None)


def test_extract_place_id_requires_place_id():
    with pytest.raises(
        ValueError,
        match="does not contain a place_id",
    ):
        extract_place_id(
            "https://example.com/review"
        )


def test_get_new_reviews_returns_only_unknown_ids():
    reviews = [
        {"id": "A", "text": "Old"},
        {"id": "B", "text": "New"},
        {"id": "C", "text": "New"},
    ]

    result = get_new_reviews(
        reviews,
        ["A"],
    )

    assert result == [
        {"id": "B", "text": "New"},
        {"id": "C", "text": "New"},
    ]


def test_get_new_reviews_ignores_duplicate_ids_in_same_response():
    reviews = [
        {"id": "A", "text": "Review"},
        {"id": "A", "text": "Review"},
        {"id": "B", "text": "Another"},
    ]

    result = get_new_reviews(
        reviews,
        [],
    )

    assert result == [
        {"id": "A", "text": "Review"},
        {"id": "B", "text": "Another"},
    ]


def test_get_new_reviews_ignores_reviews_without_id():
    reviews = [
        {"text": "Without ID"},
        {"id": "A", "text": "Valid"},
    ]

    result = get_new_reviews(
        reviews,
        [],
    )

    assert result == [
        {"id": "A", "text": "Valid"},
    ]


def test_sync_google_reviews_imports_new_reviews(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv(
        "DATABASE_URL",
        test_database_url,
    )

    from app.services.businesses import create_business
    from app.services.google_review_observer import (
        sync_google_reviews,
    )
    from app.services.review_evidence import (
        get_review_evidence_by_business,
    )

    business = create_business(
        name="Google Sync Café",
        google_review_url=(
            "https://search.google.com/local/writereview"
            "?placeid=PLACE123"
        ),
    )

    reviews = [
        {
            "id": "google-review-A",
            "rating": 5,
            "text": "Excelente atención.",
            "publish_time": "2026-09-22T14:00:00Z",
            "author": {
                "display_name": "Juan Pérez",
            },
            "google_maps_uri": (
                "https://google.com/review/A"
            ),
        },
        {
            "id": "google-review-B",
            "rating": 4,
            "text": "Muy buena experiencia.",
            "publish_time": "2026-09-22T15:00:00Z",
            "author": {
                "display_name": "Ana López",
            },
            "google_maps_uri": (
                "https://google.com/review/B"
            ),
        },
    ]

    with patch(
        "app.services.google_review_observer.get_place_reviews",
        return_value=reviews,
    ):
        result = sync_google_reviews(
            business[0]
        )

    assert result == {
        "business_id": business[0],
        "place_id": "PLACE123",
        "reviews_received": 2,
        "new_reviews": 2,
        "imported": 2,
        "duplicates": 0,
    }

    evidence = get_review_evidence_by_business(
        business[0]
    )

    assert len(evidence) == 2
    assert {
        item[3]
        for item in evidence
    } == {
        "google-review-A",
        "google-review-B",
    }


def test_sync_google_reviews_is_idempotent(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv(
        "DATABASE_URL",
        test_database_url,
    )

    from app.services.businesses import create_business
    from app.services.google_review_observer import (
        sync_google_reviews,
    )
    from app.services.review_evidence import (
        get_review_evidence_by_business,
    )

    business = create_business(
        name="Idempotent Café",
        google_review_url=(
            "https://search.google.com/local/writereview"
            "?placeid=PLACE123"
        ),
    )

    reviews = [
        {
            "id": "google-review-A",
            "rating": 5,
            "text": "Excelente atención.",
            "publish_time": "2026-09-22T14:00:00Z",
            "author": {
                "display_name": "Juan Pérez",
            },
            "google_maps_uri": (
                "https://google.com/review/A"
            ),
        },
        {
            "id": "google-review-B",
            "rating": 4,
            "text": "Muy buena experiencia.",
            "publish_time": "2026-09-22T15:00:00Z",
            "author": {
                "display_name": "Ana López",
            },
            "google_maps_uri": (
                "https://google.com/review/B"
            ),
        },
    ]

    with patch(
        "app.services.google_review_observer.get_place_reviews",
        return_value=reviews,
    ):
        first = sync_google_reviews(
            business[0]
        )

        second = sync_google_reviews(
            business[0]
        )

    assert first["imported"] == 2
    assert second["new_reviews"] == 0
    assert second["imported"] == 0

    evidence = get_review_evidence_by_business(
        business[0]
    )

    assert len(evidence) == 2
