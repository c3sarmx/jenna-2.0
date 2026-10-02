from app.services.business_settings import (
    get_business_settings,
    mark_review_sync_error,
    mark_review_sync_run,
)
from app.services.businesses import get_businesses_with_google_reviews
from app.services.google_review_observer import (
    backfill_review_translations,
    sync_google_reviews,
)
from app.services.review_sync_schedule import (
    is_review_sync_allowed,
    is_review_sync_due,
)


def sync_all_google_reviews(now=None):
    businesses = get_businesses_with_google_reviews()

    results = []

    for business in businesses:
        business_id, name, google_review_url, created_at = business

        settings = get_business_settings(business_id)

        if settings is None:
            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "skipped",
                "reason": "settings_not_configured",
            })
            continue

        try:
            allowed = is_review_sync_allowed(
                enabled=settings[5],
                timezone=settings[7],
                schedule=settings[8],
                now=now,
            )
        except Exception as exc:
            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "error",
                "error": str(exc),
            })
            continue

        if not allowed:
            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "skipped",
                "reason": "outside_schedule",
            })
            continue

        try:
            due = is_review_sync_due(
                last_run_at=settings[9],
                interval_minutes=settings[6],
                timezone=settings[7],
                now=now,
            )
        except Exception as exc:
            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "error",
                "error": str(exc),
            })
            continue

        if not due:
            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "skipped",
                "reason": "interval_not_elapsed",
            })
            continue

        try:
            sync_result = sync_google_reviews(business_id)

            mark_review_sync_run(business_id)

            translation_result = backfill_review_translations(
                business_id
            )

            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "ok",
                "result": {
                    **sync_result,
                    "translation_backfill": translation_result,
                },
            })

        except Exception as exc:
            mark_review_sync_error(
                business_id,
                str(exc),
            )

            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "error",
                "error": str(exc),
            })

    return results


if __name__ == "__main__":
    results = sync_all_google_reviews()

    for result in results:
        print(result)
