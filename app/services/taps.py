from app.database.connection import get_connection


def create_tap(business_id, waiter_id=None, source="nfc", card_id=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO taps (
                    business_id,
                    waiter_id,
                    source,
                    card_id
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id, business_id, waiter_id, source, created_at, card_id;
                """,
                (business_id, waiter_id, source, card_id),
            )

            tap = cur.fetchone()
            conn.commit()

            return tap

    finally:
        conn.close()


def get_taps_by_business(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    business_id,
                    waiter_id,
                    source,
                    created_at,
                    card_id
                FROM taps
                WHERE business_id = %s
                ORDER BY id;
                """,
                (business_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()
