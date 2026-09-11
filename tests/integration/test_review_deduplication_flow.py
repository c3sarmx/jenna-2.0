from app.services.businesses import create_business
from app.services.review_evidence import (
    build_review_fingerprint,
    create_review_evidence,
    find_duplicate_review_evidence,
)


def test_find_duplicate_by_external_id(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="External ID Café",
        google_review_url="https://example.com/review",
    )

    evidence = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        external_id="google-review-001",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    result = find_duplicate_review_evidence(
        business_id=business[0],
        external_id="google-review-001",
        fingerprint="different-fingerprint",
    )

    assert result is not None
    assert result[0] == "external_id"
    assert result[1][0] == evidence[0]


def test_find_duplicate_by_fingerprint(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Fingerprint Café",
        google_review_url="https://example.com/review",
    )

    evidence = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    fingerprint = build_review_fingerprint(
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
        published_at=None,
    )

    result = find_duplicate_review_evidence(
        business_id=business[0],
        external_id=None,
        fingerprint=fingerprint,
    )

    assert result is not None
    assert result[0] == "fingerprint"
    assert result[1][0] == evidence[0]


def test_external_id_match_has_priority_over_fingerprint(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="Priority Café",
        google_review_url="https://example.com/review",
    )

    evidence_external = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        external_id="google-review-001",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Primera reseña.",
    )

    evidence_fingerprint = create_review_evidence(
        business_id=business[0],
        source="manual_import",
        reviewer_name="Ana López",
        rating=4,
        content="Segunda reseña.",
    )

    result = find_duplicate_review_evidence(
        business_id=business[0],
        external_id="google-review-001",
        fingerprint=evidence_fingerprint[9],
    )

    assert result is not None
    assert result[0] == "external_id"
    assert result[1][0] == evidence_external[0]


def test_find_duplicate_returns_none_for_new_review(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    business = create_business(
        name="New Review Café",
        google_review_url="https://example.com/review",
    )

    create_review_evidence(
        business_id=business[0],
        source="manual_import",
        external_id="google-review-001",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    result = find_duplicate_review_evidence(
        business_id=business[0],
        external_id="google-review-002",
        fingerprint="not-a-match",
    )

    assert result is None


def test_duplicate_search_is_isolated_by_business(
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

    create_review_evidence(
        business_id=business_a[0],
        source="manual_import",
        external_id="google-review-001",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    result = find_duplicate_review_evidence(
        business_id=business_b[0],
        external_id="google-review-001",
        fingerprint=None,
    )

    assert result is None
