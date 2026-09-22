import json
from io import BytesIO
from unittest.mock import patch

import pytest

from app.services.google_places import (
    GooglePlacesError,
    get_place_reviews,
)


PLACE_ID = "ChIJ1_fSGAD_0YURIFxtKjfW4r0"


def _google_response():
    return {
        "reviews": [
            {
                "name": (
                    "places/PLACE/reviews/REVIEW_1"
                ),
                "relativePublishTimeDescription": "3 weeks ago",
                "rating": 5,
                "text": {
                    "text": "Veronica was amazing.",
                    "languageCode": "en",
                },
                "originalText": {
                    "text": "Veronica was amazing.",
                    "languageCode": "en",
                },
                "authorAttribution": {
                    "displayName": "Andrea Cagle Villegas",
                    "uri": "https://example.com/author",
                    "photoUri": "https://example.com/photo",
                },
                "publishTime": "2026-08-30T16:01:12Z",
                "flagContentUri": "https://example.com/report",
                "googleMapsUri": "https://example.com/review",
            }
        ]
    }


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_get_place_reviews_returns_normalized_reviews(monkeypatch):
    monkeypatch.setenv(
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    )

    with patch(
        "app.services.google_places.urlopen",
        return_value=FakeResponse(_google_response()),
    ) as mock_urlopen:
        reviews = get_place_reviews(PLACE_ID)

    assert len(reviews) == 1

    review = reviews[0]

    assert review["id"] == "places/PLACE/reviews/REVIEW_1"
    assert review["rating"] == 5
    assert review["text"] == "Veronica was amazing."
    assert review["language_code"] == "en"
    assert review["publish_time"] == (
        "2026-08-30T16:01:12Z"
    )

    assert review["author"]["display_name"] == (
        "Andrea Cagle Villegas"
    )

    assert review["google_maps_uri"] == (
        "https://example.com/review"
    )

    request = mock_urlopen.call_args.args[0]

    assert request.full_url == (
        "https://places.googleapis.com/v1/places/"
        f"{PLACE_ID}"
    )

    assert request.get_header("X-goog-api-key") == (
        "test-api-key"
    )

    assert request.get_header("X-goog-fieldmask") == (
        "reviews"
    )


def test_get_place_reviews_returns_empty_list_when_reviews_missing(
    monkeypatch,
):
    monkeypatch.setenv(
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    )

    response = FakeResponse({})

    with patch(
        "app.services.google_places.urlopen",
        return_value=response,
    ):
        reviews = get_place_reviews(PLACE_ID)

    assert reviews == []


def test_get_place_reviews_requires_place_id():
    with pytest.raises(ValueError, match="place_id is required"):
        get_place_reviews("")


def test_get_place_reviews_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "GOOGLE_PLACES_API_KEY",
        raising=False,
    )

    with pytest.raises(
        GooglePlacesError,
        match="GOOGLE_PLACES_API_KEY",
    ):
        get_place_reviews(PLACE_ID)
