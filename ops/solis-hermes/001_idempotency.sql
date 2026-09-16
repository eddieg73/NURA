-- ============================================================
-- 001_idempotency.sql  — make re-runs safe (idempotent writes)
-- Applied with: psql -f  (psql parses comments correctly; do NOT hand-split)
-- ============================================================
-- WHY: hcc_opportunities UNIQUE(recommendation_id) defaults to gen_random_uuid(),
-- so it never blocks a duplicate. provider_tasks had no unique constraint at all.
-- Running the loader twice duplicated every row.

ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS idempotency_key TEXT;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS algorithm_version TEXT;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS model_version TEXT;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS evidence JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE raf_scores ADD COLUMN IF NOT EXISTS algorithm_version TEXT;
ALTER TABLE raf_scores ADD COLUMN IF NOT EXISTS tenant_id TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS uq_hcc_opp_business
    ON hcc_opportunities (tenant_id, source, source_record);

CREATE INDEX IF NOT EXISTS idx_hcc_opp_tenant_status
    ON hcc_opportunities (tenant_id, status);

CREATE UNIQUE INDEX IF NOT EXISTS uq_provider_tasks_idem
    ON provider_tasks (idempotency_key) WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_provider_tasks_open
    ON provider_tasks (tenant_id, status) WHERE status = 'OPEN';

CREATE UNIQUE INDEX IF NOT EXISTS uq_member_ident_system_value
    ON member_identifiers (system, value);

CREATE UNIQUE INDEX IF NOT EXISTS uq_members_natural
    ON members (tenant_id, last_name, first_name, dob);

CREATE UNIQUE INDEX IF NOT EXISTS uq_raf_scores_versioned
    ON raf_scores (member_id, model, COALESCE(algorithm_version, ''));

CREATE INDEX IF NOT EXISTS idx_audit_events_recent ON audit_events (created_at DESC);
