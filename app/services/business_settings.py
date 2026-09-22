from app.database.connection import get_connection


def get_business_settings(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    business_id,
                    weekly_reviews_per_waiter,
                    created_at,
                    updated_at
                FROM business_settings
                WHERE business_id = %s;
                """,
                (business_id,),
            )

            return cur.fetchone()

    finally:
        conn.close()


def set_weekly_reviews_per_waiter(
    business_id,
    weekly_reviews_per_waiter,
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                FROM businesses
                WHERE id = %s;
                """,
                (business_id,),
            )

            if cur.fetchone() is None:
                raise ValueError("business not found")

            cur.execute(
                """
                INSERT INTO business_settings (
                    business_id,
                    weekly_reviews_per_waiter
                )
                VALUES (%s, %s)
                ON CONFLICT (business_id)
                DO UPDATE SET
                    weekly_reviews_per_waiter =
                        EXCLUDED.weekly_reviews_per_waiter,
                    updated_at = NOW()
                RETURNING
                    id,
                    business_id,
                    weekly_reviews_per_waiter,
                    created_at,
                    updated_at;
                """,
                (
                    business_id,
                    weekly_reviews_per_waiter,
                ),
            )

            settings = cur.fetchone()
            conn.commit()

            return settings

    finally:
        conn.close()
