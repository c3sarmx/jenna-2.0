from unittest.mock import patch

from app import create_app


def make_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def login_session(client, user_id=1):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_create_review_evidence_returns_conflict_for_duplicate():
    client = make_app().test_client()
    login_session(client)

    with patch(
        "app.auth.decorators.user_has_business_access",
        return_value=True,
    ), patch(
        "app.routes.review_evidence.create_review_evidence",
        side_effect=ValueError(
            "review evidence already exists"
        ),
    ):
        response = client.post(
            "/api/businesses/4/review-evidence",
            json={
                "source": "manual_import",
                "external_id": "google-review-001",
                "reviewer_name": "Juan Pérez",
                "rating": 5,
                "content": "Excelente atención.",
            },
        )

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "review evidence already exists"
    }


def test_google_reviews_with_different_external_ids_are_not_duplicates(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    from app.services.businesses import create_business
    from app.services.review_evidence import create_review_evidence

    business = create_business(
        name="Google Review Café",
        google_review_url="https://example.com/review",
    )

    first = create_review_evidence(
        business_id=business[0],
        source="google_places",
        external_id="google-review-A",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    second = create_review_evidence(
        business_id=business[0],
        source="google_places",
        external_id="google-review-B",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    assert first[0] != second[0]


def test_google_review_same_external_id_is_duplicate(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    from app.services.businesses import create_business
    from app.services.review_evidence import create_review_evidence

    business = create_business(
        name="Google Review Café",
        google_review_url="https://example.com/review",
    )

    create_review_evidence(
        business_id=business[0],
        source="google_places",
        external_id="google-review-A",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    try:
        create_review_evidence(
            business_id=business[0],
            source="google_places",
            external_id="google-review-A",
            reviewer_name="Otra Persona",
            rating=4,
            content="Contenido completamente diferente.",
        )
    except ValueError as exc:
        assert str(exc) == "review evidence already exists"
    else:
        raise AssertionError(
            "Expected duplicate review evidence error"
        )


def test_manual_review_without_external_id_uses_fingerprint_for_deduplication(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    from app.services.businesses import create_business
    from app.services.review_evidence import create_review_evidence

    business = create_business(
        name="Manual Review Café",
        google_review_url="https://example.com/review",
    )

    create_review_evidence(
        business_id=business[0],
        source="manual_import",
        reviewer_name="Juan Pérez",
        rating=5,
        content="Excelente atención.",
    )

    try:
        create_review_evidence(
            business_id=business[0],
            source="manual_import",
            reviewer_name="Juan Pérez",
            rating=5,
            content="Excelente atención.",
        )
    except ValueError as exc:
        assert str(exc) == "review evidence already exists"
    else:
        raise AssertionError(
            "Expected duplicate review evidence error"
        )
