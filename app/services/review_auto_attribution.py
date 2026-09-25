from app.services.review_attributions import create_review_attribution
from app.services.review_name_matcher import find_waiter_matches
from app.services.waiters import get_waiters_by_business


def attribute_review_by_waiter_names(
    business_id,
    review_evidence_id,
    content,
    translated_content=None,
):
    waiters = get_waiters_by_business(business_id)

    waiter_candidates = [
        {
            "id": waiter[0],
            "name": waiter[2],
        }
        for waiter in waiters
        if waiter[3]
    ]

    matches = find_waiter_matches(
        content,
        waiter_candidates,
        translated_content=translated_content,
    )

    created = 0
    skipped = 0

    for match in matches:
        try:
            create_review_attribution(
                business_id=business_id,
                review_evidence_id=review_evidence_id,
                waiter_id=match["waiter_id"],
                method="name_match",
                confidence=match["confidence"],
                reason=match["reason"],
            )
            created += 1

        except ValueError as exc:
            if str(exc) == "review attribution already exists":
                skipped += 1
                continue

            raise

    return {
        "matched": len(matches),
        "created": created,
        "skipped": skipped,
    }
