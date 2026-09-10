from psycopg.errors import UniqueViolation

from app.database.connection import get_connection


def create_review_attribution(
    business_id,
    review_evidence_id,
    waiter_id,
    method,
    confidence,
    reason=None,
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT business_id
                FROM review_evidence
                WHERE id = %s;
                """,
                (review_evidence_id,),
            )

            evidence = cur.fetchone()

            if not evidence:
                raise ValueError("review evidence not found")

            if evidence[0] != business_id:
                raise ValueError(
                    "review evidence does not belong to business"
                )

            cur.execute(
                """
                SELECT business_id
                FROM waiters
                WHERE id = %s;
                """,
                (waiter_id,),
            )

            waiter = cur.fetchone()

            if not waiter:
                raise ValueError("waiter not found")

            if waiter[0] != business_id:
                raise ValueError(
                    "waiter does not belong to business"
                )

            cur.execute(
                """
                INSERT INTO review_attributions (
                    review_evidence_id,
                    waiter_id,
                    method,
                    confidence,
                    reason
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING
                    id,
                    review_evidence_id,
                    waiter_id,
                    method,
                    confidence,
                    reason,
                    created_at;
                """,
                (
                    review_evidence_id,
                    waiter_id,
                    method,
                    confidence,
                    reason,
                ),
            )

            attribution = cur.fetchone()

            conn.commit()

            return attribution

    except UniqueViolation:
        conn.rollback()
        raise ValueError(
            "review attribution already exists"
        )

    finally:
        conn.close()


def get_review_attributions_by_business(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    ra.id,
                    ra.review_evidence_id,
                    ra.waiter_id,
                    ra.method,
                    ra.confidence,
                    ra.reason,
                    ra.created_at
                FROM review_attributions AS ra
                INNER JOIN review_evidence AS re
                    ON re.id = ra.review_evidence_id
                WHERE re.business_id = %s
                ORDER BY ra.created_at DESC, ra.id DESC;
                """,
                (business_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()
