from app.services.businesses import get_businesses_with_google_reviews
from app.services.google_review_observer import sync_google_reviews


def sync_all_google_reviews():
    businesses = get_businesses_with_google_reviews()

    results = []

    for business in businesses:
        business_id, name, google_review_url, created_at = business

        try:
            result = sync_google_reviews(business_id)

            results.append({
                "business_id": business_id,
                "business_name": name,
                "status": "ok",
                "result": result,
            })
        except Exception as exc:
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
