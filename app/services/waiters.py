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


def get_waiters_by_business(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, business_id, name, active, created_at
                FROM waiters
                WHERE business_id = %s
                ORDER BY id;
                """,
                (business_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()

def update_waiter_status(business_id, waiter_id, active):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE waiters
                SET active = %s
                WHERE id = %s
                  AND business_id = %s
                RETURNING id, business_id, name, active, created_at;
                """,
                (active, waiter_id, business_id),
            )

            waiter = cur.fetchone()
            conn.commit()

            return waiter

    finally:
        conn.close()
