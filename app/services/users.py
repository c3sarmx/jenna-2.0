from werkzeug.security import generate_password_hash

from app.database.connection import get_connection


def create_user(email, password):
    password_hash = generate_password_hash(password)

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (
                    email,
                    password_hash
                )
                VALUES (%s, %s)
                RETURNING id, email, active, created_at;
                """,
                (email, password_hash),
            )

            user = cur.fetchone()
            conn.commit()

            return user

    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    email,
                    password_hash,
                    active,
                    created_at
                FROM users
                WHERE email = %s;
                """,
                (email,),
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    email,
                    active,
                    created_at
                FROM users
                WHERE id = %s;
                """,
                (user_id,),
            )

            return cur.fetchone()

    finally:
        conn.close()
