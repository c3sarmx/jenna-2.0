import hashlib
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GOOGLE_PLACES_LEGACY_BASE_URL = (
    "https://maps.googleapis.com/maps/api/place/details/json"
)


class GooglePlacesError(RuntimeError):
    """Raised when Google Places cannot return place data."""


def _get_api_key():
    api_key = os.environ.get(
        "GOOGLE_PLACES_API_KEY"
    )

    if not api_key:
        raise GooglePlacesError(
            "GOOGLE_PLACES_API_KEY environment variable is required"
        )

    return api_key


def _build_place_details_url(place_id):
    params = {
        "place_id": place_id,
        "fields": "reviews",
        "reviews_sort": "newest",
        "reviews_no_translations": "true",
        "key": _get_api_key(),
    }

    return (
        f"{GOOGLE_PLACES_LEGACY_BASE_URL}?"
        f"{urlencode(params)}"
    )


def _build_review_external_id(review):
    author_url = review.get("author_url") or ""
    timestamp = review.get("time") or ""
    text = review.get("text") or ""

    payload = "|".join(
        (
            author_url,
            str(timestamp),
            text,
        )
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()


def _normalize_review(review):
    external_id = _build_review_external_id(
        review
    )

    return {
        "id": external_id,
        "relative_publish_time_description": review.get(
            "relative_time_description"
        ),
        "rating": review.get("rating"),
        "text": review.get("text"),
        "language_code": review.get("language"),
        "original_text": review.get("text"),
        "original_language_code": review.get("language"),
        "author": {
            "display_name": review.get("author_name"),
            "uri": review.get("author_url"),
            "photo_uri": review.get(
                "profile_photo_url"
            ),
        },
        "publish_time": (
            _timestamp_to_iso(
                review.get("time")
            )
        ),
        "flag_content_uri": None,
        "google_maps_uri": None,
    }


def _timestamp_to_iso(timestamp):
    if not timestamp:
        return None

    from datetime import datetime, timezone

    return datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    ).isoformat()


def get_place_reviews(place_id):
    if not place_id:
        raise ValueError("place_id is required")

    request = Request(
        _build_place_details_url(place_id),
        headers={
            "Content-Type": "application/json",
        },
        method="GET",
    )

    try:
        with urlopen(
            request,
            timeout=15,
        ) as response:
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

    status = payload.get("status")

    if status != "OK":
        error_message = payload.get(
            "error_message"
        ) or status or "UNKNOWN_ERROR"

        raise GooglePlacesError(
            f"Google Places API returned {error_message}"
        )

    reviews = (
        payload.get("result", {}).get("reviews")
        or []
    )

    return [
        _normalize_review(review)
        for review in reviews
    ]
