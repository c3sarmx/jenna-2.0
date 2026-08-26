from app.database.connection import get_connection


def create_business(name, google_review_url=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO businesses (name, google_review_url)
                VALUES (%s, %s)
                RETURNING id, name, google_review_url, created_at;
                """,
                (name, google_review_url),
            )

            business = cur.fetchone()
            conn.commit()

            return business

    finally:
        conn.close()
