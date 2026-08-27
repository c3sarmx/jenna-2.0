from werkzeug.security import check_password_hash

from app.database.connection import get_connection


def authenticate_user(email, password):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    active
                FROM users
                WHERE email = %s;
                """,
                (email,),
            )

            user = cur.fetchone()

            if not user:
                return None

            if not user[3]:
                return None

            if not check_password_hash(user[2], password):
                return None

            return {
                "id": user[0],
                "email": user[1],
                "active": user[3],
            }

    finally:
        conn.close()
