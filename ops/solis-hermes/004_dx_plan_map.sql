-- 004_dx_plan_map.sql
-- Reference table for the DataMining Diagnosis -> Plan mapping (672 ICD-10 codes).
-- Source of truth: "DataMining DiagnosisPlanMapping.xlsx" supplied by the operator.
-- Plans: D Snap (431) | C Snap (183) | Behavioral (58).
-- Priority hierarchy when a patient carries multiple dx: Behavioral > C Snap > D Snap.
--
-- NOTE: this table holds NO PHI — it is a public-ish code reference (ICD-10 + plan).

CREATE TABLE IF NOT EXISTS dx_plan_map (
    icd10              TEXT PRIMARY KEY,
    icd10_description  TEXT NOT NULL,
    disease_group      TEXT NOT NULL,
    corresponding_plan TEXT NOT NULL,
    source_record      TEXT NOT NULL DEFAULT 'DataMining DiagnosisPlanMapping.xlsx',
    loaded_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dx_plan_map_plan  ON dx_plan_map (corresponding_plan);
CREATE INDEX IF NOT EXISTS idx_dx_plan_map_group ON dx_plan_map (disease_group);

-- Plan priority: lower number wins when a member has multiple qualifying dx.
CREATE TABLE IF NOT EXISTS plan_priority (
    plan         TEXT PRIMARY KEY,
    priority     INTEGER NOT NULL,
    rationale    TEXT NOT NULL
);

INSERT INTO plan_priority (plan, priority, rationale) VALUES
    ('Behavioral', 1, 'Psychiatric dx ALWAYS overrides cardiac and diabetes'),
    ('C Snap',     2, 'Cardiac dx overrides diabetes when no psychiatric dx present'),
    ('D Snap',     3, 'Diabetes assigned only when no psychiatric or cardiac dx present')
ON CONFLICT (plan) DO UPDATE
    SET priority = EXCLUDED.priority, rationale = EXCLUDED.rationale;

-- Member -> plan assignment, derived by applying the priority hierarchy to the
-- member''s diagnosis set. One row per member (a member enrolls in ONE plan).
CREATE TABLE IF NOT EXISTS member_plan_assignment (
    member_number  TEXT PRIMARY KEY,
    plan           TEXT NOT NULL,
    matched_icd10  TEXT,
    match_basis    TEXT,
    computed_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
