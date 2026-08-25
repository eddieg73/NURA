-- Hermes Solis/Ensure integration — core schema (spec sections 25-28)
-- Zone 01 RAW: original payload, immutable. Zone 02 VALIDATED. Zone 03 NORMALIZED. Zone 04 ACTIONABLE.

-- ============ SOURCE DOCUMENTS (Zone 01 — never overwritten) ============
CREATE TABLE IF NOT EXISTS source_documents (
    id BIGSERIAL PRIMARY KEY,
    payer TEXT NOT NULL DEFAULT 'SOLIS',
    source TEXT NOT NULL DEFAULT 'ENSURE',
    transaction_type TEXT NOT NULL,              -- 834, 837P, 837I, 835, RISK, HEDIS, ADT, PHARMACY, ...
    file_name TEXT,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw_payload BYTEA NOT NULL,                  -- original, byte-exact
    payload_sha256 TEXT NOT NULL UNIQUE,         -- dedupe/audit
    content_type TEXT
);

-- ============ TRANSACTION STATE MACHINE (Section 27) ============
CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE,        -- SHA256(payer+member_id+claim_id+service_date+type)
    source_document_id BIGINT REFERENCES source_documents(id),
    state TEXT NOT NULL DEFAULT 'RECEIVED'
        CHECK (state IN ('RECEIVED','VALIDATING','VALIDATED','PROCESSING','PROCESSED',
                         'REJECTED','QUARANTINED','RETRY','MANUAL_REVIEW')),
    version INT NOT NULL DEFAULT 1,
    error_category TEXT,                          -- schema, identity, downstream, timeout, dup
    error_detail TEXT,
    retry_count INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ MEMBERS + IDENTITY (EMPIs) ============
