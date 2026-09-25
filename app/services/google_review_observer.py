def get_new_reviews(reviews, known_review_ids):
    known_ids = set(known_review_ids or [])

    new_reviews = []
    seen_ids = set()

    for review in reviews or []:
        review_id = review.get("id")

        if not review_id:
            continue

        if review_id in known_ids:
            continue

        if review_id in seen_ids:
            continue

        seen_ids.add(review_id)
        new_reviews.append(review)

    return new_reviews

from datetime import datetime

from app.services.businesses import get_business_by_id
from app.services.google_places import get_place_reviews
from app.services.google_translate import (
    GoogleTranslateError,
    translate_to_spanish,
)
from app.services.review_evidence import (
    create_review_evidence,
    get_review_evidence_by_business,
)
from app.services.review_auto_attribution import (
    attribute_review_by_waiter_names,
)


def extract_place_id(google_review_url):
    if not google_review_url:
        raise ValueError("google_review_url is required")

    marker = "placeid="

    if marker not in google_review_url:
        raise ValueError(
            "google_review_url does not contain a place_id"
        )

    place_id = google_review_url.split(marker, 1)[1].split(
        "&", 1
    )[0]

    if not place_id:
        raise ValueError("place_id is required")

    return place_id


def _parse_publish_time(value):
    if not value:
        return None

    if value.endswith("Z"):
        value = value[:-1] + "+00:00"

    return datetime.fromisoformat(value)


def backfill_review_translations(business_id):
    existing_evidence = get_review_evidence_by_business(
        business_id
    )

    translated = 0
    skipped = 0

    from app.database.connection import get_connection

    conn = get_connection()

    try:
        for item in existing_evidence:
            review_id = item[0]
            content = item[6]
            translated_content = item[11]

            if (
                item[2] != "google_places"
                or translated_content
                or not content
            ):
                skipped += 1
                continue

            try:
                translated_text = translate_to_spanish(
                    content,
                )
            except GoogleTranslateError:
                skipped += 1
                continue

            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE review_evidence
                    SET translated_content = %s
                    WHERE id = %s
                      AND translated_content IS NULL;
                    """,
                    (translated_text, review_id),
                )

                if cur.rowcount:
                    translated += 1

        conn.commit()
    finally:
        conn.close()

    return {
        "business_id": business_id,
        "translated": translated,
        "skipped": skipped,
    }


def sync_google_reviews(business_id):
    business = get_business_by_id(business_id)

    if not business:
        raise ValueError("business not found")

    google_review_url = business[2]

    place_id = extract_place_id(google_review_url)

    reviews = get_place_reviews(place_id)

    existing_evidence = get_review_evidence_by_business(
        business_id
    )

    known_review_ids = {
        item[3]
        for item in existing_evidence
        if item[3]
    }

    new_reviews = get_new_reviews(
        reviews,
        known_review_ids,
    )

    imported = 0
    duplicates = 0

    for review in new_reviews:
        try:
            content = (
                review.get("original_text")
                or review.get("text")
                or ""
            )

            source_language = (
                review.get("original_language_code")
                or review.get("language_code")
            )

            translated_content = None

            try:
                translated_content = translate_to_spanish(
                    content,
                    source_language=source_language,
                )
            except GoogleTranslateError:
                translated_content = None

            evidence = create_review_evidence(
                business_id=business_id,
                source="google_places",
                external_id=review["id"],
                reviewer_name=(
                    review.get("author") or {}
                ).get("display_name"),
                rating=review.get("rating"),
                content=content,
                translated_content=translated_content,
                published_at=_parse_publish_time(
                    review.get("publish_time")
                ),
                source_url=review.get(
                    "google_maps_uri"
                ),
            )

            attribute_review_by_waiter_names(
                business_id=business_id,
                review_evidence_id=evidence[0],
                content=content,
                translated_content=translated_content,
            )

            imported += 1

        except ValueError as exc:
            if str(exc) == "review evidence already exists":
                duplicates += 1
                continue

            raise

    return {
        "business_id": business_id,
        "place_id": place_id,
        "reviews_received": len(reviews),
        "new_reviews": len(new_reviews),
        "imported": imported,
        "duplicates": duplicates,
    }
