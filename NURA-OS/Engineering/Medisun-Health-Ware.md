# Medisun Health-Ware — sovereign clinical edge

Date: 2026-08-28 · Owner: Eddie (founder / medical director) · Operator: Hermes (CTO)
Mirror: Notion board · GitHub: `eddieg73/NURA` → `medisun-health-ware/` · Skill: (route via deployment-ops / mcp-lane-wiring)

## What
The in-house answer to the student/hackathon open-source wearables (Aegis, Friend/OMI, NextBand) —
**but clinical-grade**. Thin ESP32 + open ML + MCP, wrapped in the NURA sovereign clinical layer.
**Source of truth: `medisun-health-ware/README.md` + `SPEC.md` in the NURA monorepo.**

## The doctrine (medical director-signed)
1. Consent-gated identity (enroll requires consent).
2. Emergency-necessity override = safety-cam mode (detection + safety flags, `identity: null`).
3. Never stranger-surveillance (no crowd watchlists / reverse-ID of non-participants).
4. Provider-gated — decision-support only, clinician approves, no autonomous action.
5. PHI boundary — capture stays BAA/clinical; B2=binary, Postgres=state, Hermes=events, Redis=transient.
6. Audit — every enroll/verify/override logged (who/when/why/result).

## Architecture (local capture → sovereign brain → clinical-safe store)
- **Device**: ESP32-S3 (INMP441 mic + MAX30102 HR/SpO2) — thin sensor, never does heavy AI.
- **Bridge** (`bridge/ingest_server.py`, dock :8108): receives frames → sovereign lanes → structured event → audit.
- **Face/Identity** (`:8107`): InsightFace buffalo_l, consent-gated enroll/verify + safety-cam detect.
- **Sovereign AI** (dock Ollama :11435): local STT/LLM, free/offline.
- **Memory**: Qdrant + four-node clock · **Clinical**: FHIR Observation → OpenEMR (API only).
- **Audit**: append-only events.db.

## Status
- **P1 software spine: BUILT + VERIFIED** — bridge ingest path proven (POST /ingest → audit → GET /events,
  HR 72/SpO2 98 + face safety-cam `identity:null`). Clinic identity flow `.sh` live.
- **P2 wearable (firmware)**: skeleton done (firmware/MICROPYTHON.md); real MAX30102 DSP + STT lane = next.
- **P3 clinical wire**: bridge → FHIR → OpenEMR (next).
- **P4 safety-cam/glasses**: gated, capture pane (next).

## Files (mirror of the monorepo)
README.md (master spec) · SPEC.md (architecture) · bridge/ingest_server.py ·
identity/clinical_verify.sh · firmware/MICROPYTHON.md · docs/SAFETY-POLICY.md · mhh-install.sh

## Run
```bash
cd medisun-health-ware && bash mhh-install.sh      # installdeps into .venv
.venv/bin/python bridge/ingest_server.py           # ingest bridge :8108 (background)
./identity/clinical_verify.sh enroll|verify|safety|verify1  # clinic flow (uses :8107 face lane)
```

## Open / next
- Medical director sign-off on docs/SAFETY-POLICY.md before go-live.
- P2: MAX30102 real HR/SpO2 DSP + whisper STT lane + device→bridge.
- P3: FHIR Observation → OpenEMR (sidecar doctrine, API only, provider-gate).
