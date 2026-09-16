-- 010_upside_only.sql
-- OPERATOR FACT (2026-09-15): "And we are upside only."
--
-- UPSIDE-ONLY means the practice shares in savings/recapture but bears NO downside
-- risk. Consequences that must be explicit in the data model:
--   * a MISSED qualifying diagnosis = pure lost revenue (no offsetting penalty)
--   * a member on the WRONG plan     = pure lost revenue when a richer plan applies
--   * there is NO loss to provision against, so the only question is OPPORTUNITY
-- Reporting therefore quantifies UPSIDE AT RISK, never downside exposure.
--
-- Note: this does not change clinical governance. Upside-only is an economic
-- arrangement, not permission to diagnose. Still propose-only; provider signs.

ALTER TABLE payers ADD COLUMN IF NOT EXISTS risk_arrangement TEXT NOT NULL DEFAULT 'UPSIDE_ONLY';
ALTER TABLE payers ADD COLUMN IF NOT EXISTS downside_pct NUMERIC;
ALTER TABLE payers ADD COLUMN IF NOT EXISTS upside_pct   NUMERIC;

-- Set the stated arrangement for every payer in the dropdown.
UPDATE payers SET risk_arrangement = 'UPSIDE_ONLY' WHERE risk_arrangement IS NULL;

-- Per-plan monthly capitation the practice could capture. Operator-supplied or
-- payer-confirmed values only — NEVER invented. NULL means "unknown, ask".
CREATE TABLE IF NOT EXISTS plan_economics (
    payer_code     TEXT NOT NULL REFERENCES payers (payer_code) ON DELETE CASCADE,
    plan_code      TEXT NOT NULL,
    pmpm           NUMERIC,          -- monthly capitation per member
    raf_multiplier BOOLEAN NOT NULL DEFAULT true,  -- is payment RAF-scaled?
    effective_from DATE,
    source         TEXT NOT NULL DEFAULT 'OPERATOR_PENDING',
    notes          TEXT,
    PRIMARY KEY (payer_code, plan_code)
);

INSERT INTO plan_economics (payer_code, plan_code, pmpm, raf_multiplier, source, notes) VALUES
    ('SOLIS','Wellness',      NULL, true, 'OPERATOR_PENDING',
     'Solis C-SNP capitation. Operator stated $300 PMPM appears on the CarePilot board '
     'as a panel-wide figure — confirm whether that is the C-SNP or HMO rate before use.'),
    ('SOLIS','Balanced',      NULL, true, 'OPERATOR_PENDING', 'Confirm rate.'),
    ('SOLIS','HealthyLiving', NULL, true, 'OPERATOR_PENDING', 'Confirm rate.'),
    ('SOLIS','Guardian',      NULL, true, 'OPERATOR_PENDING', 'Confirm rate.'),
    ('OSCAR','OscarHMO',      NULL, true, 'OPERATOR_PENDING', 'Confirm rate.'),
    ('OSCAR','OscarDual',     NULL, true, 'OPERATOR_PENDING', 'Confirm rate.'),
    ('MEDICARE','OriginalFFS',NULL, true, 'N/A', 'FFS: no capitation. RAF still applies.')
ON CONFLICT (payer_code, plan_code) DO UPDATE
    SET notes = EXCLUDED.notes, source = EXCLUDED.source;

-- ------------------------------------------------------- UPSIDE report views --
-- Upside at risk = members whose qualifying dx maps to a plan they are NOT on.
-- Only meaningful where economics are known; otherwise the COUNT is the exposure.
CREATE OR REPLACE VIEW v_upside_at_risk AS
SELECT e.member_number,
       pc.payer_code,
       e.current_plan,
       e.expected_plan,
       e.severity,
       e.status,
       COALESCE(pe.pmpm, 0)                                    AS target_pmpm,
       COALESCE(pc2.pmpm, 0)                                   AS current_pmpm,
       COALESCE(pe.pmpm, 0) - COALESCE(pc2.pmpm, 0)            AS monthly_uplift,
       (COALESCE(pe.pmpm, 0) - COALESCE(pc2.pmpm, 0)) * 12     AS annual_uplift
FROM plan_exceptions e
LEFT JOIN member_intake pc  ON pc.member_number = e.member_number
LEFT JOIN plan_economics pe  ON pe.plan_code = e.expected_plan
                            AND pe.payer_code = COALESCE(pc.payer_code, 'SOLIS')
LEFT JOIN plan_economics pc2 ON pc2.plan_code = e.current_plan
                            AND pc2.payer_code = COALESCE(pc.payer_code, 'SOLIS')
WHERE e.status IN ('OPEN','TASKED');

-- Rollup: how much upside sits in each bucket, by payer.
CREATE OR REPLACE VIEW v_upside_summary AS
SELECT pc.payer_code,
       count(DISTINCT e.member_number)                                  AS members_off_plan,
       count(*) FILTER (WHERE e.severity = 'HIGH')                      AS high_severity,
       sum(COALESCE(pe.pmpm,0) - COALESCE(pc2.pmpm,0))                  AS monthly_uplift,
       sum((COALESCE(pe.pmpm,0) - COALESCE(pc2.pmpm,0)) * 12)           AS annual_uplift,
       bool_or(pe.pmpm IS NULL)                                         AS economics_incomplete
FROM plan_exceptions e
LEFT JOIN member_intake pc  ON pc.member_number = e.member_number
LEFT JOIN plan_economics pe  ON pe.plan_code = e.expected_plan
                            AND pe.payer_code = COALESCE(pc.payer_code,'SOLIS')
LEFT JOIN plan_economics pc2 ON pc2.plan_code = e.current_plan
                            AND pc2.payer_code = COALESCE(pc.payer_code,'SOLIS')
WHERE e.status IN ('OPEN','TASKED')
GROUP BY pc.payer_code ORDER BY members_off_plan DESC;
