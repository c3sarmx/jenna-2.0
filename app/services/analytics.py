from datetime import date, timedelta

from app.database.connection import get_connection


def _set_business_timezone(cur, business_id):
    cur.execute(
        """
        SELECT COALESCE(
            review_sync_timezone,
            'America/Mexico_City'
        )
        FROM business_settings
        WHERE business_id = %s;
        """,
        (business_id,),
    )

    row = cur.fetchone()
    timezone = row[0] if row and row[0] else "America/Mexico_City"

    cur.execute(
        "SELECT set_config('timezone', %s, false)",
        (timezone,),
    )

    cur.execute("SELECT CURRENT_DATE")
    return cur.fetchone()[0]


def get_business_analytics(business_id, date_from=None, date_to=None):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            local_today = _set_business_timezone(cur, business_id)

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
                daily_start = local_today - timedelta(days=29)

            if date_to:
                daily_end = date.fromisoformat(date_to)
            else:
                daily_end = local_today

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
            _set_business_timezone(cur, business_id)

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


def get_waiter_daily_analytics(business_id, date_from, date_to):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            _set_business_timezone(cur, business_id)

            cur.execute(
                """
                SELECT
                    dates.day::date AS date,
                    w.id AS waiter_id,
                    w.name AS waiter_name,
                    COUNT(t.id) AS total_taps
                FROM generate_series(
                    %s::date,
                    %s::date,
                    INTERVAL '1 day'
                ) AS dates(day)
                CROSS JOIN waiters w
                LEFT JOIN taps t
                    ON t.business_id = %s
                    AND t.waiter_id = w.id
                    AND t.created_at::date = dates.day::date
                WHERE w.business_id = %s
                GROUP BY
                    dates.day,
                    w.id,
                    w.name
                ORDER BY
                    dates.day,
                    w.id;
                """,
                (
                    date_from,
                    date_to,
                    business_id,
                    business_id,
                ),
            )

            rows = cur.fetchall()

            return [
                {
                    "date": row[0],
                    "waiter_id": row[1],
                    "waiter_name": row[2],
                    "total_taps": row[3],
                }
                for row in rows
            ]

    finally:
        conn.close()


def get_business_weekly_analytics(business_id, week_start):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                WITH week AS (
                    SELECT
                        %s::date AS week_start,
                        (%s::date + INTERVAL '6 days')::date
                            AS week_end
                ),
                daily_reviews AS (
                    SELECT
                        ra.waiter_id,
                        (
                            re.published_at AT TIME ZONE COALESCE(
                                settings.review_sync_timezone,
                                'America/Mexico_City'
                            )
                        )::date AS review_date,
                        COUNT(DISTINCT re.id) AS review_count
                    FROM review_attributions AS ra
                    INNER JOIN review_evidence AS re
                        ON re.id = ra.review_evidence_id
                    LEFT JOIN business_settings AS settings
                        ON settings.business_id = re.business_id
                    INNER JOIN week
                        ON (
                            re.published_at AT TIME ZONE COALESCE(
                                settings.review_sync_timezone,
                                'America/Mexico_City'
                            )
                        )::date
                            BETWEEN week.week_start
                            AND week.week_end
                    WHERE re.business_id = %s
                      AND re.published_at IS NOT NULL
                    GROUP BY
                        ra.waiter_id,
                        (
                            re.published_at AT TIME ZONE COALESCE(
                                settings.review_sync_timezone,
                                'America/Mexico_City'
                            )
                        )::date
                )
                SELECT
                    w.id,
                    w.name,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN dr.review_date = week.week_start
                                THEN dr.review_count
                                ELSE 0
                            END
                        ),
                        0
                    ) AS monday,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN dr.review_date =
                                    week.week_start + 1
                                THEN dr.review_count
                                ELSE 0
                            END
                        ),
                        0
                    ) AS tuesday,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN dr.review_date =
                                    week.week_start + 2
                                THEN dr.review_count
                                ELSE 0
                            END
                        ),
                        0
                    ) AS wednesday,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN dr.review_date =
                                    week.week_start + 3
                                THEN dr.review_count
                                ELSE 0
                            END
                        ),
                        0
                    ) AS thursday,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN dr.review_date =
                                    week.week_start + 4
                                THEN dr.review_count
                                ELSE 0
                            END
                        ),
                        0
                    ) AS friday,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN dr.review_date =
                                    week.week_start + 5
                                THEN dr.review_count
                                ELSE 0
                            END
                        ),
                        0
                    ) AS saturday,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN dr.review_date =
                                    week.week_start + 6
                                THEN dr.review_count
                                ELSE 0
                            END
                        ),
                        0
                    ) AS sunday,
                    settings.weekly_reviews_per_waiter,
                    week.week_start,
                    week.week_end
                FROM waiters AS w
                CROSS JOIN week
                LEFT JOIN daily_reviews AS dr
                    ON dr.waiter_id = w.id
                LEFT JOIN business_settings AS settings
                    ON settings.business_id = w.business_id
                WHERE w.business_id = %s
                  AND w.active = TRUE
                GROUP BY
                    w.id,
                    w.name,
                    settings.weekly_reviews_per_waiter,
                    week.week_start,
                    week.week_end
                ORDER BY
                    w.name ASC;
                """,
                (
                    week_start,
                    week_start,
                    business_id,
                    business_id,
                ),
            )

            rows = cur.fetchall()

            if not rows:
                cur.execute(
                    """
                    SELECT
                        %s::date AS week_start,
                        (%s::date + INTERVAL '6 days')::date
                            AS week_end,
                        weekly_reviews_per_waiter
                    FROM business_settings
                    WHERE business_id = %s;
                    """,
                    (
                        week_start,
                        week_start,
                        business_id,
                    ),
                )

                settings = cur.fetchone()

                if settings is None:
                    weekly_reviews_per_waiter = None
                else:
                    weekly_reviews_per_waiter = settings[2]

                return {
                    "week_start": (
                        settings[0]
                        if settings
                        else week_start
                    ),
                    "week_end": (
                        settings[1]
                        if settings
                        else (
                            week_start
                            + __import__("datetime").timedelta(days=6)
                        )
                    ),
                    "weekly_reviews_per_waiter": weekly_reviews_per_waiter,
                    "waiters": [],
                }

            week_start_date = rows[0][10]
            week_end_date = rows[0][11]
            weekly_reviews_per_waiter = rows[0][9]

            if weekly_reviews_per_waiter is not None:
                weekly_reviews_per_waiter = int(weekly_reviews_per_waiter)

            waiters = []

            for row in rows:
                daily = {
                    "monday": int(row[2]),
                    "tuesday": int(row[3]),
                    "wednesday": int(row[4]),
                    "thursday": int(row[5]),
                    "friday": int(row[6]),
                    "saturday": int(row[7]),
                    "sunday": int(row[8]),
                }

                total = sum(daily.values())

                reach_percentage = (
                    round(
                        (total / weekly_reviews_per_waiter) * 100,
                        2,
                    )
                    if weekly_reviews_per_waiter is not None
                    and weekly_reviews_per_waiter > 0
                    else None
                )

                waiters.append(
                    {
                        "waiter_id": row[0],
                        "waiter_name": row[1],
                        "daily": daily,
                        "total": total,
                        "reach_percentage": reach_percentage,
                    }
                )

            return {
                "week_start": week_start_date,
                "week_end": week_end_date,
                "weekly_reviews_per_waiter": weekly_reviews_per_waiter,
                "waiters": waiters,
            }

    finally:
        conn.close()
