# CarePilot — mirror

Population-health / Transition-of-Care platform. Source mirrored from the CarePilot host
(srv1441409 working tree, 2026-09-09) for the Chief of Staff inventory + GitHub source-of-truth.

## Structure
- `mirror/backend/` — FastAPI + RBAC + propose-only safety boundary, 39 capability endpoints,
  HL7 ADT parser (hl7.py), TCM + HMO/IPA lifecycle engine, 41/41 safety tests.
- `mirror/frontend/` — Flutter UI (lib/screens, lib/state, api.dart).
- `mirror/integrations/ensure_reader/` — Ensure/Solis reader (creds from env, never inline).

## Safety
Propose-only everywhere. AI never signs, orders, diagnoses, submits claims, or sends patient
messages; humans approve clinical/coding/billing. No secrets committed (env-file creds only).
