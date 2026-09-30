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
        "status": "OK",
        "result": {
            "reviews": [
                {
                    "author_name": "Andrea Cagle Villegas",
                    "author_url": "https://example.com/author",
                    "profile_photo_url": "https://example.com/photo",
                    "language": "en",
                    "rating": 5,
                    "relative_time_description": "3 weeks ago",
                    "text": "Veronica was amazing.",
                    "time": 1788105672,
                }
            ]
        },
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

    assert len(review["id"]) == 64
    assert all(
        character in "0123456789abcdef"
        for character in review["id"]
    )
    assert review["rating"] == 5
    assert review["text"] == "Veronica was amazing."
    assert review["language_code"] == "en"
    assert review["publish_time"] == (
        "2026-08-30T16:01:12+00:00"
    )

    assert review["author"]["display_name"] == (
        "Andrea Cagle Villegas"
    )

    assert review["google_maps_uri"] is None

    request = mock_urlopen.call_args.args[0]

    assert request.full_url.startswith(
        "https://maps.googleapis.com/maps/api/place/details/json?"
    )

    assert f"place_id={PLACE_ID}" in request.full_url
    assert "fields=reviews" in request.full_url
    assert "reviews_sort=newest" in request.full_url
    assert "reviews_no_translations=true" in request.full_url
    assert "key=test-api-key" in request.full_url


def test_get_place_reviews_returns_empty_list_when_reviews_missing(
    monkeypatch,
):
    monkeypatch.setenv(
        "GOOGLE_PLACES_API_KEY",
        "test-api-key",
    )

    response = FakeResponse({
        "status": "OK",
        "result": {},
    })

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
