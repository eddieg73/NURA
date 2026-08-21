# MSO Coder Workspace — Phase 1 (Medicare Advantage MSO Coder Application)

The founder's spec (`skills/health/nura-coding-agent/references/mso-coder-spec.md`)
built as a working Python service. Every output is
**DRAFT — PROVIDER APPROVAL REQUIRED**; the service is read-only toward
production data and accepts PHI-stripped test data only.

## Files
| File | Role |
|---|---|
| `nura_engine.py` | The reuse: imports `../nura-coding-agent.py` via importlib (no copy) and exposes `analyze_chart()` |
| `mso-coder-api.py` | FastAPI service — `POST /review` returns the spec's 4 output sections + queue/audit/health routes |
| `mia.py` | MIA (AI Coder Assistant) — interactive Q&A grounded in the V28 reference + Med42 lane |
| `queue.py` | Priority queue manager — sorts by RAF opportunity / suspected HCCs / unrecaptured flags + metrics counters |
| `sample_chart.json` | PHI-stripped synthetic test chart (72yo DM2 / CKD3b / CHF) |
| `test_phase1.py` | Phase-1 test run (real HTTP against uvicorn) — exit 0 = all checks pass |
- `run.sh` | Launcher (`./run.sh [port]`, default 8643 — 8642 is the Hermes gateway) |

## Run
```bash
cd /opt/data/profiles/nura/scripts/mso-coder
.venv/bin/python -m uvicorn mso-coder-api:app --app-dir . --port 8643   # or ./run.sh
.venv/bin/python test_phase1.py   # the Phase-1 test run
```

## Endpoints
- `POST /review` — chart text + `current_codes`/`prior_year_codes` →
  `diagnosis_recommendations` (ICD-10 + HCC + confidence + evidence),
  `raf_impact` (before/after/delta + interactions + unrecaptured + suspected),
  `compliance_validation` (MEAT per recommendation), `audit_record`
  (timestamps, original vs recommended, RAF changes).
- `POST /mia/ask` — MIA Q&A (`GET /mia/` lists the spec's 3 example queries).
- `POST /queue/submit`, `GET /queue`, `GET /queue/metrics` — priority queue.
- `GET /audit` — in-memory audit trail summaries (no chart text retained).
- `GET /health` — engine + reference + Ollama lane status.

## Doctrine / constraints
- Decision support only — never invents diagnoses; meds/labs/problem lists
  are clues, never proof.
- DRAFT + provider-approval label on every output; RAF values are reference
  estimates (verify against current CMS before payment decisions).
- No production writes: queue + audit are in-memory only; no
  OpenEMR/Perfex/CarePilot calls; PHI screen rejects SSN/phone/MRN/email
  patterns with HTTP 422.
- Phase-1 simplifications (labeled in output): one RAF per HCC group (max
  coefficient); full V28 hierarchy/count-bonus logic, the CarePilot dashboard
  integration, and the Solis pipeline scale-out are V2.
