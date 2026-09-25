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

def test_matches_plural_like_name_variant():
    waiters = [
        {"id": 1, "name": "Pablo"},
    ]

    matches = find_waiter_matches(
        "Excelente atención de Pablos.",
        waiters,
    )

    assert matches[0]["waiter_id"] == 1
    assert matches[0]["confidence"] == "high"


def test_matches_name_with_apostrophe_variant():
    waiters = [
        {"id": 1, "name": "Pablo"},
    ]

    matches = find_waiter_matches(
        "Pablo's service was excellent.",
        waiters,
    )

    assert matches[0]["waiter_id"] == 1
    assert matches[0]["confidence"] == "high"


def test_matches_small_typo_as_medium_confidence():
    waiters = [
        {"id": 1, "name": "Pablo"},
    ]

    matches = find_waiter_matches(
        "Excelente atención de Pabllo.",
        waiters,
    )

    assert matches[0]["waiter_id"] == 1
    assert matches[0]["confidence"] == "medium"


def test_matches_small_name_typo():
    waiters = [
        {"id": 1, "name": "Aaron"},
    ]

    matches = find_waiter_matches(
        "Aron fue excelente.",
        waiters,
    )

    assert matches[0]["waiter_id"] == 1
    assert matches[0]["confidence"] == "medium"


def test_matches_name_without_accent():
    waiters = [
        {"id": 1, "name": "José"},
    ]

    matches = find_waiter_matches(
        "Excelente servicio de Jose.",
        waiters,
    )

    assert matches[0]["waiter_id"] == 1
    assert matches[0]["confidence"] == "high"


def test_matches_compound_name_with_missing_component():
    waiters = [
        {"id": 1, "name": "Jose Luis"},
    ]

    matches = find_waiter_matches(
        "Excelente servicio de Jose.",
        waiters,
    )

    assert matches[0]["waiter_id"] == 1
    assert matches[0]["confidence"] == "medium"

def test_does_not_match_compound_name_when_short_name_is_another_waiter():
    waiters = [
        {"id": 1, "name": "Jose"},
        {"id": 2, "name": "Jose Luis"},
    ]

    matches = find_waiter_matches(
        "Excelente servicio de Jose.",
        waiters,
    )

    assert matches == [
        {
            "waiter_id": 1,
            "waiter_name": "Jose",
            "confidence": "high",
            "reason": "La reseña menciona explícitamente el nombre Jose.",
        }
    ]


def test_does_not_match_ambiguous_compound_names():
    waiters = [
        {"id": 1, "name": "Jose Luis"},
        {"id": 2, "name": "Jose Antonio"},
    ]

    matches = find_waiter_matches(
        "Excelente servicio de Jose.",
        waiters,
    )

    assert matches == []


def test_does_not_match_unrelated_similar_name():
    waiters = [
        {"id": 1, "name": "Aaron"},
    ]

    matches = find_waiter_matches(
        "Excelente atención de Adrian.",
        waiters,
    )

    assert matches == []

def test_matches_waiter_from_translated_content():
    waiters = [
        {"id": 1, "name": "Pablo"},
    ]

    matches = find_waiter_matches(
        "Excellent service from Pablos.",
        waiters,
        translated_content="Excelente servicio de Pablo.",
    )

    assert matches == [
        {
            "waiter_id": 1,
            "waiter_name": "Pablo",
            "confidence": "high",
            "reason": "La reseña menciona explícitamente el nombre Pablo.",
        }
    ]


def test_translated_content_can_rescue_name_not_found_in_original():
    waiters = [
        {"id": 1, "name": "Pablo"},
    ]

    matches = find_waiter_matches(
        "Great service from the waiter.",
        waiters,
        translated_content="Excelente servicio de Pablo.",
    )

    assert matches[0]["waiter_id"] == 1
    assert matches[0]["confidence"] == "high"

def test_does_not_reuse_same_review_token_for_multiple_name_parts():
    waiters = [
        {"id": 1, "name": "Jose Jose"},
    ]

    matches = find_waiter_matches(
        "Gracias a Jose.",
        waiters,
    )

    assert matches == []
