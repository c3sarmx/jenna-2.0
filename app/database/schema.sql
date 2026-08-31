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
