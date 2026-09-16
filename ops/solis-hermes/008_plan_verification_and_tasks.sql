-- 008_plan_verification_and_tasks.sql
-- OPERATOR REQUIREMENT (2026-09-15):
--   "Must verify what plan the patient is on and then create a task for the
--    patient to be enrolled in the right plan and a task for the provider to
--    sign the form."
--
-- So the engine must do three things, in order:
--   1. VERIFY   what plan the member is CURRENTLY on (from the payer)
--   2. COMPARE  current vs expected -> raise a plan exception when they differ
--   3. TASK     one task to enroll the member on the right plan
--               one task for the PROVIDER TO SIGN the enrollment form
--
-- Governance: nothing here enrolls anyone. Tasks are PROPOSALS. The provider
-- signs, a human submits. Matches the documented safety boundary
-- (no_ai_sign / no_ai_order / no_ai_claim).

-- ---------------------------------------------------- current plan (payer) --
CREATE TABLE IF NOT EXISTS member_plan_current (
    member_number TEXT PRIMARY KEY,
    plan          TEXT,                 -- the product/PBP the payer shows
    pbp_code      TEXT,
    plan_id       TEXT,
    source        TEXT NOT NULL DEFAULT 'ensure',
    verified_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    raw           JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- ------------------------------------------------------------ exceptions --
CREATE TABLE IF NOT EXISTS plan_exceptions (
    id             BIGSERIAL PRIMARY KEY,
    member_number  TEXT NOT NULL,
    current_plan   TEXT,
    expected_plan  TEXT NOT NULL,
    reason         TEXT NOT NULL,
    severity       TEXT NOT NULL DEFAULT 'MEDIUM',   -- HIGH if psych-triggered
    detected_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    status         TEXT NOT NULL DEFAULT 'OPEN',     -- OPEN | TASKED | RESOLVED | DISMISSED
    CONSTRAINT plan_exceptions_uniq UNIQUE (member_number, expected_plan, status)
);
CREATE INDEX IF NOT EXISTS idx_plan_exceptions_status ON plan_exceptions (status, severity);

-- --------------------------------------------------- enrollment forms/reqs --
-- The task pair hangs off one enrollment request per member.
CREATE TABLE IF NOT EXISTS enrollment_requests (
    id             BIGSERIAL PRIMARY KEY,
    member_number  TEXT NOT NULL,
    exception_id   BIGINT REFERENCES plan_exceptions (id) ON DELETE CASCADE,
    target_plan    TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'PENDING_SIGNATURE',
                   -- PENDING_SIGNATURE | SIGNED | SUBMITTED | ENROLLED | REJECTED
    form_ref       TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    signed_by      TEXT,
    signed_at      TIMESTAMPTZ,
    CONSTRAINT enrollment_requests_uniq UNIQUE (member_number, target_plan, status)
);

-- ------------------------------------------------------------- task types --
-- Extend the task vocabulary. provider_tasks already exists (destination
-- defaults to MDFLOW) — these are the two new work items the operator asked for.
CREATE TABLE IF NOT EXISTS task_types (
    task_type   TEXT PRIMARY KEY,
    owner_role   TEXT NOT NULL,     -- who must action it
    requires_signature BOOLEAN NOT NULL DEFAULT false,
    description TEXT NOT NULL
);
INSERT INTO task_types (task_type, owner_role, requires_signature, description) VALUES
    ('PLAN_ENROLL',   'care_manager', false,
     'Enroll the member in the correct plan (member-side action / outreach).'),
    ('PROVIDER_SIGN', 'provider',     true,
     'Provider must review and SIGN the plan enrollment form. AI never signs.'),
    ('PLAN_VERIFY',   'care_manager', false,
     'Verify the plan the member is actually on with the payer before acting.'),
    ('HCC_REVIEW',    'provider',     false, 'Existing RAF/HCC review task.'),
    ('OUTREACH',      'care_manager', false, 'Member outreach.')
ON CONFLICT (task_type) DO UPDATE
    SET owner_role = EXCLUDED.owner_role,
        requires_signature = EXCLUDED.requires_signature,
        description = EXCLUDED.description;

-- Make sure provider_tasks can carry the plan context (additive, nullable).
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS member_number TEXT;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS task_type     TEXT;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS priority      TEXT DEFAULT 'MEDIUM';
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS status        TEXT DEFAULT 'OPEN';
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS payload       JSONB DEFAULT '{}'::jsonb;
ALTER TABLE provider_tasks ADD COLUMN IF NOT EXISTS requires_signature BOOLEAN DEFAULT false;
CREATE INDEX IF NOT EXISTS idx_provider_tasks_member ON provider_tasks (member_number);
CREATE INDEX IF NOT EXISTS idx_provider_tasks_type   ON provider_tasks (task_type, status);

-- Idempotency for tasks: one open task per (member, type, plan).
CREATE UNIQUE INDEX IF NOT EXISTS uq_provider_tasks_open
    ON provider_tasks (member_number, task_type, priority)
    WHERE status IN ('OPEN', 'IN_PROGRESS');

CREATE OR REPLACE VIEW v_plan_exception_board AS
SELECT e.member_number, e.current_plan, e.expected_plan, e.severity, e.status,
       r.status AS enrollment_status,
       (SELECT count(*) FROM provider_tasks t
         WHERE t.member_number = e.member_number AND t.status = 'OPEN') AS open_tasks
FROM plan_exceptions e
LEFT JOIN enrollment_requests r ON r.exception_id = e.id
WHERE e.status <> 'DISMISSED'
ORDER BY (e.severity = 'HIGH') DESC, e.member_number;
