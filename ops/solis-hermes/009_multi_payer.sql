-- 009_multi_payer.sql
-- Multi-payer support + the payer dropdown the operator asked for.
--
-- OPERATOR REQUIREMENT (2026-09-15):
--   "If a patient had a qualifying diagnosis place the patient in the right health
--    plan with Solis and same for Oscar when I add the pool of patients.
--    Create a drop down to select from Solis, Oscar, Medicare, Dual."
--
-- KEY DESIGN FACT: qualifying-diagnosis logic is PAYER-SCOPED, not global.
--   Solis  (H0982) offers HMO + C-SNP + D-SNP  -> C-SNP chronic dx CHANGES the plan
--   Oscar  (FL)    offers HMO + D-SNP only     -> no C-SNP, so chronic dx does NOT
--   Medicare (FFS) no plan product at all      -> no plan assignment
--   Dual           Medicare + Medicaid         -> routes to D-SNP
-- Assigning the same plan to a member regardless of payer would be WRONG.

-- ------------------------------------------------------------------ payers --
CREATE TABLE IF NOT EXISTS payers (
    payer_code   TEXT PRIMARY KEY,
    payer_label  TEXT NOT NULL,          -- the dropdown text
    payer_type   TEXT NOT NULL,          -- MA | MA_DUAL | FFS
    offers_csnp  BOOLEAN NOT NULL DEFAULT false,
    offers_dsnp  BOOLEAN NOT NULL DEFAULT false,
    portal       TEXT,
    notes        TEXT,
    sort_order   INTEGER NOT NULL DEFAULT 100
);

INSERT INTO payers (payer_code, payer_label, payer_type, offers_csnp, offers_dsnp, portal, notes, sort_order)
VALUES
    ('SOLIS', 'Solis', 'MA', true, true, 'solis.ensuredatasolutions.com',
     'Solis Health Plans, CMS H0982. HMO + Wellness C-SNP + Guardian D-SNP + Balanced. '
     'Contract includes a delegated-entity group (MEDISUN 62 MEDICAL CENTER LLC_SolisOrg).', 1),

    ('OSCAR', 'Oscar', 'MA', false, true, 'hioscar.com',
     'Oscar Health Maintenance Organization of Florida / Managed Care of South Florida. '
     'FL product set is HMO + D-SNP. NO C-SNP, so a chronic qualifying dx does not '
     'reclassify the member the way it does under Solis.', 2),

    ('MEDICARE', 'Medicare', 'FFS', false, false, 'medicare.gov',
     'Original Medicare (Parts A/B) fee-for-service. No plan product to assign; '
     'documentation and RAF work still apply.', 3),

    ('DUAL', 'Dual', 'MA_DUAL', true, true, NULL,
     'Dual-eligible: Medicare + Medicaid. Routes to the payer D-SNP product '
     '(Solis Guardian, or the Oscar D-SNP equivalent).', 4)
ON CONFLICT (payer_code) DO UPDATE
    SET payer_label = EXCLUDED.payer_label, payer_type = EXCLUDED.payer_type,
        offers_csnp = EXCLUDED.offers_csnp, offers_dsnp = EXCLUDED.offers_dsnp,
        portal = EXCLUDED.portal, notes = EXCLUDED.notes, sort_order = EXCLUDED.sort_order;

-- --------------------------------------------------------- payer plan catalog --
CREATE TABLE IF NOT EXISTS payer_plans (
    payer_code   TEXT NOT NULL REFERENCES payers (payer_code) ON DELETE CASCADE,
    plan_code    TEXT NOT NULL,
    plan_label   TEXT NOT NULL,
    plan_type    TEXT NOT NULL,          -- HMO | C-SNP | D-SNP | FFS
    pbp_prefixes TEXT[],
    is_csnp      BOOLEAN NOT NULL DEFAULT false,
    is_dsnp      BOOLEAN NOT NULL DEFAULT false,
    PRIMARY KEY (payer_code, plan_code)
);

INSERT INTO payer_plans (payer_code, plan_code, plan_label, plan_type, pbp_prefixes, is_csnp, is_dsnp) VALUES
    ('SOLIS', 'Balanced',      'Solis Balanced Plan',            'HMO',   ARRAY['H0982-027'],                    false, false),
    ('SOLIS', 'HealthyLiving', 'Solis Healthy Living Plan (HMO)','HMO',   ARRAY['H0982-007','H0982-022','H0982-024'], false, false),
    ('SOLIS', 'Wellness',      'Solis Wellness Plan (HMO C-SNP)','C-SNP', ARRAY['H0982-008','H0982-016','H0982-017','H0982-018','H0982-019'], true, false),
    ('SOLIS', 'WellnessGB',    'Solis Wellness Giveback Plan',   'HMO',   ARRAY['H0982-028','H0982-031','H0982-032'], false, false),
    ('SOLIS', 'Guardian',      'Solis Guardian Plan (D-SNP)',    'D-SNP', ARRAY['H0982-002','H0982-010','H0982-012','H0982-013','H0982-023','H0982-025'], false, true),
    ('OSCAR', 'OscarHMO',      'Oscar Medicare Advantage (HMO)', 'HMO',   NULL, false, false),
    ('OSCAR', 'OscarDual',     'Oscar D-SNP',                    'D-SNP', NULL, false, true),
    ('MEDICARE', 'OriginalFFS','Original Medicare (Part A/B)',   'FFS',   NULL, false, false)