CREATE TABLE IF NOT EXISTS members (
    id BIGSERIAL PRIMARY KEY,
    hermes_patient_id UUID UNIQUE,               -- assigned on first successful identity resolution
    first_name TEXT, last_name TEXT,
    dob DATE, sex TEXT,
    pcp_npi TEXT,
    dual_eligible BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS member_identifiers (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    system TEXT NOT NULL,                        -- SOLIS, MEDICARE, MDFLOW, EMEDICAL
    value TEXT NOT NULL,
    match_confidence TEXT NOT NULL DEFAULT 'exact'
        CHECK (match_confidence IN ('exact','high','medium','manual_review')),
    UNIQUE (system, value)
);

CREATE TABLE IF NOT EXISTS eligibility (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    solis_member_id TEXT, plan_product TEXT,
    effective_date DATE, termination_date DATE,
    status TEXT, risk_population TEXT,
    provider_assignment TEXT,
    source_document_id BIGINT REFERENCES source_documents(id),
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ CLAIMS ============
CREATE TABLE IF NOT EXISTS claims (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    claim_id TEXT NOT NULL, claim_type TEXT,     -- 837P/I/D, 835
    provider_npi TEXT, facility TEXT,
    date_of_service DATE, place_of_service TEXT,
    drg TEXT, admission_date DATE, discharge_date DATE,
    claim_status TEXT,
    paid_amount NUMERIC(14,2), allowed_amount NUMERIC(14,2),
    member_responsibility NUMERIC(14,2),
    source_document_id BIGINT REFERENCES source_documents(id),
    UNIQUE (claim_id, date_of_service)
);
CREATE TABLE IF NOT EXISTS claim_lines (
    id BIGSERIAL PRIMARY KEY,
    claim_id BIGINT REFERENCES claims(id),
    procedure_code TEXT, hcpcs_code TEXT,
    revenue_code TEXT, line_status TEXT
);
CREATE TABLE IF NOT EXISTS diagnoses (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    claim_id BIGINT REFERENCES claims(id),
    icd10_code TEXT, icd10_description TEXT,
    source TEXT,                                 -- CLAIM, EMEDICAL, MDFLOW
    source_record TEXT, service_date DATE
);
CREATE TABLE IF NOT EXISTS procedures (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    claim_id BIGINT REFERENCES claims(id),
    cpt_code TEXT, hcpcs_code TEXT,
    service_date DATE, source TEXT
);

-- ============ RISK / HCC ============
CREATE TABLE IF NOT EXISTS hcc_history (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    hcc_category TEXT, diagnosis TEXT,
    icd10_candidates TEXT[],
    year INT NOT NULL,
    source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hcc_opportunities (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    condition TEXT NOT NULL,
    icd10_candidates TEXT[],
    evidence JSONB NOT NULL DEFAULT '{}',        -- {claims, emr_note, laboratory}
    status TEXT NOT NULL DEFAULT 'REQUIRES_PROVIDER_REVIEW'
        CHECK (status IN ('CONFIRMED','DOCUMENTED','CODED','RECAPTURE REQUIRED','SUSPECTED',
                          'INSUFFICIENT EVIDENCE','RESOLVED','REQUIRES_PROVIDER_REVIEW')),
    confidence NUMERIC(4,3),
    recommendation_id UUID UNIQUE DEFAULT gen_random_uuid(),
    provider_action TEXT, provider_id TEXT,
    decided_at TIMESTAMPTZ,
    algorithm_version TEXT, rule_version TEXT, model_version TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raf_scores (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    model TEXT NOT NULL,                         -- CMS-HCC V22 / V24 / V28 / RxHCC
    current_raf NUMERIC(8,3), projected_raf NUMERIC(8,3),
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ QUALITY ============
CREATE TABLE IF NOT EXISTS hedis_measures (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    measure TEXT NOT NULL, eligible BOOLEAN DEFAULT TRUE,
    numerator_met BOOLEAN DEFAULT FALSE,
    evidence JSONB NOT NULL DEFAULT '[]',
    due_date DATE, recommended_action TEXT,
    status TEXT NOT NULL DEFAULT 'OPEN'
);
CREATE TABLE IF NOT EXISTS care_gaps (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    gap_type TEXT NOT NULL,                      -- HEDIS, AWV, TOC, HCC_RECAPTURE, ...
    status TEXT NOT NULL DEFAULT 'OPEN',
    priority TEXT NOT NULL DEFAULT 'MEDIUM',
    source TEXT NOT NULL DEFAULT 'ENSURE',
    reason TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============ UTILIZATION ============
CREATE TABLE IF NOT EXISTS admissions (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    admission_date DATE, discharge_date DATE,
    facility TEXT, disposition TEXT,
    principal_diagnosis TEXT,
    readmission_of BIGINT REFERENCES admissions(id),  -- 30-day readmission link
    source_document_id BIGINT REFERENCES source_documents(id)
);

-- ============ ACTIONS / WORKFLOWS ============
CREATE TABLE IF NOT EXISTS provider_tasks (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    task_type TEXT NOT NULL,                     -- HCC_REVIEW, HEDIS_GAP, TOC, OUTREACH, ...
    priority TEXT NOT NULL DEFAULT 'MEDIUM',
    payer TEXT NOT NULL DEFAULT 'SOLIS',
    source TEXT NOT NULL DEFAULT 'ENSURE',
    destination TEXT NOT NULL DEFAULT 'MDFLOW',
    reason TEXT, status TEXT NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS interventions (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    task_id BIGINT REFERENCES provider_tasks(id),
    intervention_type TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    completed_at TIMESTAMPTZ
);

-- ============ AUDIT (immutable append) ============
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor TEXT NOT NULL,                          -- system, provider id, agent id
    action TEXT NOT NULL,
    entity_type TEXT, entity_id TEXT,
    correlation_id UUID,
    detail JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_tx_state ON transactions(state);
CREATE INDEX IF NOT EXISTS idx_members_ident ON member_identifiers(system, value);
CREATE INDEX IF NOT EXISTS idx_opp_status ON hcc_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_tasks_open ON provider_tasks(status) WHERE status = 'OPEN';
