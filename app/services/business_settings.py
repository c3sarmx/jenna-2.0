from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from psycopg.types.json import Jsonb

from app.database.connection import get_connection


_ALLOWED_DAYS = {
    "mon",
    "tue",
    "wed",
    "thu",
    "fri",
    "sat",
    "sun",
}


def _validate_timezone(timezone):
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, TypeError):
        raise ValueError("invalid timezone")


def _validate_time(value):
    if not isinstance(value, str):
        raise ValueError("schedule time must be in HH:MM format")

    try:
        parsed = time.fromisoformat(value)
    except ValueError:
        raise ValueError("schedule time must be in HH:MM format")

    if parsed.second != 0 or parsed.microsecond != 0:
        raise ValueError("schedule time must be in HH:MM format")

    return parsed


def _validate_schedule(schedule):
    if not isinstance(schedule, dict):
        raise ValueError("schedule must be an object")

    unknown_days = set(schedule) - _ALLOWED_DAYS

    if unknown_days:
        raise ValueError("schedule contains invalid day")

    for day, period in schedule.items():
        if period is None:
            continue

        if not isinstance(period, dict):
            raise ValueError("schedule day must be an object or null")

        if set(period) != {"start", "end"}:
            raise ValueError(
                "schedule day must contain start and end"
            )

        start = _validate_time(period["start"])
        end = _validate_time(period["end"])

        if start >= end:
            raise ValueError(
                "schedule start must be before end"
            )


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
                    updated_at,
                    review_sync_enabled,
                    review_sync_interval_minutes,
                    review_sync_timezone,
                    review_sync_schedule,
                    review_sync_last_run_at
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
                    updated_at,
                    review_sync_enabled,
                    review_sync_interval_minutes,
                    review_sync_timezone,
                    review_sync_schedule,
                    review_sync_last_run_at;
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


def set_review_sync_settings(
    business_id,
    enabled,
    interval_minutes,
    timezone,
    schedule,
):
    if not isinstance(enabled, bool):
        raise ValueError("enabled must be a boolean")

    if not isinstance(interval_minutes, int) or isinstance(
        interval_minutes, bool
    ):
        raise ValueError(
            "interval_minutes must be an integer"
        )

    if interval_minutes <= 0:
        raise ValueError(
            "interval_minutes must be greater than 0"
        )

    if not isinstance(timezone, str) or not timezone:
        raise ValueError("invalid timezone")

    _validate_timezone(timezone)
    _validate_schedule(schedule)

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
                    review_sync_enabled,
                    review_sync_interval_minutes,
                    review_sync_timezone,
                    review_sync_schedule
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (business_id)
                DO UPDATE SET
                    review_sync_enabled =
                        EXCLUDED.review_sync_enabled,
                    review_sync_interval_minutes =
                        EXCLUDED.review_sync_interval_minutes,
                    review_sync_timezone =
                        EXCLUDED.review_sync_timezone,
                    review_sync_schedule =
                        EXCLUDED.review_sync_schedule,
                    updated_at = NOW()
                RETURNING
                    id,
                    business_id,
                    weekly_reviews_per_waiter,
                    created_at,
                    updated_at,
                    review_sync_enabled,
                    review_sync_interval_minutes,
                    review_sync_timezone,
                    review_sync_schedule,
                    review_sync_last_run_at;
                """,
                (
                    business_id,
                    enabled,
                    interval_minutes,
                    timezone,
                    Jsonb(schedule),
                ),
            )

            settings = cur.fetchone()
            conn.commit()

            return settings

    finally:
        conn.close()

def mark_review_sync_run(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE business_settings
                SET
                    review_sync_last_run_at = NOW()
                WHERE business_id = %s
                RETURNING review_sync_last_run_at;
                """,
                (business_id,),
            )

            result = cur.fetchone()

            if result is None:
                raise ValueError("business settings not found")

            conn.commit()

            return result[0]

    finally:
        conn.close()
