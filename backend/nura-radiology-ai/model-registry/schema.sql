-- NURA Radiology AI — model registry schema (PostgreSQL 15)
-- Tracks every model, its I/O contract, eval evidence, and the dataset-to-model matrix.

CREATE TABLE IF NOT EXISTS models (
    id               BIGSERIAL PRIMARY KEY,
    name             TEXT NOT NULL,
    slug             TEXT NOT NULL UNIQUE,
    version          TEXT NOT NULL,
    task             TEXT NOT NULL CHECK (task IN
                       ('detection','segmentation','classification','triage','report_generation')),
    modality         TEXT NOT NULL,              -- CT / MR / XR / US / MG / NM
    anatomy          TEXT NOT NULL,              -- chest / brain / breast / full_body / ...
    framework        TEXT,                       -- torchxrayvision / monai / totalsementator / ...
    checkpoint_ref   TEXT,                       -- local path or model-hub URI
    input_contract   JSONB NOT NULL,             -- {"format":"dicom","series":"head","channels":1}
    output_contract  JSONB NOT NULL,             -- {"type":"structured_finding","schema":"ich_v1"}
    status           TEXT NOT NULL DEFAULT 'dev'
                       CHECK (status IN ('dev','staging','prod','retired')),
    fda_clearance    TEXT,                       -- 510(k)/De Novo number, or NULL (research-only)
    intended_use     TEXT NOT NULL DEFAULT 'assistive-triage',
                       -- assistive-triage / assistive-detection / research / ...
    license          TEXT,                       -- model + weights license (commercial_ok?)
    eval_metrics     JSONB,                      -- latest aggregate metrics snapshot
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

-- Audit trail: one row per inference run (source-linked, provider-reviewable).
CREATE TABLE IF NOT EXISTS model_inferences (
    id                  BIGSERIAL PRIMARY KEY,
    model_id            BIGINT REFERENCES models(id),
    study_uid           TEXT NOT NULL,
    series_uid          TEXT,
    input_ref           TEXT,                    -- Orthanc study/series URL or B2 key
    output_ref          TEXT,                    -- DICOM-SR / finding JSON location
    structured_finding  JSONB,                   -- the machine-readable result
    confidence          REAL,
    latency_ms          INTEGER,
    status              TEXT NOT NULL DEFAULT 'completed'
                          CHECK (status IN ('running','completed','failed','reviewed','rejected')),
    created_at          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_inferences_study ON model_inferences(study_uid);
CREATE INDEX IF NOT EXISTS idx_inferences_model ON model_inferences(model_id);

-- Evaluation history: every metric run, kept for re-runnable audits.
CREATE TABLE IF NOT EXISTS model_evaluations (
    id         BIGSERIAL PRIMARY KEY,
    model_id   BIGINT REFERENCES models(id),
    dataset    TEXT NOT NULL,
    metric     TEXT NOT NULL,                    -- AUROC / sensitivity / specificity / Dice ...
    value      REAL NOT NULL,
    run_at     TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_evals_model ON model_evaluations(model_id);

-- Dataset-to-model matrix (the acquisition plan as a table).
CREATE TABLE IF NOT EXISTS dataset_registry (
    id            BIGSERIAL PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,          -- MIMIC-CXR / RSNA-ICH / CheXpert ...
    source        TEXT,                          -- PhysioNet / RSNA / TCIA ...
    modality      TEXT,
    task          TEXT,
    num_studies   INTEGER,
    license       TEXT,
    commercial_ok BOOLEAN NOT NULL DEFAULT false,
    storage       TEXT,                          -- local path / B2 bucket
    annotations   TEXT,                          -- radiologist labels / segmentation / bbox
    intended_use  TEXT NOT NULL DEFAULT 'validation',
                   -- train / validation / both  (research-only sets = validation only)
    notes         TEXT
);

-- Seed the two models we already have installed (status dev — NOT wired to serving yet).
INSERT INTO models (name, slug, version, task, modality, anatomy, framework,
                    input_contract, output_contract, status, intended_use, license)
VALUES
  ('TorchXRayVision CXR Triage', 'torchxrayvision-cxr-triage', '0.1',
   'triage', 'XR', 'chest', 'torchxrayvision',
   '{"format":"dicom","series":"chest-pa-ap","channels":1}',
   '{"type":"structured_finding","schema":"cxr_triage_v1","fields":["normal","abnormal","priority"]}',
   'dev', 'assistive-triage', 'Apache-2.0 (weights: check per model)'),
  ('TotalSegmentator Anatomy', 'totalsegmentator-anatomy', '0.1',
   'segmentation', 'CT', 'full_body', 'totalsegmentator',
   '{"format":"dicom","series":"ct","channels":1}',
   '{"type":"segmentation_masks","schema":"totalsegmentator_v1"}',
   'dev', 'assistive-detection', 'Apache-2.0')
ON CONFLICT (slug) DO NOTHING;
