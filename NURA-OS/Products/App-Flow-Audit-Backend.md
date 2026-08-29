---
title: App-Flow-Audit-Backend
date: 2026-08-19
tags:
  - nura
  - backend
  - audit
  - api
  - clinical
  - mso-coder
---

# NURA App — Backend Flow Audit (2026-08-19)

**Scope:** The live probe of the backend lanes the ONE app's Clinical screen depends on — the tools API (`:8095`), the MSO Coder API (`:8643`), the coding agent, the OpenEMR MCP, the Orthanc MCP, and the Ollama lane (`:11434`).
**Constraints honored:** Read-only (no backend file changed, no config touched), no patient data in this report (all test inputs synthetic; the OpenEMR probe used a nonexistent synthetic name), no breaking changes. One probe batch (live POST /review against a throwaway instance) was denied by the consent gate and was NOT retried — noted below.

**Verdict up front:** The Clinical screen's three buttons hit one working lane (DX), one lane that always returns an empty case (SYNTHESIS), and one lane that is 100% broken (SCRIBE — a one-line `import` bug). The MSO Coder API's production listener is dead while its process is alive, and the tools-API health check misreports the LLM lane as down when it is up.

---

## 1. Per-endpoint status — Tools API `:8095` (`/opt/data/scripts/nura-tools-api.py`, PID 2887, listening ✓)

| Endpoint | Probe | Status | Note |
|---|---|---|---|
| `GET /health` | 200 `{"status":"ok","tools":["derm","verify","metar","dx","synthesis"],"lanes":{"llm":"down"}}` | ⚠️ MISLEADING | The `llm:down` flag is a **false negative** — root cause found (see §2). The hardcoded `tools` list omits `/scribe`, `/dsh`, `/harness`, `/alexa`. |
| `POST /dx` | bad-body → 400 · OPTIONS → 200 · **real run** (52F dry cough) → ranked differential JSON via Med42 | ✅ WORKS | Full lane verified: local Med42 → structured differential + red flags + workup. DocsGPT grounding falls back gracefully. |
| `POST /synthesis` | bad-body → 400 · OPTIONS → 200 | ❌ BROKEN BY DESIGN | The API pipes the JSON to **stdin**, but `nura-clinical-synthesis.py` only reads `sys.argv[1]` (never passed) → **always synthesizes an empty case** (`{}`). The app's `{'text': ...}` payload doesn't match its schema either. |
| `POST /scribe` | `{}` → 400 "text required" (wiring ✓) · real dictation → `{"note":"[scribe unavailable: name 'urllib' is not defined]"}` | ❌ BROKEN (100%) | Missing module-level `import urllib` — the handler raises `NameError` on every real call; the except string masks it as "unavailable". The Clinical screen's SCRIBE button can never return a note. |
| `POST /derm` | `{}` → 400 "image_path required" | ✅ WIRED | Arg-validation path verified; image run not executed (no image, read-only). |
| `POST /verify` | `{}` → 400 "image_path required" | ✅ WIRED | Same as derm. |
| `GET /metar` | real call → live METARs (KVNC/KFXE/KPIE/KPMP, KTPA VFR) | ✅ WORKS | Aviation lane independent of LLM. |
| `POST /alexa` | `{"text":""}` → 200 "I didn't catch that." · real LLM call → `{"reply":"OK"}` (5.9s) | ✅ WORKS | Proves the in-process Ollama lane is healthy — contradicts the `/health` flag. |
| `GET /dsh` | no goal → 400 "goal param required" | ✅ WIRED | Not part of the Clinical screen flow. |
| `GET /harness` | no goal → 400 "goal param required" | ✅ WIRED | Not part of the Clinical screen flow. |

---

## 2. The root cause the probes uncovered — one missing import

`nura-tools-api.py` imports `json, subprocess, sys` at module level but **never imports `urllib`**. `llm()` imports it locally (so `/alexa` works) and `/dx` shells out to a subprocess (so it works) — but `/health` and `/scribe` use `urllib.` without importing it:

