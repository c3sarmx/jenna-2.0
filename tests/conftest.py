import os
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def initialize_test_database():
    load_dotenv(".env")

    database_url = os.environ["DATABASE_URL"]
    test_database_url = (
        database_url.rsplit("/", 1)[0]
        + "/dukkah_2_test"
    )

    schema_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "database"
        / "schema.sql"
    )

    schema_sql = schema_path.read_text()

    conn = psycopg.connect(test_database_url)

    try:
        with conn.cursor() as cur:
            cur.execute(
                "DROP SCHEMA public CASCADE;"
            )
            cur.execute(
                "CREATE SCHEMA public;"
            )
            cur.execute(schema_sql)

        conn.commit()
        yield

    finally:
        conn.close()



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
                    business_settings,
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
                    business_settings,
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
