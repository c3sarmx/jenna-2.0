from psycopg.errors import UniqueViolation

from app.database.connection import get_connection


def create_review_snapshot(business_id, snapshot_date, total_reviews=0):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO review_snapshots (
                    business_id,
                    snapshot_date,
                    total_reviews
                )
                VALUES (%s, %s, %s)
                RETURNING id, business_id, snapshot_date, total_reviews;
                """,
                (business_id, snapshot_date, total_reviews),
            )

            snapshot = cur.fetchone()
            conn.commit()

            return snapshot

    except UniqueViolation:
        conn.rollback()
        raise ValueError(
            "A review snapshot already exists for this business on this date"
        )

    finally:
        conn.close()


def get_review_snapshots_by_business(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, business_id, snapshot_date, total_reviews
                FROM review_snapshots
                WHERE business_id = %s
                ORDER BY snapshot_date DESC;
                """,
                (business_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()
