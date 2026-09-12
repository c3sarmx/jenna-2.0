from datetime import date, timedelta

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
                waiter_taps_conditions.append(
                    "t.created_at::date >= %s"
                )
                waiter_taps_params.append(date_from)

            if date_to:
                waiter_taps_conditions.append(
                    "t.created_at::date <= %s"
                )
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

            card_taps_conditions = []
            card_taps_params = []

            if date_from:
                card_taps_conditions.append(
                    "t.created_at::date >= %s"
                )
                card_taps_params.append(date_from)

            if date_to:
                card_taps_conditions.append(
                    "t.created_at::date <= %s"
                )
                card_taps_params.append(date_to)

            card_taps_date_filter = ""

            if card_taps_conditions:
                card_taps_date_filter = (
                    "AND " + " AND ".join(card_taps_conditions)
                )

            cur.execute(
                f"""
                SELECT
                    c.id,
                    c.public_id,
                    c.waiter_id,
                    w.name,
                    COUNT(t.id) AS total_taps
                FROM cards c
                JOIN waiters w
                    ON w.id = c.waiter_id
                LEFT JOIN taps t
                    ON t.card_id = c.id
                    {card_taps_date_filter}
                WHERE c.business_id = %s
                GROUP BY c.id, c.public_id, c.waiter_id, w.name
                ORDER BY total_taps DESC, c.id;
                """,
                card_taps_params + [business_id],
            )

            taps_by_card = cur.fetchall()

            if date_from:
                daily_start = date.fromisoformat(date_from)
            else:
                daily_start = date.today() - timedelta(days=29)

            if date_to:
                daily_end = date.fromisoformat(date_to)
            else:
                daily_end = date.today()

            cur.execute(
                """
                SELECT
                    dates.day::date,
                    COUNT(t.id) AS total_taps
                FROM generate_series(
                    %s::date,
                    %s::date,
                    INTERVAL '1 day'
                ) AS dates(day)
                LEFT JOIN taps t
                    ON t.business_id = %s
                    AND t.created_at::date = dates.day::date
                GROUP BY dates.day
                ORDER BY dates.day;
                """,
                (
                    daily_start,
                    daily_end,
                    business_id,
                ),
            )

            daily_taps = cur.fetchall()

            return summary, taps_by_waiter, taps_by_card, daily_taps

    finally:
        conn.close()


def get_review_analytics(business_id, date_from=None, date_to=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            evidence_conditions = ["re.business_id = %s"]
            evidence_params = [business_id]

            if date_from:
                evidence_conditions.append(
                    "re.published_at::date >= %s"
                )
                evidence_params.append(date_from)

            if date_to:
                evidence_conditions.append(
                    "re.published_at::date <= %s"
                )
                evidence_params.append(date_to)

            evidence_where = " AND ".join(evidence_conditions)

            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS total_review_evidence,

                    COUNT(*) FILTER (
                        WHERE EXISTS (
                            SELECT 1
                            FROM review_attributions ra
                            WHERE ra.review_evidence_id = re.id
                        )
                    ) AS attributed_reviews

                FROM review_evidence re
                WHERE {evidence_where};
                """,
                evidence_params,
            )

            summary = cur.fetchone()

            cur.execute(
                f"""
                SELECT
                    w.id,
                    w.name,
                    COUNT(DISTINCT ra.review_evidence_id)
                        AS total_reviews
                FROM review_attributions ra
                INNER JOIN review_evidence re
                    ON re.id = ra.review_evidence_id
                INNER JOIN waiters w
                    ON w.id = ra.waiter_id
                WHERE {evidence_where}
                GROUP BY w.id, w.name
                ORDER BY total_reviews DESC, w.id;
                """,
                evidence_params,
            )

            reviews_by_waiter = cur.fetchall()

            total_review_evidence = summary[0]
            attributed_reviews = summary[1]

            return {
                "total_review_evidence": total_review_evidence,
                "attributed_reviews": attributed_reviews,
                "unattributed_reviews": (
                    total_review_evidence - attributed_reviews
                ),
                "reviews_by_waiter": [
                    {
                        "waiter_id": waiter[0],
                        "waiter_name": waiter[1],
                        "total_reviews": waiter[2],
                    }
                    for waiter in reviews_by_waiter
                ],
            }

    finally:
        conn.close()
