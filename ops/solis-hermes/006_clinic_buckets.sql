-- 006_clinic_buckets.sql
-- Clinic buckets + the plan-assignment rules the operator specified 2026-09-15.
--
-- TWO DISTINCT OUTPUTS:
--   1. member_plan_assignment  — which Solis PLAN the member should be on
--   2. member_buckets          — which CLINIC buckets the member belongs to
-- A member has exactly ONE plan, but may sit in MANY buckets.
--
-- OPERATOR RULES (verbatim intent, 2026-09-15):
--   "patients are matched based on qualifying diagnosis per plan"
--   "A psych diagnosis always triggers a plan check and make sure they are on
--    balance. Psych trumps all conditions."
--   buckets: Diabetes, Heart failure, Coumadin, Cardiac, Renal, Behavioral, CHF...
--
-- NOTE ON COUMADIN: warfarin therapy is NOT derivable from ICD-10. It is a
-- MEDICATION bucket. It is modelled here (dx_prefix NULL, source='medication')
-- so it is honestly visible as unpopulated until a med feed exists, rather than
-- being silently faked from diagnosis codes.

-- ------------------------------------------------------------------ buckets --
CREATE TABLE IF NOT EXISTS clinic_buckets (
    bucket_code   TEXT PRIMARY KEY,
    bucket_label  TEXT NOT NULL,
    icd_prefixes  TEXT[],                 -- NULL => not diagnosis-derivable
    depends_on    TEXT NOT NULL DEFAULT 'diagnosis',  -- diagnosis | medication | lab
    plan_if_only  TEXT,                   -- which plan this bucket implies
    notes         TEXT,
    sort_order    INTEGER NOT NULL DEFAULT 100
);

INSERT INTO clinic_buckets
    (bucket_code, bucket_label, icd_prefixes, depends_on, plan_if_only, notes, sort_order)
VALUES
    ('BEHAVIORAL', 'Behavioral', ARRAY['F20','F21','F22','F23','F24','F25','F28','F29',
                                       'F30','F31','F32','F33','F34','F39','F60'],
     'diagnosis', 'Balanced',
     'PSYCH TRUMPS ALL. Any F-code here forces a plan check -> Solis Balanced Plan.', 1),

    ('DIABETES', 'Diabetes', ARRAY['E08','E09','E10','E11','E13'],
     'diagnosis', 'D Snap',
     'C-SNP qualifying: diabetes mellitus.', 2),

    ('HEART_FAILURE', 'Heart failure', ARRAY['I50'],
     'diagnosis', 'C Snap',
     'C-SNP qualifying: chronic heart failure.', 3),

    ('CHF', 'CHF', ARRAY['I50','I11.0','I13.0','I13.2'],
     'diagnosis', 'C Snap',
     'Congestive HF incl. hypertensive heart disease WITH heart failure. '
     'Overlaps HEART_FAILURE by design — CHF is the operational registry name.', 4),

    ('CARDIAC', 'Cardiac', ARRAY['I09','I10','I11','I12','I13','I20','I21','I22','I24','I25',
                                 'I26','I27','I30','I31','I33','I34','I35','I36','I37','I38',
                                 'I40','I42','I43','I44','I45','I46','I47','I48','I49','I50',
                                 'I51','I52','I60','I61','I62','I63','I65','I66','I67','I69',
                                 'I70','I71','I72','I73','I74','I77','I78','I80','I82','I83',
                                 'I85','I86','I87','I89','I95','I96','I97'],
     'diagnosis', 'C Snap',
     'Broad cardiovascular range (C Snap). HEART_FAILURE/CHF are subsets of this.', 5),

    ('RENAL', 'Renal', ARRAY['N17','N18','N19','N25','N26','N28',
                             'I12','I13'],   -- hypertensive CKD
     'diagnosis', NULL,
     'CKD/ESRD/acute renal failure. NOTE: hypertensive CKD (I12/I13) also lands in '
     'CARDIAC — a member can be in both buckets.', 6),

    ('COUMADIN', 'Coumadin', NULL,
     'medication', NULL,
     'ANTICOAGULANT THERAPY (warfarin/Coumadin). NOT diagnosis-derivable — requires a '
     'medication feed. Left unpopulated rather than guessed. Common indications to '
     'cross-check once meds exist: I48 (AFib), I26 (PE), I82 (VTE), M32, Z95.81.',
     7)
ON CONFLICT (bucket_code) DO UPDATE
    SET bucket_label  = EXCLUDED.bucket_label,
        icd_prefixes  = EXCLUDED.icd_prefixes,
        depends_on    = EXCLUDED.depends_on,
        plan_if_only  = EXCLUDED.plan_if_only,
        notes         = EXCLUDED.notes,
        sort_order    = EXCLUDED.sort_order;

-- ---------------------------------------------------------- member -> bucket --
CREATE TABLE IF NOT EXISTS member_buckets (
    member_number TEXT NOT NULL,
    bucket_code   TEXT NOT NULL REFERENCES clinic_buckets (bucket_code) ON DELETE CASCADE,
    matched_icd10 TEXT,
    basis         TEXT NOT NULL DEFAULT 'diagnosis',   -- diagnosis | medication | lab
    computed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (member_number, bucket_code)
);
CREATE INDEX IF NOT EXISTS idx_member_buckets_bucket ON member_buckets (bucket_code);

-- ------------------------------------------------------- plan rule (psych) --
-- Encode the operator's override explicitly so the rule is auditable, not buried
-- in code: psych trumps -> Balanced.
CREATE TABLE IF NOT EXISTS plan_rules (
    rule_id     INTEGER PRIMARY KEY,
    rule_name   TEXT NOT NULL,
    condition   TEXT NOT NULL,
    outcome     TEXT NOT NULL,
    precedence  INTEGER NOT NULL,
    rationale   TEXT NOT NULL
);
INSERT INTO plan_rules (rule_id, rule_name, condition, outcome, precedence, rationale) VALUES
    (1, 'psych_overrides_all',
        'any F20-F39/F60 behavioral dx present',
        'Balanced', 1,
        'Psych trumps all conditions. Always triggers a plan check -> Solis Balanced Plan.'),
    (2, 'cardiac_over_diabetes',
        'cardiac/C-SNP dx present, no behavioral dx',
        'C Snap', 2,
        'Cardiac qualifying condition outranks diabetes.'),
    (3, 'diabetes_only',
        'diabetes dx present, no behavioral or cardiac dx',
        'D Snap', 3,
        'Diabetes assigned only when nothing higher applies.'),
    (4, 'unmapped',
        'no qualifying dx found',
        'REQUIRES_PROVIDER_REVIEW', 99,
        'Never guess a plan. Escalate for human review.')
ON CONFLICT (rule_id) DO UPDATE
    SET rule_name = EXCLUDED.rule_name, condition = EXCLUDED.condition,
        outcome = EXCLUDED.outcome, precedence = EXCLUDED.precedence,
        rationale = EXCLUDED.rationale;

-- Convenience views
CREATE OR REPLACE VIEW v_bucket_rollup AS
SELECT b.bucket_code, b.bucket_label, b.depends_on,
       count(mb.member_number) AS members
FROM clinic_buckets b
LEFT JOIN member_buckets mb ON mb.bucket_code = b.bucket_code
GROUP BY b.bucket_code, b.bucket_label, b.depends_on, b.sort_order
ORDER BY b.sort_order;

CREATE OR REPLACE VIEW v_plan_rollup AS
SELECT plan, count(*) AS members FROM member_plan_assignment GROUP BY plan ORDER BY 2 DESC;
