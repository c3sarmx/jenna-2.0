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

def get_business_by_id(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    name,
                    google_review_url,
                    created_at
                FROM businesses
                WHERE id = %s
                LIMIT 1;
                """,
                (business_id,),
            )

            return cur.fetchone()

    finally:
        conn.close()

def get_businesses_with_google_reviews():
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    name,
                    google_review_url,
                    created_at
                FROM businesses
                WHERE google_review_url IS NOT NULL
                  AND google_review_url <> ''
                ORDER BY id ASC;
                """
            )

            return cur.fetchall()

    finally:
        conn.close()
