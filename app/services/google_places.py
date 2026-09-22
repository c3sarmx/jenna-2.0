import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


GOOGLE_PLACES_BASE_URL = (
    "https://places.googleapis.com/v1/places"
)


class GooglePlacesError(RuntimeError):
    """Raised when Google Places cannot return place data."""


def _get_api_key():
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")

    if not api_key:
        raise GooglePlacesError(
            "GOOGLE_PLACES_API_KEY environment variable is required"
        )

    return api_key


def _build_place_details_url(place_id):
    return f"{GOOGLE_PLACES_BASE_URL}/{place_id}"


def _normalize_review(review):
    text = review.get("text") or {}
    original_text = review.get("originalText") or {}
    author = review.get("authorAttribution") or {}

    return {
        "id": review.get("name"),
        "relative_publish_time_description": review.get(
            "relativePublishTimeDescription"
        ),
        "rating": review.get("rating"),
        "text": text.get("text"),
        "language_code": text.get("languageCode"),
        "original_text": original_text.get("text"),
        "original_language_code": original_text.get(
            "languageCode"
        ),
        "author": {
            "display_name": author.get("displayName"),
            "uri": author.get("uri"),
            "photo_uri": author.get("photoUri"),
        },
        "publish_time": review.get("publishTime"),
        "flag_content_uri": review.get("flagContentUri"),
        "google_maps_uri": review.get("googleMapsUri"),
    }


def get_place_reviews(place_id):
    if not place_id:
        raise ValueError("place_id is required")

    api_key = _get_api_key()

    request = Request(
        _build_place_details_url(place_id),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "reviews",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as exc:
        raise GooglePlacesError(
            f"Google Places API returned HTTP {exc.code}"
        ) from exc

    except URLError as exc:
        raise GooglePlacesError(
            "Unable to reach Google Places API"
        ) from exc

    except json.JSONDecodeError as exc:
        raise GooglePlacesError(
            "Google Places API returned invalid JSON"
        ) from exc

    reviews = payload.get("reviews") or []

    return [
        _normalize_review(review)
        for review in reviews
    ]
