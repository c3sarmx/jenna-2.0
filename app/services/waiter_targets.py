from app.database.connection import get_connection


def set_waiter_target(
    business_id,
    waiter_id,
    weekly_target,
    effective_from,
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                FROM waiters
                WHERE id = %s
                  AND business_id = %s;
                """,
                (
                    waiter_id,
                    business_id,
                ),
            )

            waiter = cur.fetchone()

            if waiter is None:
                raise ValueError("waiter not found")

            cur.execute(
                """
                INSERT INTO waiter_targets (
                    waiter_id,
                    weekly_target,
                    effective_from
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (waiter_id, effective_from)
                DO UPDATE SET
                    weekly_target = EXCLUDED.weekly_target
                RETURNING
                    id,
                    waiter_id,
                    weekly_target,
                    effective_from,
                    created_at;
                """,
                (
                    waiter_id,
                    weekly_target,
                    effective_from,
                ),
            )

            target = cur.fetchone()
            conn.commit()

            return target

    finally:
        conn.close()


def get_waiter_target(waiter_id, target_date):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    waiter_id,
                    weekly_target,
                    effective_from,
                    created_at
                FROM waiter_targets
                WHERE waiter_id = %s
                  AND effective_from <= %s
                ORDER BY effective_from DESC
                LIMIT 1;
                """,
                (
                    waiter_id,
                    target_date,
                ),
            )

            return cur.fetchone()

    finally:
        conn.close()


def get_waiter_targets_by_business(business_id, target_date):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    wt.id,
                    wt.waiter_id,
                    w.name,
                    wt.weekly_target,
                    wt.effective_from,
                    wt.created_at
                FROM waiter_targets wt
                INNER JOIN waiters w
                    ON w.id = wt.waiter_id
                WHERE w.business_id = %s
                  AND wt.effective_from <= %s
                  AND wt.effective_from = (
                      SELECT MAX(wt2.effective_from)
                      FROM waiter_targets wt2
                      WHERE wt2.waiter_id = wt.waiter_id
                        AND wt2.effective_from <= %s
                  )
                ORDER BY w.id;
                """,
                (
                    business_id,
                    target_date,
                    target_date,
                ),
            )

            return cur.fetchall()

    finally:
        conn.close()
