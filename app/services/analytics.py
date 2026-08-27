from app.database.connection import get_connection


def get_business_analytics(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    (SELECT COUNT(*)
                     FROM taps
                     WHERE business_id = %s) AS total_taps,

                    (SELECT COUNT(*)
                     FROM waiters
                     WHERE business_id = %s) AS total_waiters,

                    (SELECT total_reviews
                     FROM review_snapshots
                     WHERE business_id = %s
                     ORDER BY snapshot_date DESC
                     LIMIT 1) AS latest_review_count;
                """,
                (business_id, business_id, business_id),
            )

            return cur.fetchone()

    finally:
        conn.close()
