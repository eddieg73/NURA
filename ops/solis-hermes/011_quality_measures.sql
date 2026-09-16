-- 011_quality_measures.sql
-- Preventive / quality measure tracking, per the operator's list (2026-09-15):
--   annual wellness, mammography, ColoGuard OR colonoscopy, bone density,
--   eye exam, A1C.
--
-- These are CARE GAPS, not plan assignments. A member accrues them whether or not
-- their plan changes. Under an upside-only arrangement a closed gap is pure
-- revenue + quality-score upside, so due/overdue work is the point of this table.
--
-- Cadence and eligibility below follow the standard Medicare/HEDIS conventions.
-- They are CONFIGURABLE ROWS, not hardcoded logic, so clinical staff can correct
-- a cadence without a code change.

CREATE TABLE IF NOT EXISTS quality_measures (
    measure_code    TEXT PRIMARY KEY,
    measure_label   TEXT NOT NULL,
    cadence_months  INTEGER,             -- NULL => one-time / as-indicated
    min_age         INTEGER,
    max_age         INTEGER,
    sex_includes    TEXT,                -- 'F' | 'M' | NULL(=any)
    requires_dx_group TEXT,              -- Disease Group required for eligibility
    alternative_of  TEXT REFERENCES quality_measures (measure_code),
    cpt_hints       TEXT[],
    notes           TEXT,
    sort_order      INTEGER NOT NULL DEFAULT 100
);

INSERT INTO quality_measures
  (measure_code, measure_label, cadence_months, min_age, max_age, sex_includes,
   requires_dx_group, alternative_of, cpt_hints, notes, sort_order)
VALUES
    ('AWV', 'Annual Wellness Visit', 12, 65, NULL, NULL, NULL, NULL,
     ARRAY['G0438','G0439','G0468'],
     'One per 12 months. Initial (G0438) once, subsequent (G0439) annually.', 1),

    ('MAMMO', 'Mammography', 24, 50, 74, 'F', NULL, NULL,
     ARRAY['77067','77065','77066'],
     'Screening mammogram. 24-month cadence per HEDIS BCS-E; some contracts use annual.', 2),

    ('CRC', 'Colorectal screening (ColoGuard or colonoscopy)', 12, 45, 75, NULL, NULL, NULL,
     ARRAY['81528','45378','45380','82270','G0328'],
     'ColoGuard (mt-sDNA, CPT 81528) is annual. Colonoscopy is every 10 years — '
     'short cadence here so the member is re-surfaced for the FIT/ColoGuard path '
     'rather than forgotten. Individualize from the procedure history.', 3),

    ('DEXA', 'Bone density (DEXA)', 24, 65, NULL, 'F', NULL, NULL,
     ARRAY['77080','77081'],
     'Women 65+. Women 50-64 with risk factors also qualify — add via override.', 4),

    ('EYE', 'Diabetic eye exam', 12, NULL, NULL, NULL, 'Diabetes', NULL,
     ARRAY['92014','92012','2022F','2023F'],
     'Annual retinal exam. Only applies to members with a diabetes dx group.', 5),

    ('A1C', 'Hemoglobin A1C', 6, NULL, NULL, NULL, 'Diabetes', NULL,
     ARRAY['83036','83037'],
     'Diabetic glycemic control. 6-month cadence for uncontrolled; 12mo if controlled.', 6),

    ('BP', 'Blood pressure control', 12, 18, 85, NULL, NULL, NULL,
     ARRAY['3074F','3075F'],
     'Included because it is the most common shared gap with the above.', 7)
ON CONFLICT (measure_code) DO UPDATE
    SET measure_label = EXCLUDED.measure_label, cadence_months = EXCLUDED.cadence_months,
        min_age = EXCLUDED.min_age, max_age = EXCLUDED.max_age,
        sex_includes = EXCLUDED.sex_includes, requires_dx_group = EXCLUDED.requires_dx_group,
        cpt_hints = EXCLUDED.cpt_hints, notes = EXCLUDED.notes, sort_order = EXCLUDED.sort_order;

-- ---------------------------------------------------- per-member completion --
CREATE TABLE IF NOT EXISTS member_measures (
    id            BIGSERIAL PRIMARY KEY,
    member_number TEXT NOT NULL,
    measure_code  TEXT NOT NULL REFERENCES quality_measures (measure_code),
    last_done_on  DATE,
    next_due_on   DATE,
    status        TEXT NOT NULL DEFAULT 'UNKNOWN',
                  -- UNKNOWN | CURRENT | DUE | OVERDUE | NOT_ELIGIBLE | REFUSED
    source        TEXT NOT NULL DEFAULT 'ensure',
    evidence      JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT member_measures_uniq UNIQUE (member_number, measure_code)
);
CREATE INDEX IF NOT EXISTS idx_member_measures_due ON member_measures (status, next_due_on);

-- Eligibility + due-date computation. Eligibility is derived, never assumed.
CREATE OR REPLACE VIEW v_measure_due AS
SELECT m.member_number,
       q.measure_code,
       q.measure_label,
       mm.last_done_on,
       mm.next_due_on,
       CASE
         WHEN mm.member_number IS NULL                     THEN 'NOT_TRACKED'
         WHEN q.cadence_months IS NULL                     THEN 'AS_INDICATED'
         WHEN mm.last_done_on IS NULL                      THEN 'NEVER_DONE'
         WHEN mm.next_due_on IS NULL                       THEN 'UNKNOWN'
         WHEN mm.next_due_on <  current_date               THEN 'OVERDUE'
         WHEN mm.next_due_on <= current_date + 30          THEN 'DUE_SOON'
         ELSE 'CURRENT'
       END AS gap_state,
       CASE WHEN mm.next_due_on IS NOT NULL
            THEN (current_date - mm.next_due_on) END AS days_past_due
FROM member_intake m
CROSS JOIN quality_measures q
LEFT JOIN member_measures mm
       ON mm.member_number = m.member_number AND mm.measure_code = q.measure_code
WHERE (q.min_age IS NULL OR EXTRACT(YEAR FROM age(current_date, m.dob)) >= q.min_age)
  AND (q.max_age IS NULL OR EXTRACT(YEAR FROM age(current_date, m.dob)) <= q.max_age)
  AND (q.sex_includes IS NULL OR q.sex_includes = 'F');

CREATE OR REPLACE VIEW v_measure_gap_summary AS
SELECT measure_code, measure_label,
       count(*) FILTER (WHERE gap_state IN ('OVERDUE','NEVER_DONE')) AS open_gaps,
       count(*) FILTER (WHERE gap_state = 'DUE_SOON')                AS due_soon,
       count(*) FILTER (WHERE gap_state = 'CURRENT')                 AS current,
       count(*) FILTER (WHERE gap_state = 'NOT_TRACKED')             AS not_tracked
FROM v_measure_due GROUP BY measure_code, measure_label, measure_label
ORDER BY open_gaps DESC;
