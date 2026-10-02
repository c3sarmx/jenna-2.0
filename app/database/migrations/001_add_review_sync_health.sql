ALTER TABLE business_settings
    ADD COLUMN IF NOT EXISTS review_sync_last_error_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS review_sync_last_error TEXT,
    ADD COLUMN IF NOT EXISTS review_sync_consecutive_failures INTEGER NOT NULL DEFAULT 0;
