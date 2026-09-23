CREATE TABLE businesses (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    google_review_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE business_users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'owner',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT business_users_role_check
        CHECK (role IN ('owner', 'admin')),

    CONSTRAINT business_users_unique
        UNIQUE (user_id, business_id)
);

CREATE INDEX idx_business_users_user
    ON business_users(user_id);

CREATE INDEX idx_business_users_business
    ON business_users(business_id);

CREATE TABLE waiters (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT waiters_id_business_unique
        UNIQUE (id, business_id)
);

CREATE TABLE cards (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    waiter_id BIGINT NOT NULL REFERENCES waiters(id) ON DELETE RESTRICT,
    public_id VARCHAR(64) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT cards_id_business_unique
        UNIQUE (id, business_id),

    CONSTRAINT cards_waiter_business_fkey
        FOREIGN KEY (waiter_id, business_id)
        REFERENCES waiters(id, business_id)
        ON DELETE RESTRICT
);

CREATE TABLE taps (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    waiter_id BIGINT REFERENCES waiters(id) ON DELETE SET NULL,
    card_id BIGINT REFERENCES cards(id) ON DELETE SET NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'nfc',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT taps_source_check
        CHECK (source IN ('nfc', 'qr', 'web')),

    CONSTRAINT taps_waiter_business_fkey
        FOREIGN KEY (waiter_id, business_id)
        REFERENCES waiters(id, business_id),

    CONSTRAINT taps_card_business_fkey
        FOREIGN KEY (card_id, business_id)
        REFERENCES cards(id, business_id)
);

CREATE TABLE review_snapshots (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    snapshot_date DATE NOT NULL,
    total_reviews INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT review_snapshots_total_check
        CHECK (total_reviews >= 0),

    CONSTRAINT review_snapshots_unique_date
        UNIQUE (business_id, snapshot_date)
);

CREATE INDEX idx_cards_business
    ON cards(business_id);

CREATE INDEX idx_cards_waiter
    ON cards(waiter_id);

CREATE INDEX idx_waiters_business
    ON waiters(business_id);

CREATE TABLE business_settings (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL
        REFERENCES businesses(id) ON DELETE CASCADE,
    weekly_reviews_per_waiter INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT business_settings_unique_business
        UNIQUE (business_id),

    CONSTRAINT business_settings_weekly_reviews_check
        CHECK (
            weekly_reviews_per_waiter IS NULL
            OR weekly_reviews_per_waiter >= 0
        )
);

CREATE INDEX idx_business_settings_business
    ON business_settings(business_id);

CREATE INDEX idx_taps_business
    ON taps(business_id);

CREATE INDEX idx_taps_waiter
    ON taps(waiter_id);

CREATE INDEX idx_taps_created_at
    ON taps(created_at);

CREATE INDEX idx_taps_card
    ON taps(card_id);

CREATE INDEX idx_review_snapshots_business_date
    ON review_snapshots(business_id, snapshot_date);

CREATE TABLE review_evidence (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    source VARCHAR(30) NOT NULL,
    external_id VARCHAR(255),
    reviewer_name VARCHAR(150),
    rating INTEGER,
    content TEXT NOT NULL,
    translated_content TEXT,
    fingerprint VARCHAR(64),
    published_at TIMESTAMPTZ,
    source_url TEXT,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT review_evidence_source_check
        CHECK (
            source IN (
                'manual_import',
                'google_places'
            )
        ),

    CONSTRAINT review_evidence_rating_check
        CHECK (
            rating IS NULL
            OR rating BETWEEN 1 AND 5
        )
);

CREATE INDEX idx_review_evidence_business
    ON review_evidence(business_id);

CREATE INDEX idx_review_evidence_published_at
    ON review_evidence(published_at);

CREATE INDEX idx_review_evidence_fingerprint
    ON review_evidence(business_id, fingerprint);

CREATE UNIQUE INDEX idx_review_evidence_external_unique
    ON review_evidence(business_id, source, external_id)
    WHERE external_id IS NOT NULL;

CREATE TABLE review_attributions (
    id BIGSERIAL PRIMARY KEY,
    review_evidence_id BIGINT NOT NULL
        REFERENCES review_evidence(id) ON DELETE CASCADE,
    waiter_id BIGINT NOT NULL
        REFERENCES waiters(id) ON DELETE CASCADE,
    method VARCHAR(30) NOT NULL,
    confidence VARCHAR(20) NOT NULL,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT review_attributions_method_check
        CHECK (
            method IN (
                'manual',
                'name_match',
                'assisted'
            )
        ),

    CONSTRAINT review_attributions_confidence_check
        CHECK (
            confidence IN (
                'confirmed',
                'high',
                'medium',
                'low'
            )
        ),

    CONSTRAINT review_attributions_unique
        UNIQUE (review_evidence_id, waiter_id)
);

CREATE INDEX idx_review_attributions_review
    ON review_attributions(review_evidence_id);

CREATE INDEX idx_review_attributions_waiter
    ON review_attributions(waiter_id);