- `/health` → `NameError` swallowed by the bare `except` → `lanes.llm = "down"` **deterministically, forever** — Ollama (`:11434`, 16 models incl. med42/biomistral/qwen2.5:3b) is up and answerable in ~0.01s.
- `/scribe` → `NameError` surfaced as `[scribe unavailable: name 'urllib' is not defined]`.

**Fix (recommended, not applied — read-only constraint):** add `import urllib.request` to the module top of `nura-tools-api.py`. One line; no behavioral risk.

---

## 3. MSO Coder API (`/opt/data/profiles/nura/scripts/mso-coder/`, default port 8643)

| Item | Status | Evidence |
|---|---|---|
| Production process | ⚠️ ALIVE BUT NOT LISTENING | uvicorn PID 89402 running since 01:45, but `:8643` is absent from the socket tables (own namespace checked) → connection refused. Its log shows a healthy burst of 200s (incl. `POST /review 200 OK`) before the listener vanished; no shutdown line, no watchdog, no systemd unit. **Needs a restart.** |
| Code quality | ✅ | FastAPI Phase-1 service; spec-shaped 4-section `/review` payload; PHI screen (422); in-memory audit/queue only; DRAFT doctrine on every section. |
| `/review` behavior | ✅ VERIFIED (historical + code) | `test_output_review.json` (saved from the live run at 01:47) shows the full shape on the synthetic sample chart: 4 recommendations (E11.9→HCC 37/0.166/conf 0.98 · N18.32→HCC 328/0.07 · I50.22→HCC 85/0.323 · I10→no HCC/conf 0.47), per-recommendation MEAT, RAF before/after/delta, unrecaptured/suspected flags, audit record, DRAFT label. Production log line `POST /review 200 OK` corroborates. |
| Fresh boot | ✅ | A throwaway instance on `:8645` booted clean ("Application startup complete") and shut down cleanly after the audit; the live POST /review re-probe against it was **denied by the consent gate and not retried** — the endpoint's correctness stands on the production 200 OK + the saved artifact + the code path. |
| MIA / queue / audit routes | ✅ (code + earlier log 200s) | `/mia/ask`, `/queue/submit`, `/queue`, `/queue/metrics`, `/audit`, `/health` all defined; log shows 200s for each during the 01:47 window. |

---

## 4. Coding agent (`nura-coding-agent.py`) — self-test

`python3 nura-coding-agent.py --self-test --json` → **rc = 0** ✅ (274s, incl. the Med42 pass). Output: candidates (E11.9, N18.32, I50.22), gap prompts ("document E11.22 relationship explicitly"), trap notes (HTN-alone has no HCC), interaction bonus (Diabetes+CHF ~0.121), `status: DRAFT — PROVIDER APPROVAL REQUIRED`, compliance flags read_only/no_emr_writes/provider_approval_required. The MSO coder wraps this engine via importlib (no code copy).

## 5. OpenEMR MCP — reachable ✅

- 20 tools registered in Hermes (patient search, appointments, medications, labs/vitals/questionnaire trends, health trajectory, visit prep, drug-safety flags, FDA labels/FAERS, interactions, eCQM catalog, QRDA parse, providers).
- Live check: `openemr_patient_search("ZZAUDITPROBE-NO-SUCH-PATIENT")` → `[]` (lane responds; zero patient data touched). Watchdog process running (PID 295).

## 6. Orthanc MCP — not wired

`/opt/data/mcp-installs/orthanc/orthanc-mcp.py` exists (REST wrapper, default `127.0.0.1:8042`), but: no Orthanc process listening locally (8042 → HTTP 000) and **the MCP is not registered in Hermes' tool catalog** (no orthanc tools loadable). It needs the Clinic tunnel + MCP registration before the app's imaging flows can exist.

---

## 7. Flow gaps — Clinical screen needs vs. what the API returns

