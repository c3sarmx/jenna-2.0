import pytest

from app.services.businesses import create_business
from app.services.review_attributions import (
    create_review_attribution,
    get_review_attributions_by_business,
)
from app.services.review_evidence import create_review_evidence
from app.services.waiters import create_waiter


def test_create_review_attribution_flow(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Attribution Café",
        google_review_url="https://example.com/review",
    )

    business_id = business[0]

    waiter = create_waiter(
        business_id=business_id,
        name="César",
    )

    waiter_id = waiter[0]

    evidence = create_review_evidence(
        business_id=business_id,
        source="manual_import",
        content="Excelente atención de César.",
        reviewer_name="Juan Pérez",
        rating=5,
    )

    evidence_id = evidence[0]

    attribution = create_review_attribution(
        business_id=business_id,
        review_evidence_id=evidence_id,
        waiter_id=waiter_id,
        method="name_match",
        confidence="high",
        reason="La reseña menciona explícitamente el nombre César.",
    )

    assert attribution[0] == 1
    assert attribution[1] == evidence_id
    assert attribution[2] == waiter_id
    assert attribution[3] == "name_match"
    assert attribution[4] == "high"
    assert attribution[5] == (
        "La reseña menciona explícitamente el nombre César."
    )


def test_review_attribution_rejects_evidence_from_other_business(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business_a = create_business(
        name="Business A",
        google_review_url="https://example.com/a",
    )

    business_b = create_business(
        name="Business B",
        google_review_url="https://example.com/b",
    )

    waiter = create_waiter(
        business_id=business_a[0],
        name="César",
    )

    evidence = create_review_evidence(
        business_id=business_b[0],
        source="manual_import",
        content="Excelente atención.",
    )

    with pytest.raises(ValueError, match="review evidence does not belong to business"):
        create_review_attribution(
            business_id=business_a[0],
            review_evidence_id=evidence[0],
            waiter_id=waiter[0],
            method="manual",
            confidence="confirmed",
        )


def test_review_attribution_rejects_waiter_from_other_business(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business_a = create_business(
        name="Business A",
        google_review_url="https://example.com/a",
    )

    business_b = create_business(
        name="Business B",
        google_review_url="https://example.com/b",
    )

    waiter = create_waiter(
        business_id=business_b[0],
        name="Aaron",
    )

    evidence = create_review_evidence(
        business_id=business_a[0],
        source="manual_import",
        content="Excelente atención.",
    )

    with pytest.raises(ValueError, match="waiter does not belong to business"):
        create_review_attribution(
            business_id=business_a[0],
            review_evidence_id=evidence[0],
            waiter_id=waiter[0],
            method="manual",
            confidence="confirmed",
        )


def test_review_attribution_rejects_duplicate(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Duplicate Café",
        google_review_url="https://example.com/review",
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

    create_review_attribution(
        business_id=business[0],
        review_evidence_id=evidence[0],
        waiter_id=waiter[0],
        method="name_match",
        confidence="high",
    )

    with pytest.raises(ValueError, match="review attribution already exists"):
        create_review_attribution(
            business_id=business[0],
            review_evidence_id=evidence[0],
            waiter_id=waiter[0],
            method="name_match",
            confidence="high",
        )


def test_review_can_be_attributed_to_multiple_waiters(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Multiple Waiters Café",
        google_review_url="https://example.com/review",
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

    create_review_attribution(
        business_id=business[0],
        review_evidence_id=evidence[0],
        waiter_id=waiter_a[0],
        method="name_match",
        confidence="high",
    )

    create_review_attribution(
        business_id=business[0],
        review_evidence_id=evidence[0],
        waiter_id=waiter_b[0],
        method="name_match",
        confidence="high",
    )

    attributions = get_review_attributions_by_business(
        business[0]
    )

    assert len(attributions) == 2

    waiter_ids = {
        attribution[2]
        for attribution in attributions
    }

    assert waiter_ids == {
        waiter_a[0],
        waiter_b[0],
    }


def test_get_review_attributions_by_business_flow(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="List Attribution Café",
        google_review_url="https://example.com/review",
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

    create_review_attribution(
        business_id=business[0],
        review_evidence_id=evidence[0],
        waiter_id=waiter[0],
        method="manual",
        confidence="confirmed",
        reason="Confirmado por el encargado.",
    )

    attributions = get_review_attributions_by_business(
        business[0]
    )

    assert len(attributions) == 1
    assert attributions[0][1] == evidence[0]
    assert attributions[0][2] == waiter[0]
    assert attributions[0][3] == "manual"
    assert attributions[0][4] == "confirmed"
    assert attributions[0][5] == "Confirmado por el encargado."
