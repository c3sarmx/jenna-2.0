from app.services.businesses import create_business
from app.services.review_auto_attribution import (
    attribute_review_by_waiter_names,
)
from app.services.review_evidence import create_review_evidence
from app.services.review_attributions import (
    get_review_attributions_by_business,
)
from app.services.waiters import create_waiter


def test_attributes_review_to_mentioned_waiter(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Auto Attribution Café",
    )

    waiter = create_waiter(
        business_id=business[0],
        name="César",
    )

    evidence = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        content="Excelente atención de César.",
    )

    result = attribute_review_by_waiter_names(
        business_id=business[0],
        review_evidence_id=evidence[0],
        content=evidence[6],
    )

    assert result["matched"] == 1
    assert result["created"] == 1
    assert result["skipped"] == 0

    attributions = get_review_attributions_by_business(
        business[0]
    )

    assert len(attributions) == 1
    assert attributions[0][2] == waiter[0]
    assert attributions[0][3] == "name_match"
    assert attributions[0][4] == "high"


def test_attributes_review_to_multiple_waiters(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Multiple Attribution Café",
    )

    waiter_a = create_waiter(
        business_id=business[0],
        name="César",
    )

    waiter_b = create_waiter(
        business_id=business[0],
        name="Aaron",
    )

    evidence = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        content="César y Aaron fueron excelentes.",
    )

    result = attribute_review_by_waiter_names(
        business_id=business[0],
        review_evidence_id=evidence[0],
        content=evidence[6],
    )

    assert result["matched"] == 2
    assert result["created"] == 2
    assert result["skipped"] == 0

    attributions = get_review_attributions_by_business(
        business[0]
    )

    assert len(attributions) == 2
    assert {
        attribution[2]
        for attribution in attributions
    } == {
        waiter_a[0],
        waiter_b[0],
    }


def test_review_without_waiter_name_creates_no_attribution(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="No Match Café",
    )

    create_waiter(
        business_id=business[0],
        name="César",
    )

    evidence = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        content="Excelente comida y ambiente.",
    )

    result = attribute_review_by_waiter_names(
        business_id=business[0],
        review_evidence_id=evidence[0],
        content=evidence[6],
    )

    assert result == {
        "matched": 0,
        "created": 0,
        "skipped": 0,
    }

    assert get_review_attributions_by_business(
        business[0]
    ) == []


def test_repeated_attribution_is_idempotent(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Idempotent Café",
    )

    create_waiter(
        business_id=business[0],
        name="Aaron",
    )

    evidence = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        content="Gracias Aaron por la atención.",
    )

    first = attribute_review_by_waiter_names(
        business_id=business[0],
        review_evidence_id=evidence[0],
        content=evidence[6],
    )

    second = attribute_review_by_waiter_names(
        business_id=business[0],
        review_evidence_id=evidence[0],
        content=evidence[6],
    )

    assert first == {
        "matched": 1,
        "created": 1,
        "skipped": 0,
    }

    assert second == {
        "matched": 1,
        "created": 0,
        "skipped": 1,
    }

    assert len(
        get_review_attributions_by_business(business[0])
    ) == 1
