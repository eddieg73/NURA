# PERFORMANCE_AUDIT — eddieg73/NURA monorepo

**Date:** 2026-08-23
**Target repo:** `eddieg73/NURA` — working copy at `/opt/data/nura_medical` (branch `master`)
**Auditor:** Hermes (CTO lane)
**Status:** AUDIT COMPLETE — no application code changed (approval gate respected)

## Executive summary

The monorepo is healthy and close to Github state (only untracked `orion/` dir; `git fetch` was blocked by SSH key denial — the working copy is the authoritative local mirror, but I could not verify push/fetch drift against the remote live). The pipeline owns a handful of real, measurable performance bottlenecks. They are **not** in the Flutter app or the ORION backend (much of that is scaffolded simulation); they are concentrated in the **live SQLite hot-path of the mesh monitors** — the code that is actually running in production on the EMS mesh today.

Four findings are actionable, reversible, and each independently verifiable. No architecture change required. Highest ROI is a single composite DB index.

## Evidence & baseline

Repo inventory (source only, excl. `.git`, `build`, `.venv`, `.dart_tool`, `node_modules`):
- `apps/` 19 files, `orion/backend/` 12 files, `ops/` 109 files, `infra/scripts/` 15 files.
- Largest ops payloads: `nura-coding-agent.py` (50 KB), `emed-gap-audit.py` (34 KB), `mso-coder` bundle (~60 KB).

Live processes: `python3 /opt/data/meshtastic-monitor/app.py` (PID 2880) — the mesh API is running.
The mesh SQLite DB is on the remote EMS box, not on this host; row counts could not be measured locally (no `/data/*.db` here). Findings are code-path driven and confirmed by reading the code; impact sizing is estimated, not measured against a live DB.

## Findings by layer

### Database (SQLite — `apps/meshtastic-monitor`, `ops/ems-mesh-monitor`)

**D-1 [P1] Unindexed latest-position-per-node query.** `/api/positions` runs a `GROUP BY sender_id` subquery self-joined back to `positions` on every request. `init_db.py` creates `idx_positions_ts` on `timestamp` alone — **no composite `(sender_id, timestamp)` index**. Every request full-scans + sorts `positions` to derive "latest per node."
- Root cause: index does not match the join predicate.
- Impact: grows linearly with positions table size; the map lane (most-fetched) degrades over time.
- Expected gain: query goes from table-scan to index-only lookups. Large. Low risk.
- Fix: `CREATE INDEX IF NOT EXISTS idx_positions_sender_ts ON positions(sender_id, timestamp DESC);` (optionally a window function `ROW_NUMBER() OVER (PARTITION BY sender_id ...)` to remove the self-join).

**D-2 [P1] `/api/export.csv` loads the entire table into memory.** `SELECT * FROM {table}` then builds the CSV in a `StringIO`, no stream, no cap. `packets` grows continuously (every mesh packet). On a busy network this is an OOM / request-block risk and freezes the API for large exports.
- Fix: stream via `cursor.iterflew`/`fetchmany` and write the response incrementally, or cap the export with a limit param.

**D-3 [P2] New SQLite connection per query, and per packet.** `app.py q()` opens→closes a connection on **every** call; `/api/stats` calls `q()` 4 times = 4 connections per request. `listener.py handle_packet()` opens→commits→closes a connection per packet. Under burst load there is no connection reuse.
- Fix: keep a module-level connection (`check_same_thread=False` for Flask) or thread-local; batch commits in the listener (commit every N packets or every 1s).

**D-4 [P2] Unbounded reads + N+1 COUNTs.** `/api/nodes` is `SELECT * FROM nodes ORDER BY last_seen DESC` with no limit; `/api/positions` is unbounded; `/api/stats` runs 4 separate `COUNT(*)` full-scans.
- Fix: add `LIMIT` defaults, and collapse the four counts into one query or a cached counter.

### Application (ORION backend — `orion/backend`)

**A-1 [Documented, not a regression] Sequential simulation chain.** `model_router.route()` sovereign path awaits tiers serially, and `clinical_chain` runs Scribe→Docs→EHR sequentially. These are currently mock implementations (`_call_model` returns hardcoded content) — not a live perf problem yet, but the synchronous escalation pattern will serialize latency when wired to real APIs. Noted for future, not actioned now.

**A-2 [Info] `rate_limit_manager` is sound.** Redis sliding-window, key rotation, cache hashing and `compress_context` are all implemented correctly — no performance defect.

### Frontend (Flutter `apps/nura_medical`)

Not audited at runtime — requires a real build bundle to measure (no `build/app` AOT artifacts evaluated). Excluded per scope; note that a bundle-size / tree-shake pass is a valid future gap, not a current finding.

## Prioritized bottleneck table

| ID | Layer | Issue | Impact | Risk | ROI |
|----|-------|-------|--------|------|-----|
| D-1 | DB | Missing composite `(sender_id, timestamp)` index on `positions` | High | Low | P0/P1 |
| D-2 | API | CSV export loads whole table into memory | Medium-High | Low | P1 |
| D-3 | API | Connection-per-query/per-packet | Medium | Low | P2 |
| D-4 | API | Unbounded reads, N+1 COUNTs | Medium | Low | P2 |

## Metrics to establish before refactor
- `positions` row count and growth rate on the live mesh DB.
- 95th-percentile latency of `/api/positions` and `/api/stats` over a 5-min window (current baseline) before any change.
- Packets/sec during peak mesh activity (for the listener batch-commit sizing).
- `/api/export.csv` peak RSS at max table size.
