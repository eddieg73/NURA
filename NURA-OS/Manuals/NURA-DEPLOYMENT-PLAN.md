# NURA DEPLOYMENT PLAN — phased rollout (2026-08-02)
Sequenced from the Synthetic-Clinician P0–P10 roadmap + our live infrastructure. Audience: board + engineers.

## Phase 0 — Anchor Build (now → 90 days) [P0–P3]
- **Safety + interop**: CDS Hooks, critical-lab alerts, med rec; FHIR R4 + SMART on FHIR; OpenEMR + eMedical adapters FIRST (our EMRs).
- **Voice + AI**: Whisper (Lab/free lanes) + ElevenLabs; SOAP scribe pipeline (DeepSeek/Gemma; Bio_ClinicalBERT entities); model router + swarm live.
- **Dashboards**: Mission Control (Hermes) + 6 clinician dashboards scaffolded in the master app.
- **Board live**: Atlas executing (after gateway-key fix), weekly scrum, agents directive'd.
- **Success gate**: 285-patient Medisun panel fully in the loop (scheduling, scribe, billing, gaps) + NURA Imaging hub (North Miami) on Orthanc/ThaiRIS/OHIF with OpenEMR+Perfex tie-in (NUR-61).

## Phase 1 — Internal Rollout (90–180 days) [P4–P6]
- All agents (pharmacist/coder/consultant/scribe/nurse/receptionist) on internal practices: North Miami + Little Haiti + Ft. Lauderdale clinics.
- CarePilot Phase 2 work queues live (reports → work); Medisun coding buckets in GHL; TCM/RPM/CCM tracking.
- Imaging bundle: MWL + results loop + viewer links in charts; fax (Documo) + comms (Twilio/Firebase) automated.
- **Success gate**: doc time <30 min, chart closure <2h, coding +11%, gap closure per cohort, NPS measured.

## Phase 2 — External Pilots (6–12 months) [P7]
- Adapter registry expansion: Epic/Cerner/eCW/Athena (Mirth channels per EMR; FHIR R4).
- 3–5 pilot practices (aesthetics + small groups + one MA group) — 7-day Hermes trial → paid.
- SaaS division (DIV-1) productizes the bundle; support + onboarding runbook (plug-in adapter → go-live in 2 weeks).
- **Success gate**: 20 paid practices, <3% churn, reference case studies.

## Phase 3 — Scale (12–24 months) [P8–P10]
- Production hardening: latency <500ms, 99.9% SLA, HIPAA audit, FDA 510(k) path, DEA EPCS, CLIA.
- Clinical validation: MIMIC-IV 10K retrospective + RCT; payer/regulatory engagement.
- Launch: 18-EMR coverage; 1K → 10K providers; ARR $12M trajectory; $5M seed deployed per plan.

## Deployment mechanics (how a practice goes live)
1. **Adapter plug-in** (2 weeks): connect their EMR (FHIR/SMART or HL7 via Mirth) → verify read/write with their IT.
2. **Hermes bake-in** (day 1): their instance ships with the agent layer — scheduling, recall, scribe, billing sweeps run supervised.
3. **Training**: 2 sessions (providers + staff) + playbooks; success manager (Nova) for 30 days.
4. **Success metrics dashboard**: doc time, closures, coding lift, gaps, NPS — reported by Hermes weekly.

## Environments
Dev → Integration → Simulation (de-identified) → Staging → Production (supervised) + local-fallback. Every deployment follows the same gate sequence (runbook: MEDISUN-RIS-PACS-SETUP pattern generalized).

## Owners
Orion (architecture/adapters) · Atlas (sequencing/customer pilots) · Nova (onboarding/success) · Midas (economics) · Vigil (compliance gates) · Hermes (automation + verification, always baked in).

## SAAS-READY MANDATE (founder, standing — "once built fully, we make NURA a SaaS for other providers")
Every build ships multi-tenant-ready — NURA Imaging/Medisun are TENANTS (anchor/internal), not the end state.
Guardrails (encoded since 2026-08-02, DIV-1 charter):
- **Per-tenant isolation**: data, lanes, adapters, dashboards, memory scoped per tenant (tenant_id everywhere; never cross-tenant reads).
- **Adapter registry**: every EMR/clinic connection is a REGISTERED adapter (eMedical = tenant adapter #1) — new providers plug in, not rebuild.
- **Brandable bundle**: CRM/EMR/RIS/PACS/viewer/Hermes per-tenant branded (nura-product-lineup; multilingual EN/ES/Creole agents).
- **RBAC + audit**: per-tenant roles, full audit trail (provider = system owner; NURA = platform operator).
- **Economics**: Midas owns the tenant pricing model ($100–150/provider tiers); every internal deployment also validates SaaS unit economics.
- **Build rule**: ANY directive that ships without tenant-scoping is NOT done. Atlas enforces in scrum; Hermes checks in verification.
