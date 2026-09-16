-- TENANCY LAYER — Solis/Hermes multi-tenant (spec §§ 34-40, 46-49 of Phase-6 + Solis spec)
-- Tenant → Facility → User → Patient context. Every transaction resolves tenant.

CREATE TABLE IF NOT EXISTS tenants (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL UNIQUE,            -- e.g. 'solis-msl', 'medisun', 'test-practice'
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',      -- active | suspended | archived
    features JSONB NOT NULL DEFAULT '{}',       -- {nura, imaging, voice, labs, coding...}
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS facilities (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id),
    facility_id TEXT NOT NULL,
    name TEXT,
    UNIQUE (tenant_id, facility_id)
);

-- tenant/facility on every member + every workflow object
ALTER TABLE members ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE members ADD COLUMN IF NOT EXISTS facility_id TEXT;
ALTER TABLE eligibility ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE claims ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE hcc_opportunities ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE hedis_measures ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE care_gaps ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE admissions ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE interventions ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE transactions ADD COLUMN IF NOT EXISTS tenant_id TEXT;
ALTER TABLE source_documents ADD COLUMN IF NOT EXISTS tenant_id TEXT;

-- the only tenant allowed to see its rows: every query filters tenant_id.
CREATE INDEX IF NOT EXISTS idx_members_tenant ON members(tenant_id);
CREATE INDEX IF NOT EXISTS idx_claims_tenant ON claims(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tx_tenant ON transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tasks_tenant ON provider_tasks(tenant_id);

-- tenant-scoped audit trail
ALTER TABLE audit_events ADD COLUMN IF NOT EXISTS tenant_id TEXT;
CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_events(tenant_id);

-- seed: the real tenants we operate
INSERT INTO tenants (tenant_id, name, features) VALUES
  ('solis-msl', 'Solis / Medisun MSO', '{"nura":true,"imaging":true,"coding":true,"hedis":true}'),
  ('nuratech-test', 'NuraTech Synthetic', '{"nura":true,"imaging":false,"coding":true}')
ON CONFLICT (tenant_id) DO NOTHING;
