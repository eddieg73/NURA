-- 014_fix_exception_duplication.sql
-- DEFECT (found 2026-09-15, caught by re-running the daily):
--   plan_exceptions counted 43 after one run and 86 after the next -- EXACTLY
--   doubled. Every subsequent run would add another 43.
--
-- ROOT CAUSE: the uniqueness key included `status`:
--     CONSTRAINT plan_exceptions_uniq UNIQUE (member_number, expected_plan, status)
--   The engine raises an exception as status='OPEN', then step 6 flips it to
--   'TASKED'. On the next run the INSERT ... ON CONFLICT targets
--   (member, plan, 'OPEN'), which no longer exists -- the row is now 'TASKED' --
--   so it inserts a brand-new OPEN row. The guard only ever worked while the
--   row was still OPEN, i.e. for a single run.
--
-- FIX: uniqueness must be on the MEMBER + TARGET PLAN, independent of status.
--   An exception means "this member is off this plan"; that fact does not become
--   untrue because we already raised a task for it. Status is lifecycle, and
--   lifecycle must not participate in identity.
--
-- This is the same class of bug as the provider_tasks insert: identity keyed on
-- mutable state. Both are now fixed.

-- 1. collapse any duplicates the bug already produced, keeping the oldest row
--    (it carries the original detection time) but preferring a non-OPEN status
--    so we do not resurrect already-tasked work.
UPDATE plan_exceptions p
   SET status = 'DISMISSED'
 WHERE p.status = 'OPEN'
   AND EXISTS (SELECT 1 FROM plan_exceptions q
                WHERE q.member_number = p.member_number
                  AND q.expected_plan = p.expected_plan
                  AND q.id < p.id
                  AND q.status IN ('TASKED','RESOLVED','DISMISSED'));

-- 2. drop the bad constraint and put identity on (member, plan)
ALTER TABLE plan_exceptions DROP CONSTRAINT IF EXISTS plan_exceptions_uniq;

CREATE UNIQUE INDEX IF NOT EXISTS uq_plan_exceptions_member_plan
    ON plan_exceptions (member_number, expected_plan);

-- 3. keep the board view honest: one row per member/plan, newest lifecycle state
CREATE OR REPLACE VIEW v_plan_exception_board AS
SELECT e.member_number, e.current_plan, e.expected_plan, e.severity, e.status,
       r.status AS enrollment_status,
       (SELECT count(*) FROM provider_tasks t
         WHERE t.member_number = e.member_number AND t.status = 'OPEN') AS open_tasks
FROM plan_exceptions e
LEFT JOIN enrollment_requests r ON r.exception_id = e.id
WHERE e.status <> 'DISMISSED'
ORDER BY (e.severity = 'HIGH') DESC, e.member_number;

-- 4. SAME DEFECT in enrollment_requests: UNIQUE (member_number, target_plan, status).
--    The request moves PENDING_SIGNATURE -> SIGNED -> SUBMITTED, so each status
--    transition would permit a duplicate row on the next run. Identity again
--    keyed on lifecycle. Key it on the member + target plan instead.
ALTER TABLE enrollment_requests DROP CONSTRAINT IF EXISTS enrollment_requests_uniq;
CREATE UNIQUE INDEX IF NOT EXISTS uq_enrollment_requests_member_plan
    ON enrollment_requests (member_number, target_plan);
