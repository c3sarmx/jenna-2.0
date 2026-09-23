import re
import unicodedata


def _normalize_text(value):
    value = value or ""

    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    )

    return normalized.casefold()


def _name_pattern(name):
    normalized_name = _normalize_text(name)

    escaped_name = re.escape(normalized_name)

    return re.compile(
        rf"(?<!\w){escaped_name}(?!\w)",
        re.IGNORECASE,
    )


def find_waiter_matches(content, waiters):
    normalized_content = _normalize_text(content)

    matches = []

    for waiter in waiters or []:
        waiter_id = waiter["id"]
        waiter_name = waiter["name"]

        if not waiter_name:
            continue

        pattern = _name_pattern(waiter_name)

        if not pattern.search(normalized_content):
            continue

        matches.append(
            {
                "waiter_id": waiter_id,
                "waiter_name": waiter_name,
                "confidence": "high",
                "reason": (
                    "La reseña menciona explícitamente "
                    f"el nombre {waiter_name}."
                ),
            }
        )

    return matches
