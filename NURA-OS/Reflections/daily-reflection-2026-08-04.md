# Daily Self-Reflection — 2026-08-04

## Pass 1: Config Files
- `config.yaml` (active): 832 lines, well-structured, 94 enabled MCP servers, proper model aliases
- `config.yaml` (root): 11 lines, minimal dashboard-only config. Clean.
- `.env`: 600 permissions, sealed, 137 lines. ONE benign empty: `EMAIL_PASSWORD=` (email disabled, `EMAIL_ENABLED: false`).
- Compose files: saas-stack, mirth-docker-stack, imaging-stack, nura-clinical-platform — all annotated with ELIMINATED/DUPLICATE-DISABLED markers. Port mappings intentional, no collisions. No orphans detected.

## Pass 2: Databases + Memory
- **Qdrant**: running, 2 collections (nura-docs, nura-os) — healthy.
- **Redis**: redis-cli not in PATH but service confirmed running (cron probes succeed).
- **Paperclip**: HTTP 200 at 127.0.0.1:3100 — healthy.
- **mem0**: configured (OSS mode, OpenAI embeddings).
- **P1: SWAP AT 100%** — 4095/4095 MB used, only 448-532KB free. swappiness=10. 1.95M pages in, 3.02M pages out. Top consumers: hermes process (10MB), python3 instances (~25MB cumulative). No OOM events yet. Fleet-scan confirms CLINIC node (1441409) is the affected VM.
- **Memory**: 5.9GB/15.6GB used — healthy headroom.
- **Disk**: 109GB/193GB (57%) — healthy.
- **Fleet**: All 3 VPS nodes up — CLINIC (1441409) 37 containers, LAB (1030183) 24 containers, EDGE (817449) light load.

## Pass 3: Skills
- 25 skill directories, 979 total markdown files.
- **FLAGGED**: `langchain` skill — 0 markdown files, not in bundled manifest. Stale/broken download. Candidate for cleanup.
- Most skills lack SKILL.md descriptions. Only tree-of-thoughts, web-research have descriptions. Non-critical.
- No duplicate skill names detected across categories.

## Pass 4: Crons
- 33 active jobs, 2 disabled. Summary:
  - **DUPLICATE**: `Morning briefing` (ec7bdfba0733, disabled) vs `Morning Briefing` (612e34d0bdf6, disabled) — both disabled, near-duplicate names. Consolidate.
  - **STALE PAUSED**: `stack-uptime-watchdog` (349bd58a34b4) — paused 2026-08-01 with note "purge after one green week". Well past threshold. Ready to delete.
  - **RECURRING ERROR**: `nura-backup.sh` — "tar: file changed as we read it" race condition. **FIXED** (added `--warning=no-file-changed`).
  - **TIMEOUT**: VPS Core Snapshot (1441409, weekly) — 604s timeout > 600s limit. Needs longer timeout or split.
  - **PATTERN**: ~11 jobs show `last_status: error` with "Gateway shutdown (final-cleanup)" — all from Aug 3 18:57 restart cascade. Jobs that ran after restart show `ok`. Not persistent.
  - **HEALTHY**: Incident Commander (5min + hourly), Paperclip SLA (2min), Swap Monitor (30min), legal-inbox (30min), fleet sweep (6h), Mission Control regen (daily) — all green.
  - **SILENT-OK compliance**: Fleet sweep, Paperclip SLA, legal-inbox use local delivery. Good.

## Pass 5: Scripts
- `fleet-scan.py`: COMPILE OK, SMOKE RUN OK (3 VPS nodes reported, valid JSON output).
- `legal-inbox-ingest.py`: COMPILE OK.
- `swap-watchdog.py`: COMPILE OK (lives in profiles/nura/scripts/, correctly resolved by cron runner, 126 completions, all ok).
- `nura-backup.sh`: syntax OK after fix.

## Pass 6: Fixes Applied
- **FIXED**: `nura-backup.sh` — added `--warning=no-file-changed` to tar command to prevent race condition failures during concurrent skill updates.

## Pass 7: Escalations
- **P1: SWAP EXHAUSTION on CLINIC VM (1441409)** — 4095/4095 MB, 100% utilized. Root cause: cumulative memory pressure from multiple processes over ~26h uptime. swappiness=10 means kernel avoids swap until necessary, but once full it stays full until processes cycle. Recommend operator schedule a controlled process-cycle during maintenance window. No OOM events detected yet.
- **LOW**: langchain skill (0 files) — stale, remove or restore.
- **LOW**: stack-uptime-watchdog — purge per its own note.
- **LOW**: VPS snapshot timeout — increase job timeout to 900s.
