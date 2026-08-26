CREATE TABLE businesses (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    google_review_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE waiters (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE taps (
    id BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    waiter_id BIGINT REFERENCES waiters(id) ON DELETE SET NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'nfc',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT taps_source_check
        CHECK (source IN ('nfc', 'qr', 'web'))
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

CREATE INDEX idx_waiters_business
    ON waiters(business_id);

CREATE INDEX idx_taps_business
    ON taps(business_id);

CREATE INDEX idx_taps_waiter
    ON taps(waiter_id);

CREATE INDEX idx_taps_created_at
    ON taps(created_at);

CREATE INDEX idx_review_snapshots_business_date
    ON review_snapshots(business_id, snapshot_date);
