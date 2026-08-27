from app.database.connection import get_connection


def assign_user_to_business(user_id, business_id, role="owner"):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO business_users (
                    user_id,
                    business_id,
                    role
                )
                VALUES (%s, %s, %s)
                RETURNING id, user_id, business_id, role, created_at;
                """,
                (user_id, business_id, role),
            )

            business_user = cur.fetchone()
            conn.commit()

            return business_user

    finally:
        conn.close()


def get_user_businesses(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    b.id,
                    b.name,
                    bu.role
                FROM business_users bu
                JOIN businesses b
                    ON b.id = bu.business_id
                WHERE bu.user_id = %s
                ORDER BY b.id;
                """,
                (user_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()
