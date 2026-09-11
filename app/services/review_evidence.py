from hashlib import sha256
import re


def _normalize_fingerprint_text(value):
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value).strip().lower())


def build_review_fingerprint(
    reviewer_name,
    rating,
    content,
    published_at,
):
    normalized_reviewer = _normalize_fingerprint_text(
        reviewer_name
    )

    normalized_rating = (
        ""
        if rating is None
        else str(rating).strip()
    )

    normalized_content = _normalize_fingerprint_text(
        content
    )

    normalized_published_at = (
        ""
        if published_at is None
        else published_at.isoformat()
    )

    payload = "|".join(
        (
            normalized_reviewer,
            normalized_rating,
            normalized_content,
            normalized_published_at,
        )
    )

    return sha256(payload.encode("utf-8")).hexdigest()


from app.database.connection import get_connection


def create_review_evidence(
    business_id,
    source,
    content,
    reviewer_name=None,
    rating=None,
    external_id=None,
    published_at=None,
    source_url=None,
):
    fingerprint = build_review_fingerprint(
        reviewer_name=reviewer_name,
        rating=rating,
        content=content,
        published_at=published_at,
    )

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            if external_id is not None:
                cur.execute(
                    """
                    SELECT
                        id
                    FROM review_evidence
                    WHERE business_id = %s
                      AND external_id = %s
                    ORDER BY id ASC
                    LIMIT 1;
                    """,
                    (business_id, external_id),
                )

                if cur.fetchone():
                    raise ValueError(
                        "review evidence already exists"
                    )

            cur.execute(
                """
                SELECT
                    id
                FROM review_evidence
                WHERE business_id = %s
                  AND fingerprint = %s
                ORDER BY id ASC
                LIMIT 1;
                """,
                (business_id, fingerprint),
            )

            if cur.fetchone():
                raise ValueError(
                    "review evidence already exists"
                )

            cur.execute(
                """
                INSERT INTO review_evidence (
                    business_id,
                    source,
                    external_id,
                    reviewer_name,
                    rating,
                    content,
                    published_at,
                    source_url,
                    fingerprint
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    business_id,
                    source,
                    external_id,
                    reviewer_name,
                    rating,
                    content,
                    published_at,
                    source_url,
                    fingerprint,
                    imported_at;
                """,
                (
                    business_id,
                    source,
                    external_id,
                    reviewer_name,
                    rating,
                    content,
                    published_at,
                    source_url,
                    fingerprint,
                ),
            )

            evidence = cur.fetchone()
            conn.commit()

            return evidence

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def find_duplicate_review_evidence(
    business_id,
    external_id=None,
    fingerprint=None,
):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            if external_id is not None:
                cur.execute(
                    """
                    SELECT
                        id,
                        business_id,
                        source,
                        external_id,
                        reviewer_name,
                        rating,
                        content,
                        published_at,
                        source_url,
                        fingerprint,
                        imported_at
                    FROM review_evidence
                    WHERE business_id = %s
                      AND external_id = %s
                    ORDER BY id ASC
                    LIMIT 1;
                    """,
                    (business_id, external_id),
                )

                evidence = cur.fetchone()

                if evidence:
                    return "external_id", evidence

            if fingerprint is not None:
                cur.execute(
                    """
                    SELECT
                        id,
                        business_id,
                        source,
                        external_id,
                        reviewer_name,
                        rating,
                        content,
                        published_at,
                        source_url,
                        fingerprint,
                        imported_at
                    FROM review_evidence
                    WHERE business_id = %s
                      AND fingerprint = %s
                    ORDER BY id ASC
                    LIMIT 1;
                    """,
                    (business_id, fingerprint),
                )

                evidence = cur.fetchone()

                if evidence:
                    return "fingerprint", evidence

            return None

    finally:
        conn.close()


def get_review_evidence_by_business(business_id):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    business_id,
                    source,
                    external_id,
                    reviewer_name,
                    rating,
                    content,
                    published_at,
                    source_url,
                    fingerprint,
                    imported_at
                FROM review_evidence
                WHERE business_id = %s
                ORDER BY imported_at DESC, id DESC;
                """,
                (business_id,),
            )

            return cur.fetchall()

    finally:
        conn.close()
