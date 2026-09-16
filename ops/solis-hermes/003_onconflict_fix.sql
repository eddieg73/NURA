-- ============================================================
-- 003_onconflict_fix.sql — make ON CONFLICT legal
-- Applied with: psql -f
-- ============================================================
-- FAILURE: "there is no unique or exclusion constraint matching the ON CONFLICT
-- specification"
--
-- CAUSE 1 (raf_scores): the unique index was on an EXPRESSION
--   (member_id, model, COALESCE(algorithm_version, ''))
--   ON CONFLICT cannot infer an expression index reliably. Fix: a PLAIN unique
--   index on the real columns, and the writer must never insert NULL there.
--   nura_raf_store.py always supplies algorithm_version, so this is safe.
--
-- CAUSE 2 (provider_tasks): the unique index was PARTIAL
--   (idempotency_key) WHERE idempotency_key IS NOT NULL
--   ON CONFLICT with a partial index must repeat the predicate. Simpler and
--   stricter: a full unique index — every task we write HAS a key.

DROP INDEX IF EXISTS uq_raf_scores_versioned;
CREATE UNIQUE INDEX IF NOT EXISTS uq_raf_scores_versioned
    ON raf_scores (member_id, model, algorithm_version);

DROP INDEX IF EXISTS uq_provider_tasks_idem;
CREATE UNIQUE INDEX IF NOT EXISTS uq_provider_tasks_idem
    ON provider_tasks (idempotency_key);

-- guard: algorithm_version must be present for the unique key to work
ALTER TABLE raf_scores ALTER COLUMN algorithm_version SET NOT NULL;
