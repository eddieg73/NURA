-- =============================================================================
-- NURA SOVEREIGN WIRING — CREATE-READY SCHEMA  (2026-08-19)
-- Companion to: Products/NURA-Sovereign-Wiring.md  +  Products/NURA-Policy-Matrix.md
--
-- Open-stack only: plain PostgreSQL (runs on the existing paperclip-db or any
-- NURA postgres — the schema `sovereign` is NEW and touches nothing existing).
--
-- Sections:
--   1. THE ONE AUDIT STORE   sovereign.audit_event (append-only, queryable)
--   2. POLICY REGISTRY       sovereign.policy_version + sovereign.role_capability
--   3. CASE-CONTEXT ENGINE   sovereign.case_context + case_document + agent_view_claim
--
-- Idempotent: safe to re-run (CREATE ... IF NOT EXISTS / DO $$ guards).
-- NOTE: this file DEFINES the schema. It does NOT wire enforcement — running it
-- performs no production writes beyond DDL + one reference seed row.
-- =============================================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS sovereign;

-- ---------------------------------------------------------------------------
-- 1. THE ONE AUDIT STORE
--    Every agent action = one row: actor · resource · model · policy · result.
--    Append-only: UPDATE/DELETE are rejected by trigger. The app role gets
--    INSERT + SELECT only (grant pattern at the bottom).
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sovereign.audit_event (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    seq            bigint GENERATED ALWAYS AS IDENTITY,  -- monotonic append order

    -- WHEN
    ts             timestamptz NOT NULL DEFAULT now(),

    -- WHO (the actor)
    actor_type     text NOT NULL,                        -- 'agent' | 'human' | 'system' | 'gateway'
    actor_id       text NOT NULL,                        -- paperclip agent uuid / provider id / lane name
    actor_role     text,                                 -- RBAC role at action time (see role_capability)

    -- WHAT (the resource + action)
    resource_type  text NOT NULL,                        -- 'patient' | 'encounter' | 'document' | 'issue' | 'config'
    resource_id    text NOT NULL,                        -- patient_ref / encounter id / doc id / board issue uuid
    action         text NOT NULL,                        -- 'chart.read' | 'chart.write' | 'coding.candidates' | 'tool.call' ...

    -- WHICH MODEL produced the output
    model_id       text,                                 -- routed model alias (e.g. 'deepseek-v4-pro')
    model_version  text,                                 -- model pin/version when known
    prompt_ref     text,                                 -- prompt/skill version used (optional)

    -- WHICH POLICY was in force
    policy_version text NOT NULL,                        -- FK shape -> sovereign.policy_version(version)
    decision       text NOT NULL,                        -- 'allow' | 'deny' | 'hitl' | 'step-up'
    gate           text,                                 -- which checkpoint decided: 'gateway' | 'supervisory-mcp' | 'openemr' | 'nmi' | 'epcs'

    -- OUTCOME
    result         text,                                 -- 'ok' | 'error' | 'pending-provider'
    phi_scope      text,                                 -- 'none' | 'phi' | 'de-identified'
    payload_sha256 text,                                 -- payload hash (circuit-breaker doctrine)
    session_id     text,                                 -- gateway session / run id
    tenant_id      text,                                 -- mandatory tenant scope (memory-graph doctrine)

    meta           jsonb NOT NULL DEFAULT '{}'::jsonb    -- lane extras (tool_name, mcp_lane, case_id, ...)
);

-- Append-only enforcement: UPDATE/DELETE raise; only INSERTs ever land.
CREATE OR REPLACE FUNCTION sovereign.block_audit_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'sovereign.audit_event is append-only: % not allowed', TG_OP;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'audit_event_append_only') THEN
        CREATE TRIGGER audit_event_append_only
        BEFORE UPDATE OR DELETE ON sovereign.audit_event
        FOR EACH ROW EXECUTE FUNCTION sovereign.block_audit_mutation();
    END IF;
END $$;

