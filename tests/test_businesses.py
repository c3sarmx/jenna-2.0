

def test_get_businesses_with_google_reviews(
    test_database_url,
    monkeypatch,
    clean_database,
):
    monkeypatch.setenv(
        "DATABASE_URL",
        test_database_url,
    )

    from app.services.businesses import (
        create_business,
        get_businesses_with_google_reviews,
    )

    create_business(
        name="Con Google",
        google_review_url="https://example.com/google",
    )

    create_business(
        name="Sin Google",
        google_review_url=None,
    )

    businesses = get_businesses_with_google_reviews()

    assert len(businesses) == 1
    assert businesses[0][1] == "Con Google"
    assert businesses[0][2] == (
        "https://example.com/google"
    )
