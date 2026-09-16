-- 005_member_diagnoses_and_pull_state.sql
-- The dx_plan_map engine needs somewhere for diagnoses to land, and the daily
-- pull needs a durable record of what ran, when, and whether it worked.
--
-- WHY: `members` has no diagnosis column (verified 2026-09-15), so
-- member_plan_assignment could never be computed. This closes that gap.

-- Per-member diagnosis rows, one per code, with provenance back to the source
-- system that asserted it. Enables the DataMining plan assignment to run.
CREATE TABLE IF NOT EXISTS member_diagnoses (
    id           BIGSERIAL PRIMARY KEY,
    member_number TEXT NOT NULL,
    icd10        TEXT NOT NULL,
    description  TEXT,
    dx_rank      INTEGER,
    source       TEXT NOT NULL,          -- 'solis' | 'carepilot' | 'openemr' | 'emedical'
    source_record TEXT,
    observed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    tenant_id    TEXT,
    CONSTRAINT member_diagnoses_uniq UNIQUE (member_number, icd10, source)
);
CREATE INDEX IF NOT EXISTS idx_member_dx_member ON member_diagnoses (member_number);
CREATE INDEX IF NOT EXISTS idx_member_dx_code   ON member_diagnoses (icd10);

-- One row per (source, run date): did the daily pull work, how many rows, what broke.
CREATE TABLE IF NOT EXISTS pull_runs (
    id            BIGSERIAL PRIMARY KEY,
    source        TEXT NOT NULL,
    run_date      DATE NOT NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at   TIMESTAMPTZ,
    status        TEXT NOT NULL DEFAULT 'RUNNING',  -- RUNNING | OK | PARTIAL | FAILED
    rows_read     INTEGER NOT NULL DEFAULT 0,
    rows_written  INTEGER NOT NULL DEFAULT 0,
    detail        JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT pull_runs_uniq UNIQUE (source, run_date)
);
CREATE INDEX IF NOT EXISTS idx_pull_runs_date ON pull_runs (run_date DESC, source);

-- Convenience view: what does the panel actually look like by plan?
CREATE OR REPLACE VIEW v_panel_by_plan AS
SELECT a.plan,
       count(*)                                        AS members,
       count(*) FILTER (WHERE a.matched_icd10 IS NOT NULL) AS with_dx_match
FROM member_plan_assignment a
GROUP BY a.plan
ORDER BY count(*) DESC;
