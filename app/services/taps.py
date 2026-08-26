from app.database.connection import get_connection


def create_tap(business_id, waiter_id=None, source="nfc"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO taps (business_id, waiter_id, source)
                VALUES (%s, %s, %s)
                RETURNING id, business_id, waiter_id, source, created_at;
                """,
                (business_id, waiter_id, source),
            )

            tap = cur.fetchone()
            conn.commit()

            return tap

    finally:
        conn.close()
