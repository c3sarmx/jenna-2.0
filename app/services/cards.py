import secrets

from app.database.connection import get_connection


def create_card(business_id, waiter_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            public_id = secrets.token_urlsafe(24)

            cur.execute(
                """
                INSERT INTO cards (
                    business_id,
                    waiter_id,
                    public_id
                )
                VALUES (%s, %s, %s)
                RETURNING id, business_id, waiter_id, public_id, active, created_at;
                """,
                (business_id, waiter_id, public_id),
            )

            card = cur.fetchone()
            conn.commit()

            return card

    finally:
        conn.close()


def get_cards_by_business(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.business_id,
                    c.waiter_id,
                    w.name,
                    c.public_id,
                    c.active,
                    c.created_at
                FROM cards c
                JOIN waiters w
                    ON w.id = c.waiter_id
                WHERE c.business_id = %s
                ORDER BY c.id;
                """,
                (business_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()


def get_card_by_public_id(public_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.id,
                    c.business_id,
                    b.name,
                    b.google_review_url,
                    c.waiter_id,
                    w.name,
                    c.public_id,
                    c.active,
                    c.created_at
                FROM cards c
                JOIN businesses b
                    ON b.id = c.business_id
                JOIN waiters w
                    ON w.id = c.waiter_id
                WHERE c.public_id = %s;
                """,
                (public_id,),
            )

            return cur.fetchone()

    finally:
        conn.close()

def update_card_status(business_id, card_id, active):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE cards
                SET active = %s
                WHERE id = %s
                  AND business_id = %s
                RETURNING id, business_id, waiter_id, public_id, active, created_at;
                """,
                (active, card_id, business_id),
            )

            card = cur.fetchone()
            conn.commit()

            return card

    finally:
        conn.close()