ON CONFLICT (payer_code, plan_code) DO UPDATE
    SET plan_label = EXCLUDED.plan_label, plan_type = EXCLUDED.plan_type,
        pbp_prefixes = EXCLUDED.pbp_prefixes,
        is_csnp = EXCLUDED.is_csnp, is_dsnp = EXCLUDED.is_dsnp;

-- ------------------------------------------------ payer-scoped dx -> plan -----
-- Same diagnosis can imply a DIFFERENT plan under a different payer, so the rule
-- carries the payer. Precedence low = wins.
CREATE TABLE IF NOT EXISTS payer_dx_plan_rules (
    id           BIGSERIAL PRIMARY KEY,
    payer_code   TEXT NOT NULL REFERENCES payers (payer_code) ON DELETE CASCADE,
    rule_code    TEXT NOT NULL,
    when_group   TEXT NOT NULL,          -- Disease Group from dx_plan_map
    target_plan  TEXT NOT NULL,
    precedence   INTEGER NOT NULL,
    rationale    TEXT NOT NULL,
    CONSTRAINT payer_dx_rules_uniq UNIQUE (payer_code, rule_code)
);

INSERT INTO payer_dx_plan_rules (payer_code, rule_code, when_group, target_plan, precedence, rationale) VALUES
    -- SOLIS: psych trumps all -> Balanced; then cardiac; then diabetes (C-SNP logic)
    ('SOLIS', 'psych_trumps',   'Selected Mental Health',    'Balanced', 1,
     'PSYCH TRUMPS ALL. Forces a plan check; member belongs on the Solis Balanced plan.'),
    ('SOLIS', 'cardiac',        'Selected Cardiovascular',   'Wellness', 2,
     'Cardiac qualifying dx -> Solis Wellness C-SNP.'),
    ('SOLIS', 'heart_failure',  'Heart Failure',             'Wellness', 2,
     'Chronic heart failure is a C-SNP qualifying condition.'),
    ('SOLIS', 'diabetes',       'Diabetes',                  'Wellness', 3,
     'Diabetes is a C-SNP qualifying condition.'),
    -- OSCAR: no C-SNP in Florida. Chronic dx does NOT reclassify; only psych flags review.
    ('OSCAR', 'psych_review',   'Selected Mental Health',    'OscarDual', 1,
     'Oscar FL has NO C-SNP. Psych still forces a plan check; dual LLM/behavioral '
     'needs drive D-SNP evaluation rather than a chronic-condition reclassification.'),
    -- MEDICARE: FFS, nothing to assign
    ('MEDICARE', 'ffs_none',    'Diabetes',                  'OriginalFFS', 9,
     'Fee-for-service: no plan product. Documentation/RAF only.'),
    -- DUAL: any chronic group -> D-SNP
    ('DUAL', 'dual_any',        'Diabetes',                  'Guardian', 1,
     'Dual-eligible routes to the D-SNP product.'),
    ('DUAL', 'dual_psych',      'Selected Mental Health',    'Guardian', 1,
     'Dual-eligible with psychiatric dx -> D-SNP, and psych still trumps for review.')
ON CONFLICT (payer_code, rule_code) DO UPDATE
    SET when_group = EXCLUDED.when_group, target_plan = EXCLUDED.target_plan,
        precedence = EXCLUDED.precedence, rationale = EXCLUDED.rationale;

-- ------------------------------------- member intake (the "pool of patients") --
CREATE TABLE IF NOT EXISTS member_intake (
    id             BIGSERIAL PRIMARY KEY,
    batch_id       UUID NOT NULL DEFAULT gen_random_uuid(),
    payer_code     TEXT NOT NULL REFERENCES payers (payer_code),
    member_number  TEXT,
    first_name     TEXT,
    last_name      TEXT,
    dob            DATE,
    icd10_list     TEXT[],
    expected_plan  TEXT,
    match_basis    TEXT,
    status         TEXT NOT NULL DEFAULT 'RECEIVED',  -- RECEIVED|ASSIGNED|REQUIRES_REVIEW|ERROR
    error          TEXT,
    submitted_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    tenant_id      TEXT
);
CREATE INDEX IF NOT EXISTS idx_member_intake_batch ON member_intake (batch_id);
CREATE INDEX IF NOT EXISTS idx_member_intake_payer ON member_intake (payer_code, status);

CREATE OR REPLACE VIEW v_payer_dropdown AS
SELECT payer_code, payer_label, payer_type, sort_order
FROM payers ORDER BY sort_order;