1. **DX schema mismatch (silent garbage-in):** the app POSTs `{'text': ...}`; `/dx` reads `age/sex/presentation/findings/labs`. The pasted text is silently ignored and a default case runs. The app must send the case-schema fields (or `/dx` must accept `text`).
2. **SYNTHESIS is empty regardless of input:** app `{'text': ...}` → API pipes stdin → script reads `argv[1]` only → `{}` synthesized. Two bugs stacked; every SYNTHESIS tap returns a generic empty-case impression.
3. **SCRIBE always fails:** the `urllib` NameError kills the one endpoint whose contract the app already matches. The Scribe tab (and Clinical's SCRIBE button) have no working path today.
4. **Health telemetry is untrustworthy:** `/health` reports `llm:down` while the lane demonstrably serves requests — any dashboard/alert built on it will false-alarm. Same root cause as gap 3.
5. **MSO Coder is down at the socket level:** process alive, listener gone, no watchdog to recover it — the CarePilot-facing `/review` door is closed until a restart (and a watchdog is added).
6. **Device-to-backend routing:** the app targets `http://127.0.0.1:8095` — on a physical phone that's the phone itself. Needs the real gateway URL + HTTPS (iOS ATS) + an auth header. (Carried over from the mobile audit.)
7. **No auth anywhere:** all `:8095` endpoints are open loopback; before any public exposure every endpoint needs a token/attestation.
8. **Health `tools` list is stale:** omits `/scribe` (the most app-relevant lane) — the self-description and the code diverged.

## 8. Integration list (state today)

| Integration | Layer | State |
|---|---|---|
| Ollama `:11434` (16 models incl. med42, biomistral, qwen2.5:3b) | local LLM lane | ✅ up, ~0.01s tags |
| Tools API `:8095` (10 routes) | app backend | ⚠️ up; scribe broken, synthesis empty, health flag wrong |
| MSO Coder API `:8643` | CarePilot/coding workspace | ❌ listener dead, process alive |
| Coding agent (CLI) | engine reuse | ✅ self-test rc=0 |
| OpenEMR MCP (20 tools) | Hermes MCP | ✅ reachable, live query OK |
| OpenEMR (EHR) | via MCP | ✅ behind the MCP (not probed deeper — PHI scope) |
| Orthanc PACS MCP | pending | ❌ not registered + no Clinic tunnel |
| DocsGPT grounding (Clinic `:7091` via SSH) | dx enrichment | fallback-graceful (not a blocker) |
| OpenRouter free lane | LLM fallback | configured (unused in these probes — local lane answered) |

---

## The one-paragraph summary

The backend's shape is healthy but its app-facing surface is half-broken: the tools API on `:8095` is up and three lanes work end-to-end (DX returns a real ranked differential through local Med42, METAR serves live weather, and Alexa proves the in-process Ollama lane is healthy), yet the Clinical screen's SCRIBE button is dead because a missing module-level `import urllib` makes `/scribe` raise a NameError on every real call — the same bug that makes `/health` permanently misreport `llm:down` — and the SYNTHESIS button always returns an empty case because the API pipes JSON to stdin while the script only reads `argv[1]`, on top of the app sending `{'text': ...}` where `/dx` expects a case schema. Outside the API, the MSO Coder's production uvicorn is alive but no longer listening on `:8643` (its log and saved artifact prove `/review` served spec-shaped, DRAFT-labeled recommendations earlier today, and a fresh boot is clean), the coding agent's self-test exits rc=0, the 20-tool OpenEMR MCP answers live queries, and the Orthanc PACS MCP remains unwired pending the Clinic tunnel — so the highest-leverage fixes are one import line, the synthesis stdin/argv mismatch, the app-side DX payload schema, and a restart-plus-watchdog for the MSO Coder, all without touching data or auth posture.

*Audit by the NURA Backend Engineer — read-only, synthetic inputs only, one consent-denied probe not retried.*
