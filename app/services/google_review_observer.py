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
