from app.database.connection import get_connection


def create_waiter(business_id, name):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO waiters (business_id, name)
                VALUES (%s, %s)
                RETURNING id, business_id, name, active, created_at;
                """,
                (business_id, name),
            )

            waiter = cur.fetchone()
            conn.commit()

            return waiter

    finally:
        conn.close()
