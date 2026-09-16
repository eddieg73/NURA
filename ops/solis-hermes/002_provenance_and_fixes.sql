-- ============================================================
-- 002_provenance_and_fixes.sql — close the schema/loader mismatch
-- Applied with: psql -f
-- ============================================================
-- FINDING: the repo schema for hcc_opportunities has 16 columns and does NOT
-- include `source` or `source_record`, yet load-mra-csv.py INSERTs into both.
-- That loader threw UndefinedColumn on the FIRST row regardless of connectivity.
-- Provenance is the whole point of this table, so the columns belong here.

ALTER TABLE hcc_opportunities ADD COLUMN IF NOT EXISTS source TEXT;
ALTER TABLE hcc_opportunities ADD COLUMN IF NOT EXISTS source_record TEXT;

-- backfill for any rows already present (none today, but correct for rehearsals)
UPDATE hcc_opportunities SET source = 'UNKNOWN' WHERE source IS NULL;
UPDATE hcc_opportunities SET source_record = 'legacy:' || id WHERE source_record IS NULL;

-- Now the business-key uniqueness that makes re-runs safe
CREATE UNIQUE INDEX IF NOT EXISTS uq_hcc_opp_business
    ON hcc_opportunities (tenant_id, source, source_record);

-- audit_events uses event_time, NOT created_at (the first migration assumed wrong)
DROP INDEX IF EXISTS idx_audit_events_recent;
CREATE INDEX IF NOT EXISTS idx_audit_events_recent ON audit_events (event_time DESC);

-- provider_tasks.reason is where the RAF agent's rationale lands; make sure it's wide enough
ALTER TABLE provider_tasks ALTER COLUMN reason TYPE TEXT;

-- quick health view for verification
CREATE OR REPLACE VIEW v_warehouse_health AS
SELECT 'members'            AS tbl, count(*) AS rows FROM members
UNION ALL SELECT 'member_identifiers', count(*) FROM member_identifiers
UNION ALL SELECT 'hcc_opportunities',  count(*) FROM hcc_opportunities
UNION ALL SELECT 'raf_scores',         count(*) FROM raf_scores
UNION ALL SELECT 'provider_tasks',     count(*) FROM provider_tasks
UNION ALL SELECT 'interventions',      count(*) FROM interventions
UNION ALL SELECT 'source_documents',   count(*) FROM source_documents
UNION ALL SELECT 'transactions',       count(*) FROM transactions;
