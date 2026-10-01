from hashlib import sha256
import re

from psycopg.errors import UniqueViolation


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
    translated_content=None,
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

            else:
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
                    translated_content,
                    published_at,
                    source_url,
                    fingerprint
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
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
                    translated_content,
                    published_at,
                    source_url,
                    fingerprint,
                ),
            )

            evidence = cur.fetchone()
            conn.commit()

            return evidence

    except UniqueViolation:
        conn.rollback()
        raise ValueError(
            "review evidence already exists"
        )
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


def get_review_evidence_page(
    business_id,
    page=1,
    per_page=20,
    status="all",
    search=None,
    date_from=None,
    date_to=None,
):
    page = max(int(page), 1)
    per_page = min(max(int(per_page), 1), 100)
    offset = (page - 1) * per_page

    if status not in ("all", "attributed", "unattributed"):
        raise ValueError("invalid review status")

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            filters = [
                "re.business_id = %s",
            ]
            params = [business_id]

            if date_from:
                filters.append(
                    "re.published_at >= %s::timestamptz"
                )
                params.append(date_from)

            if date_to:
                filters.append(
                    "re.published_at < %s::timestamptz"
                )
                params.append(date_to)

            if search:
                filters.append(
                    """
                    (
                        re.reviewer_name ILIKE %s
                        OR re.content ILIKE %s
                        OR re.translated_content ILIKE %s
                    )
                    """
                )
                search_value = f"%{search}%"
                params.extend([
                    search_value,
                    search_value,
                    search_value,
                ])

            base_where_clause = " AND ".join(filters)

            attribution_exists = """
                EXISTS (
                    SELECT 1
                    FROM review_attributions AS ra
                    WHERE ra.review_evidence_id = re.id
                )
            """

            if status == "attributed":
                filters.append(attribution_exists)
            elif status == "unattributed":
                filters.append(f"NOT {attribution_exists}")

            where_clause = " AND ".join(filters)

            cur.execute(
                f"""
                SELECT COUNT(*)
                FROM review_evidence AS re
                WHERE {where_clause};
                """,
                params,
            )

            total = cur.fetchone()[0]

            cur.execute(
                f"""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (
                        WHERE {attribution_exists}
                    ) AS attributed_total,
                    COUNT(*) FILTER (
                        WHERE NOT {attribution_exists}
                    ) AS unattributed_total
                FROM review_evidence AS re
                WHERE {base_where_clause};
                """,
                params,
            )

            (
                filtered_total,
                attributed_total,
                unattributed_total,
            ) = cur.fetchone()

            cur.execute(
                f"""
                SELECT
                    re.id,
                    re.business_id,
                    re.source,
                    re.external_id,
                    re.reviewer_name,
                    re.rating,
                    re.content,
                    re.published_at,
                    re.source_url,
                    re.fingerprint,
                    re.imported_at,
                    re.translated_content,
                    {attribution_exists} AS has_attribution
                FROM review_evidence AS re
                WHERE {where_clause}
                ORDER BY re.imported_at DESC, re.id DESC
                LIMIT %s
                OFFSET %s;
                """,
                params + [per_page, offset],
            )

            items = cur.fetchall()

            return {
                "items": items,
                "page": page,
                "per_page": per_page,
                "total": total,
                "attributed_total": attributed_total,
                "unattributed_total": unattributed_total,
                "total_pages": (
                    (total + per_page - 1) // per_page
                    if total
                    else 0
                ),
            }

    finally:
        conn.close()


def get_review_evidence_by_business(business_id, date_from=None, date_to=None):
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
                    imported_at,
                    translated_content
                FROM review_evidence
                WHERE business_id = %s
                  AND (%s::timestamptz IS NULL OR published_at >= %s::timestamptz)
                  AND (%s::timestamptz IS NULL OR published_at < %s::timestamptz)
                ORDER BY imported_at DESC, id DESC;
                """,
                (
                    business_id,
                    date_from,
                    date_from,
                    date_to,
                    date_to,
                ),
            )

            return cur.fetchall()

    finally:
        conn.close()
