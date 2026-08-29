from app.services.users import create_user, get_user_by_email


def test_create_user_in_database(test_database_url, monkeypatch, clean_database):
    monkeypatch.setenv("DATABASE_URL", test_database_url)

    email = "integration-user@dukkah.test"

    user = create_user(
        email=email,
        password="TestPassword123!",
    )

    assert user[0] is not None
    assert user[1] == email
    assert user[2] is True

    saved_user = get_user_by_email(email)

    assert saved_user is not None
    assert saved_user[0] == user[0]
    assert saved_user[1] == email
