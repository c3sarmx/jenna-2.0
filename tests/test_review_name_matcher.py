from app.services.review_name_matcher import find_waiter_matches


def test_matches_waiter_name_case_insensitively():
    waiters = [
        {"id": 1, "name": "Aaron"},
        {"id": 2, "name": "César"},
    ]

    matches = find_waiter_matches(
        "Excelente atención de cesar.",
        waiters,
    )

    assert matches == [
        {
            "waiter_id": 2,
            "waiter_name": "César",
            "confidence": "high",
            "reason": "La reseña menciona explícitamente el nombre César.",
        }
    ]


def test_matches_names_without_accent():
    waiters = [
        {"id": 1, "name": "César"},
    ]

    matches = find_waiter_matches(
        "Excelente servicio de Cesar.",
        waiters,
    )

    assert matches == [
        {
            "waiter_id": 1,
            "waiter_name": "César",
            "confidence": "high",
            "reason": "La reseña menciona explícitamente el nombre César.",
        }
    ]


def test_matches_multiple_waiters():
    waiters = [
        {"id": 1, "name": "César"},
        {"id": 2, "name": "Aaron"},
    ]

    matches = find_waiter_matches(
        "César y Aaron fueron excelentes.",
        waiters,
    )

    assert matches == [
        {
            "waiter_id": 1,
            "waiter_name": "César",
            "confidence": "high",
            "reason": "La reseña menciona explícitamente el nombre César.",
        },
        {
            "waiter_id": 2,
            "waiter_name": "Aaron",
            "confidence": "high",
            "reason": "La reseña menciona explícitamente el nombre Aaron.",
        },
    ]


def test_does_not_match_substring():
    waiters = [
        {"id": 1, "name": "Ali"},
    ]

    matches = find_waiter_matches(
        "La comida estuvo deliciosa.",
        waiters,
    )

    assert matches == []


def test_returns_no_matches_without_names():
    waiters = [
        {"id": 1, "name": "César"},
        {"id": 2, "name": "Aaron"},
    ]

    matches = find_waiter_matches(
        "Excelente comida y ambiente.",
        waiters,
    )

    assert matches == []


def test_matches_punctuation_around_name():
    waiters = [
        {"id": 1, "name": "Aaron"},
    ]

    matches = find_waiter_matches(
        "¡Gracias, Aaron!",
        waiters,
    )

    assert matches == [
        {
            "waiter_id": 1,
            "waiter_name": "Aaron",
            "confidence": "high",
            "reason": "La reseña menciona explícitamente el nombre Aaron.",
        }
    ]
