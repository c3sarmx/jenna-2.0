import os

import psycopg
import pytest
from dotenv import load_dotenv


@pytest.fixture
def test_database_url():
    load_dotenv(".env")

    database_url = os.environ["DATABASE_URL"]

    return database_url.rsplit("/", 1)[0] + "/dukkah_2_test"


@pytest.fixture
def app(test_database_url, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", test_database_url)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")

    from app import create_app

    application = create_app()
    application.config["TESTING"] = True

    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def clean_database(test_database_url):
    conn = psycopg.connect(test_database_url)

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE
                    taps,
                    cards,
                    waiters,
                    waiter_targets,
                    review_attributions,
                    review_evidence,
                    review_snapshots,
                    business_users,
                    users,
                    businesses
                RESTART IDENTITY CASCADE;
                """
            )

        conn.commit()

        yield

        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE TABLE
                    taps,
                    cards,
                    waiters,
                    waiter_targets,
                    review_attributions,
                    review_evidence,
                    review_snapshots,
                    business_users,
                    users,
                    businesses
                RESTART IDENTITY CASCADE;
                """
            )

        conn.commit()

    finally:
        conn.close()
