-- NURA Radiology Intelligence — Data Governance + Model Registry (spec §15, §47)
-- Backs the Knowledge & Dataset Gateway (A2) and the training-governed pipeline.
-- Every image/model must be traceable to its originating dataset, license, and approved use.

CREATE TABLE IF NOT EXISTS dataset_registry (
    dataset_id          TEXT PRIMARY KEY,          -- e.g. 'vindr-cxr', 'mimic-cxr'
    dataset_name        TEXT NOT NULL,
    provider            TEXT,
    version             TEXT,
    release_date        DATE,
    access_class        TEXT,                       -- public | registered | credentialed
    license             TEXT,
    dua_identifier      TEXT,
    approved_use        TEXT,
    prohibited_use      TEXT,
    clinical_domain     TEXT,
    data_format         TEXT,                       -- DICOM | PNG-JPG | NIfTI | FHIR | CSV
    storage_location    TEXT,                       -- b2://nura-datasets/datasets/<name>
    checksum            TEXT,
    imported_at         TIMESTAMPTZ DEFAULT now(),
    reviewed_by         TEXT,
    review_expiration   DATE
);

-- Deny-gate: a workflow may not touch data whose approved_use doesn't permit it.
CREATE OR REPLACE FUNCTION dataset_use_allowed(p_dataset TEXT, p_workflow TEXT)
RETURNS boolean AS $$
  SELECT EXISTS (
    SELECT 1 FROM dataset_registry
    WHERE dataset_id = p_dataset
      AND (approved_use ILIKE '%' || p_workflow || '%' OR approved_use = '*')
  );
$$ LANGUAGE sql STABLE;

CREATE TABLE IF NOT EXISTS dataset_version (
    dataset_id     TEXT REFERENCES dataset_registry(dataset_id),
    version        TEXT,
    dataset_checksum TEXT,
    patient_group  TEXT,        -- adult | pediatric | mixed
    modality       TEXT,        -- CR DX MG US DXA CT MR
    body_region    TEXT,
    task           TEXT,        -- classification | detection | segmentation | report-nlp
    annotation_type TEXT,       -- radiologist_labels | bounding_boxes | segmentation | reports
    source         TEXT,
    split          TEXT,        -- train | validation | internal-test | external-test | safety-test | shift-test
    PRIMARY KEY (dataset_id, version, split)
);

-- Model registry (spec §47). A model is only CLINICALLY_ENABLED after governance.
CREATE TABLE IF NOT EXISTS model_registry (
    model_id          TEXT PRIMARY KEY,
    model_name        TEXT NOT NULL,
    version           TEXT NOT NULL,
    modality          TEXT,          -- XR | MG | US | DXA | CT | MR
    body_region       TEXT,
    task              TEXT,
    architecture      TEXT,          -- densenet121 | swin-unetr | ...
    training_datasets TEXT[],        -- dataset_ids
    dataset_versions  TEXT[],
    training_date     DATE,
    validation_datasets TEXT[],
    external_validation TEXT,
    auroc             NUMERIC,
    auprc             NUMERIC,
    sensitivity       NUMERIC,
    specificity       NUMERIC,
    ppv               NUMERIC,
    npv               NUMERIC,
    calibration       TEXT,
    subgroup_results  JSONB,
    operating_threshold NUMERIC,
    known_limitations TEXT,
    intended_use      TEXT,
    prohibited_use    TEXT,
    model_checksum    TEXT,
    deployment_status TEXT NOT NULL DEFAULT 'RESEARCH',  -- RESEARCH|DEVELOPMENT|VALIDATION|SHADOW_ONLY|CLINICALLY_ENABLED
    approved_by       TEXT,
    approved_at       TIMESTAMPTZ
);

-- Deterministic study router uses (modality, BodyPartExamined, StudyDescription, SeriesDescription)
-- to pick a registered model; if none is approved for that tuple -> ABSTAIN (send to provider).
CREATE TABLE IF NOT EXISTS routing_policy (
    modality      TEXT,
    body_region   TEXT,
    model_id      TEXT REFERENCES model_registry(model_id),
    threshold_version TEXT,
    PRIMARY KEY (modality, body_region)
);
