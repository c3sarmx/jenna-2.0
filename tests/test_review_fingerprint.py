from datetime import datetime, timezone

from app.services.review_evidence import build_review_fingerprint


def test_review_fingerprint_is_deterministic():
    published_at = datetime(
        2026,
        9,
        10,
        18,
        30,
        tzinfo=timezone.utc,
    )

    first = build_review_fingerprint(
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención de César.",
        published_at=published_at,
    )

    second = build_review_fingerprint(
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención de César.",
        published_at=published_at,
    )

    assert first == second


def test_review_fingerprint_normalizes_text():
    published_at = datetime(
        2026,
        9,
        10,
        18,
        30,
        tzinfo=timezone.utc,
    )

    first = build_review_fingerprint(
        reviewer_name=" Juan   Pérez ",
        rating=5,
        content="  Excelente   atención de César. ",
        published_at=published_at,
    )

    second = build_review_fingerprint(
        reviewer_name="juan pérez",
        rating=5,
        content="excelente atención de césar.",
        published_at=published_at,
    )

    assert first == second


def test_review_fingerprint_changes_when_review_changes():
    published_at = datetime(
        2026,
        9,
        10,
        18,
        30,
        tzinfo=timezone.utc,
    )

    first = build_review_fingerprint(
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
        published_at=published_at,
    )

    second = build_review_fingerprint(
        reviewer_name="Juan Pérez",
        rating=4,
        content="Excelente atención.",
        published_at=published_at,
    )

    assert first != second


def test_review_fingerprint_returns_sha256_hex():
    fingerprint = build_review_fingerprint(
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
        published_at=None,
    )

    assert len(fingerprint) == 64
    assert all(
        character in "0123456789abcdef"
        for character in fingerprint
    )


def test_create_review_evidence_generates_fingerprint(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    from app.services.businesses import create_business
    from app.services.review_evidence import create_review_evidence

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

    assert evidence[9] is not None
    assert len(evidence[9]) == 64
    assert evidence[10] is not None
