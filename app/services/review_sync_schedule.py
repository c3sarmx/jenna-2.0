from datetime import datetime
from zoneinfo import ZoneInfo


def is_review_sync_allowed(
    enabled,
    timezone,
    schedule,
    now=None,
):
    if not enabled:
        return False

    local_timezone = ZoneInfo(timezone)

    if now is None:
        now = datetime.now(local_timezone)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=local_timezone)
    else:
        now = now.astimezone(local_timezone)

    day_names = (
        "mon",
        "tue",
        "wed",
        "thu",
        "fri",
        "sat",
        "sun",
    )

    day = day_names[now.weekday()]
    period = schedule.get(day)

    if period is None:
        return False

    current_time = now.strftime("%H:%M")

    return (
        period["start"]
        <= current_time
        < period["end"]
    )


def is_review_sync_due(
    last_run_at,
    interval_minutes,
    timezone,
    now=None,
):
    local_timezone = ZoneInfo(timezone)

    if now is None:
        now = datetime.now(local_timezone)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=local_timezone)
    else:
        now = now.astimezone(local_timezone)

    if last_run_at is None:
        return True

    if last_run_at.tzinfo is None:
        last_run_at = last_run_at.replace(
            tzinfo=local_timezone
        )
    else:
        last_run_at = last_run_at.astimezone(
            local_timezone
        )

    elapsed_seconds = (
        now - last_run_at
    ).total_seconds()

    return elapsed_seconds >= interval_minutes * 60
