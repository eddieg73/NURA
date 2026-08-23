# PERFORMANCE_PLAN — eddieg73/NURA mesh-monitor hot path

**Target:** `eddieg73/NURA` (`apps/meshtastic-monitor/` and `ops/ems-mesh-monitor/` — near-identical twins; apply to both)
**Related:** `docs/PERFORMANCE_AUDIT.md`
**Status:** AWAITING APPROVAL — no code changed yet.

## Target outcome
Shave the mesh API's worst-case latency and memory on the live EMS lane (the `/api/positions` map endpoint and `/api/export.csv`) with reversible, individually-testable changes. No architecture change. No production behavior change outside of: (a) the positions query getting faster, (b) the CSV export streaming instead of buffering.

## Non-negotiable constraints
- Both monitors must stay wire-compatible with the existing schema and the existing Flask route shapes (clients already consume `/api/*`).
- Index migration must use the existing `IF NOT EXISTS` pattern; running `CREATE INDEX` twice is harmless.
- Do **not** touch the Flutter app, ORION backend, or any ops script outside the two mesh monitors.
- Every batch is gated by the mesh API booting cleanly and the affected endpoint returning valid JSON — run against a temp DB, not the live EMS DB.

## Phase sequence

### Batch 1 — Database index (highest ROI, lowest risk)
- Add `CREATE INDEX IF NOT EXISTS idx_positions_sender_ts ON positions(sender_id, timestamp DESC);` to `init_db.py` in **both** monitors.
- Apply the same migration line to the ems-mesh-monitor if its `init_db` has diverged (confirm first).
- Gate: create a temp sqlite DB, run the migration, `EXPLAIN QUERY PLAN` on the latest-per-node query and confirm it uses the new index (no `SCAN positions`).

### Batch 2 — Stream the CSV export
- In `app.py` (`/api/export.csv`), replace the `StringIO` full-materialize with an incremental writer (cursor + `fetchmany`, or a streaming generator).
- Add a hard `LIMIT` to the export (preserve current behavior for sets under the cap).
- Gate: hit `/api/export.csv` on a padded temp DB and confirm constant-ish memory (check RSS delta) and identical row output.

### Batch 3 — Connection reuse + bounded reads
- Keep one module-level SQLite connection (with `check_same_thread=False` for Flask) or thread-local; drop the per-call connect/close.
- In the listener, batch commits (flush every N packets or every ~1s) instead of per-packet commit.
- Add `LIMIT` defaults to `/api/nodes`, `/api/positions`, and collapse the four `COUNT(*)` in `/api/stats` into one query (or a cached counter).
- Gate: mesh API boots, all endpoints return valid JSON on a temp DB; sustained-packet write path doesn't leak connections (watch fd count).

## Explicit approval gate
Implementation stops here. **Do not edit application code until the user approves a specific batch.**
Recommended if approved to proceed immediately: **Batch 1** (index) — the single highest-ROI, lowest-risk change, and the one with a hard verify (`EXPLAIN QUERY PLAN`).

Options:
1. Approve **Batch 1 only** (index) — safest, largest single win.
2. Approve **Batches 1–3** (full hot-path cleanup).
3. Approve **none** — keep the audit + plan on record, no code change.
4. Repoint scope — audit/plan a different area of the monorepo instead.
