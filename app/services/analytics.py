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
                     LIMIT 1) AS latest_review_count;
                """,
                taps_params
                + [business_id]
                + snapshot_params,
            )

            return cur.fetchone()

    finally:
        conn.close()
