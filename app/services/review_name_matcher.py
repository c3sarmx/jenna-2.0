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

    normalized = normalized.casefold()

    return normalized


def _normalize_token(value):
    value = _normalize_text(value)

    value = re.sub(r"['’]s\b", "", value)
    value = re.sub(r"[^a-z0-9]+", "", value)

    return value


def _tokenize(value):
    normalized = _normalize_text(value)

    return [
        _normalize_token(token)
        for token in re.findall(r"[a-z0-9]+", normalized)
        if _normalize_token(token)
    ]


def _singular_forms(token):
    forms = {token}

    if token.endswith("s") and len(token) > 3:
        forms.add(token[:-1])

    return forms


def _levenshtein_distance(left, right):
    if left == right:
        return 0

    if not left:
        return len(right)

    if not right:
        return len(left)

    previous = list(range(len(right) + 1))

    for index_left, char_left in enumerate(left, start=1):
        current = [index_left]

        for index_right, char_right in enumerate(right, start=1):
            insertion = current[index_right - 1] + 1
            deletion = previous[index_right] + 1
            substitution = previous[index_right - 1] + (
                char_left != char_right
            )

            current.append(
                min(
                    insertion,
                    deletion,
                    substitution,
                )
            )

        previous = current

    return previous[-1]


def _is_transposition(candidate, expected):
    if len(candidate) != len(expected):
        return False

    differences = [
        index
        for index, (left, right)
        in enumerate(zip(candidate, expected))
        if left != right
    ]

    if len(differences) != 2:
        return False

    first, second = differences

    return (
        second == first + 1
        and candidate[first] == expected[second]
        and candidate[second] == expected[first]
    )


def _is_close_token(candidate, expected):
    if candidate == expected:
        return True, "exact"

    if candidate in _singular_forms(expected):
        return True, "variant"

    if expected in _singular_forms(candidate):
        return True, "variant"

    distance = _levenshtein_distance(candidate, expected)

    if len(expected) <= 7:
        max_distance = 1
    else:
        max_distance = 2

    if distance <= max_distance:
        # For short names, allow fuzzy matches caused by a missing
        # or extra character. Avoid treating arbitrary substitutions
        # as name variants, since common words can be one edit away
        # from a waiter's name (e.g. "cenar" -> "Cesar").
        if distance == 1:
            length_difference = abs(
                len(candidate) - len(expected)
            )

            if length_difference == 1:
                return True, "fuzzy"

            return False, None

        if distance == 2 and _is_transposition(
            candidate,
            expected,
        ):
            return True, "fuzzy"

        return False, None

    return False, None


def _match_name(waiter_name, content, waiters=None):
    waiter_tokens = _tokenize(waiter_name)
    content_tokens = _tokenize(content)

    if not waiter_tokens or not content_tokens:
        return None

    matched_tokens = 0
    fuzzy_matches = 0
    matched_expected = []
    used_content_indexes = set()

    for expected in waiter_tokens:
        candidates = []

        for index, candidate in enumerate(content_tokens):
            if index in used_content_indexes:
                continue

            matched, match_type = _is_close_token(
                candidate,
                expected,
            )

            if matched:
                priority = {
                    "exact": 0,
                    "variant": 1,
                    "fuzzy": 2,
                }[match_type]

                candidates.append(
                    (
                        priority,
                        index,
                        match_type,
                    )
                )

        if not candidates:
            continue

        _, index, match_type = min(candidates)

        used_content_indexes.add(index)
        matched_tokens += 1
        matched_expected.append(expected)

        if match_type == "fuzzy":
            fuzzy_matches += 1

    if len(waiter_tokens) == 1:
        if matched_tokens != 1:
            return None

        if fuzzy_matches:
            return "medium"

        return "high"

    if matched_tokens == len(waiter_tokens):
        if fuzzy_matches:
            return "medium"

        return "high"

    # Compound names may be written with one component omitted.
    # Only allow this when the matched component is distinctive
    # among the active waiters.
    if matched_tokens == len(waiter_tokens) - 1:
        if not matched_expected:
            return None

        # Do not allow partial matching when a compound name
        # repeats the same component, e.g. "Jose Jose".
        if len(set(waiter_tokens)) != len(waiter_tokens):
            return None

        if not all(len(token) >= 4 for token in matched_expected):
            return None

        other_names = [
            waiter["name"]
            for waiter in waiters or []
            if waiter.get("name") != waiter_name
        ]

        for matched_token in matched_expected:
            for other_name in other_names:
                other_tokens = _tokenize(other_name)

                if matched_token in other_tokens:
                    return None

        return "medium"

    return None


def find_waiter_matches(
    content,
    waiters,
    translated_content=None,
):
    contents = [
        value
        for value in (content, translated_content)
        if value
    ]

    matches = []

    for waiter in waiters or []:
        waiter_id = waiter["id"]
        waiter_name = waiter["name"]

        if not waiter_name:
            continue

        confidences = []

        for candidate_content in contents:
            confidence = _match_name(
                waiter_name,
                candidate_content,
                waiters,
            )

            if confidence is not None:
                confidences.append(confidence)

        if not confidences:
            continue

        if "high" in confidences:
            confidence = "high"
        else:
            confidence = "medium"

        if confidence == "high":
            reason = (
                "La reseña menciona explícitamente "
                f"el nombre {waiter_name}."
            )
        else:
            reason = (
                "La reseña contiene una coincidencia "
                f"probable con el nombre {waiter_name}, "
                "considerando variaciones o una posible "
                "omisión/error de escritura."
            )

        matches.append(
            {
                "waiter_id": waiter_id,
                "waiter_name": waiter_name,
                "confidence": confidence,
                "reason": reason,
            }
        )

    high_matches = [
        match
        for match in matches
        if match["confidence"] == "high"
    ]

    if high_matches:
        filtered_matches = []

        for match in matches:
            if match["confidence"] == "high":
                filtered_matches.append(match)
                continue

            medium_tokens = _tokenize(match["waiter_name"])
            conflicts_with_exact = False

            for high_match in high_matches:
                high_tokens = _tokenize(high_match["waiter_name"])

                if any(
                    _is_close_token(medium_token, high_token)[0]
                    for medium_token in medium_tokens
                    for high_token in high_tokens
                ):
                    conflicts_with_exact = True
                    break

            if not conflicts_with_exact:
                filtered_matches.append(match)

        matches = filtered_matches

    return matches
