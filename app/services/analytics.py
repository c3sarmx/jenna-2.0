from app.database.connection import get_connection


def get_business_analytics(business_id, date_from=None, date_to=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            taps_conditions = ["business_id = %s"]
            taps_params = [business_id]

            if date_from:
                taps_conditions.append("created_at::date >= %s")
                taps_params.append(date_from)

            if date_to:
                taps_conditions.append("created_at::date <= %s")
                taps_params.append(date_to)

            taps_where = " AND ".join(taps_conditions)

            snapshot_conditions = ["business_id = %s"]
            snapshot_params = [business_id]

            if date_from:
                snapshot_conditions.append("snapshot_date >= %s")
                snapshot_params.append(date_from)

            if date_to:
                snapshot_conditions.append("snapshot_date <= %s")
                snapshot_params.append(date_to)

            snapshot_where = " AND ".join(snapshot_conditions)

            cur.execute(
                f"""
                SELECT
                    (SELECT COUNT(*)
                     FROM taps
                     WHERE {taps_where}) AS total_taps,

                    (SELECT COUNT(*)
                     FROM waiters
                     WHERE business_id = %s) AS total_waiters,

                    (SELECT total_reviews
                     FROM review_snapshots
                     WHERE {snapshot_where}
                     ORDER BY snapshot_date DESC
                     LIMIT 1) AS latest_review_count,

                    (SELECT COUNT(*) FILTER (WHERE source = 'nfc')
                     FROM taps
                     WHERE {taps_where}) AS nfc_taps,

                    (SELECT COUNT(*) FILTER (WHERE source = 'qr')
                     FROM taps
                     WHERE {taps_where}) AS qr_taps,

                    (SELECT COUNT(*) FILTER (WHERE source = 'web')
                     FROM taps
                     WHERE {taps_where}) AS web_taps;
                """,
                taps_params
                + [business_id]
                + snapshot_params
                + taps_params
                + taps_params
                + taps_params,
            )

            summary = cur.fetchone()

            waiter_taps_conditions = ["t.business_id = %s"]
            waiter_taps_params = [business_id]

            if date_from:
                waiter_taps_conditions.append("t.created_at::date >= %s")
                waiter_taps_params.append(date_from)

            if date_to:
                waiter_taps_conditions.append("t.created_at::date <= %s")
                waiter_taps_params.append(date_to)

            waiter_taps_where = " AND ".join(waiter_taps_conditions)

            cur.execute(
                f"""
                SELECT
                    w.id,
                    w.name,
                    COUNT(t.id) AS total_taps
                FROM waiters w
                LEFT JOIN taps t
                    ON t.waiter_id = w.id
                    AND {waiter_taps_where}
                WHERE w.business_id = %s
                GROUP BY w.id, w.name
                ORDER BY total_taps DESC, w.id;
                """,
                waiter_taps_params + [business_id],
            )

            taps_by_waiter = cur.fetchall()

            return summary, taps_by_waiter

    finally:
        conn.close()
