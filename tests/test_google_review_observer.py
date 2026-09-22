from app.services.google_review_observer import (
    get_new_reviews,
)


def test_returns_all_reviews_when_none_are_known():
    reviews = [
        {"id": "A", "text": "Review A"},
        {"id": "B", "text": "Review B"},
        {"id": "C", "text": "Review C"},
    ]

    result = get_new_reviews(
        reviews,
        known_review_ids=set(),
    )

    assert result == reviews


def test_returns_only_unknown_reviews():
    reviews = [
        {"id": "A", "text": "Review A"},
        {"id": "B", "text": "Review B"},
        {"id": "C", "text": "Review C"},
    ]

    result = get_new_reviews(
        reviews,
        known_review_ids={"A", "B"},
    )

    assert result == [
        {"id": "C", "text": "Review C"},
    ]


def test_order_does_not_matter():
    reviews = [
        {"id": "G"},
        {"id": "F"},
        {"id": "A"},
        {"id": "C"},
        {"id": "B"},
    ]

    result = get_new_reviews(
        reviews,
        known_review_ids={"A", "B", "C", "D", "E", "F", "G"},
    )

    assert result == []


def test_duplicate_reviews_in_same_response_are_returned_once():
    reviews = [
        {"id": "A", "text": "Review A"},
        {"id": "A", "text": "Review A"},
        {"id": "B", "text": "Review B"},
    ]

    result = get_new_reviews(
        reviews,
        known_review_ids=set(),
    )

    assert result == [
        {"id": "A", "text": "Review A"},
        {"id": "B", "text": "Review B"},
    ]


def test_reviews_without_id_are_ignored():
    reviews = [
        {"text": "No ID"},
        {},
        {"id": None, "text": "Null ID"},
        {"id": "A", "text": "Valid review"},
    ]

    result = get_new_reviews(
        reviews,
        known_review_ids=set(),
    )

    assert result == [
        {"id": "A", "text": "Valid review"},
    ]


def test_empty_input_returns_empty_list():
    assert get_new_reviews([], set()) == []
    assert get_new_reviews(None, None) == []
