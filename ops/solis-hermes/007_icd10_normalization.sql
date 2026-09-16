-- 007_icd10_normalization.sql
-- DEFECT (found 2026-09-15): the plan lookup joined raw ICD-10 strings, but the
-- reference map stores codes WITHOUT dots (E0800) while real claims/EHR data is
-- DOTTED (E11.65). Every lookup therefore missed and every member fell through
-- to REQUIRES_PROVIDER_REVIEW. Bucketing worked; plan assignment silently did not.
--
-- FIX: a canonical normalised key on both sides. Normalisation = uppercase and
-- strip '.' only. That is the standard CMS/ICD-10 canonical form and is lossless
-- for this code set (dots are presentational, never semantic).

ALTER TABLE dx_plan_map ADD COLUMN IF NOT EXISTS icd10_norm TEXT;
UPDATE dx_plan_map
   SET icd10_norm = upper(replace(icd10, '.', ''))
 WHERE icd10_norm IS NULL OR icd10_norm <> upper(replace(icd10, '.', ''));
CREATE INDEX IF NOT EXISTS idx_dx_plan_map_norm ON dx_plan_map (icd10_norm);
CREATE UNIQUE INDEX IF NOT EXISTS uq_dx_plan_map_norm ON dx_plan_map (icd10_norm);
