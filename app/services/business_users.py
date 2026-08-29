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


def user_has_business_access(user_id, business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM business_users
                WHERE user_id = %s
                  AND business_id = %s;
                """,
                (user_id, business_id),
            )

            return cur.fetchone() is not None

    finally:
        conn.close()


def get_user_business_role(user_id, business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role
                FROM business_users
                WHERE user_id = %s
                  AND business_id = %s;
                """,
                (user_id, business_id),
            )

            business_user = cur.fetchone()

            if not business_user:
                return None

            return business_user[0]

    finally:
        conn.close()


def get_business_users(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.id,
                    u.email,
                    u.active,
                    bu.role,
                    bu.created_at
                FROM business_users bu
                JOIN users u
                    ON u.id = bu.user_id
                WHERE bu.business_id = %s
                ORDER BY bu.id;
                """,
                (business_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()