-- The query paths the founder asked for:
CREATE INDEX IF NOT EXISTS idx_audit_resource ON sovereign.audit_event (resource_type, resource_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_actor    ON sovereign.audit_event (actor_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_ts       ON sovereign.audit_event (ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_decision ON sovereign.audit_event (decision, ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_meta     ON sovereign.audit_event USING gin (meta);

-- "the who touched what" — one query:
CREATE OR REPLACE VIEW sovereign.v_who_touched_patient AS
SELECT a.resource_id  AS patient_ref,
       a.actor_id,
       a.actor_role,
       a.action,
       a.decision,
       a.model_id,
       a.policy_version,
       a.ts,
       a.result,
       a.session_id
FROM   sovereign.audit_event a
WHERE  a.resource_type = 'patient';

-- "which model produced which output, under which policy":
CREATE OR REPLACE VIEW sovereign.v_model_outputs_by_policy AS
SELECT model_id,
       model_version,
       policy_version,
       action,
       count(*)   AS n,
       max(ts)    AS last_seen
FROM   sovereign.audit_event
GROUP  BY 1, 2, 3, 4;

-- "the agent's daily footprint":
CREATE OR REPLACE VIEW sovereign.v_agent_actions_by_day AS
SELECT actor_id,
       date_trunc('day', ts) AS day,
       action,
       decision,
       count(*)              AS n
FROM   sovereign.audit_event
GROUP  BY 1, 2, 3, 4;

-- Grant pattern (run as owner/superuser when the app role is created):
--   CREATE ROLE sovereign_writer NOLOGIN;
--   GRANT USAGE ON SCHEMA sovereign TO sovereign_writer;
--   GRANT INSERT, SELECT ON sovereign.audit_event TO sovereign_writer;
--   GRANT SELECT ON sovereign.v_who_touched_patient, sovereign.v_model_outputs_by_policy,
--                 sovereign.v_agent_actions_by_day TO sovereign_writer;

-- ---------------------------------------------------------------------------
-- 2. POLICY REGISTRY (versioned — "which policy was in force" is answerable)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sovereign.policy_version (
    version      text PRIMARY KEY,                     -- 'v1.0'
    title        text NOT NULL,
    doc_ref      text,                                 -- 'Products/NURA-Policy-Matrix.md'
    effective_at timestamptz NOT NULL DEFAULT now(),
    supersedes   text REFERENCES sovereign.policy_version(version),
    notes        text
);

-- The matrix itself, row per (role, capability, gate) — mirrors NURA-Policy-Matrix.md:
CREATE TABLE IF NOT EXISTS sovereign.role_capability (
    role           text NOT NULL,   -- founder | clinician | coder_agent | scribe_agent | mia_agent | intake_agent | ops_agent | auditor
    capability     text NOT NULL,   -- chart.read | chart.write | chart.sign | orders.create | rx.prepare |
                                    -- claim.submit | comms.send_phi | data.export_phi | admin.config | audit.read
    gate           text NOT NULL,   -- 'allow' | 'deny' | 'hitl' | 'step-up'
    policy_version text NOT NULL REFERENCES sovereign.policy_version(version),
    note           text,
    PRIMARY KEY (role, capability, policy_version)
);

-- The v1.0 registration row (reference data; the full matrix lives in the vault doc):
INSERT INTO sovereign.policy_version (version, title, doc_ref, notes)
VALUES ('v1.0',
        'NURA RBAC Policy Matrix v1.0',
        'Products/NURA-Policy-Matrix.md',
        'Founder directive 2026-08-19 — the watsonx sovereign wiring. Never-autonomous + step-up lists codified.')
ON CONFLICT (version) DO NOTHING;

-- ---------------------------------------------------------------------------
-- 3. CASE-CONTEXT ENGINE (the structured half — Qdrant holds the vector half)
--    join key between halves: case_document.qdrant_point <-> Qdrant point id
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sovereign.case_context (
    case_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   text NOT NULL,                          -- tenant isolation (memory-graph doctrine)
    patient_ref text NOT NULL,                          -- EMR patient reference (no free-text PHI keyed here)
    status      text NOT NULL DEFAULT 'active',         -- 'active' | 'closed' | 'superseded'
    title       text,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, patient_ref)
);

CREATE TABLE IF NOT EXISTS sovereign.case_document (
    id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id      uuid NOT NULL REFERENCES sovereign.case_context(case_id) ON DELETE CASCADE,
    doc_type     text NOT NULL,   -- note | lab | imaging | claim | fax | referral | prior_auth | coding_candidates
    source_lane  text NOT NULL,   -- ocr-router | lab-intake | openemr-mcp | scribe | coding-agent | mia | ...
    source_ref   text NOT NULL,   -- pointer back to the EMR/lane object (source of truth, never a driftable copy)
    qdrant_point text,            -- Qdrant point id of the vector half (payload mirrors these keys)
    added_by     text NOT NULL,   -- agent id (the audit actor)
    added_at     timestamptz NOT NULL DEFAULT now(),
    UNIQUE (case_id, source_lane, source_ref)
);

-- Who assembled/worked which case at which bundle version (feeds the audit store too):
CREATE TABLE IF NOT EXISTS sovereign.agent_view_claim (
    case_id        uuid NOT NULL REFERENCES sovereign.case_context(case_id) ON DELETE CASCADE,
    agent_id       text NOT NULL,
    claimed_at     timestamptz NOT NULL DEFAULT now(),
    bundle_version text,          -- which assembled bundle the agent worked from (shared-view proof)
    PRIMARY KEY (case_id, agent_id, claimed_at)
);

CREATE INDEX IF NOT EXISTS idx_case_doc_case ON sovereign.case_document (case_id, doc_type);
CREATE INDEX IF NOT EXISTS idx_case_doc_lane ON sovereign.case_document (source_lane, added_at DESC);

COMMIT;

-- =============================================================================
-- SMOKE TEST (docs-verification only — run after the DDL, writes nothing):
--   SELECT count(*) FROM sovereign.audit_event;                          -- 0
--   SELECT version, title, doc_ref FROM sovereign.policy_version;         -- v1.0 seeded
--   INSERT INTO sovereign.audit_event (actor_type, actor_id, resource_type,
--          resource_id, action, policy_version, decision)
--   VALUES ('agent','test-probe','document','smoke','tool.call','v1.0','allow');
--   DELETE FROM sovereign.audit_event WHERE actor_id='test-probe';
--   -- ^ expected: ERROR: sovereign.audit_event is append-only: DELETE not allowed
-- =============================================================================
