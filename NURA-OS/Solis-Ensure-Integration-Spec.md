# Hermes — Solis Health Plans / Ensure Data Solutions Integration Specification

**Organization:** NuraTech AI · **System:** Hermes · **Payer:** Solis Health Plans
**Data/Managed-Care Integration:** Ensure Data Solutions · **Practice Management:** MDFlow
**Clinical EMR:** eMedical · **Interoperability Engine:** Mirth Connect
**Purpose:** Medicare Advantage population health — RAF, HEDIS, Stars, MLR, utilization, care-gap management
**Directive date:** 2026-08-15 (founder)

---

## 1. Objective
Hermes ingests, normalizes, reconciles and operationalizes Ensure/Solis data — not display, but ACTION:
- Identify attributed Solis members · verify eligibility/enrollment
- Reconcile membership across Ensure ↔ MDFlow ↔ eMedical
- Open HCC/RAF opportunities · suspected-but-undocumented conditions
- HEDIS/quality gaps · missing AWVs · claims/encounter history
- ED utilization · admissions/readmissions · medication opportunities · prior auths
- Provider work queues · intervention completion · full auditability of every AI recommendation

## 2. Target Architecture
Solis → Ensure (eligibility 834 · claims 837/835 · quality/risk RAF/HEDIS) → INGESTION (SFTP/API/HL7/X12) → Mirth → Hermes Normalization → Patient Identity (EMPI) + Validation → Hermes Data Model → Engines (RAF/HCC · HEDIS · Utilization · Claims · Pharmacy) → Reasoning Layer (Clinical Review Agent + Operational Agent) → ACTION ENGINE → MDFlow / eMedical / Staff Work Queues.

## 3. Data sources (configurable adapters — never hard-code one format)
- **Membership/Eligibility:** X12 834 — Solis member ID, Medicare IDs (where permitted), effective/termination dates, PCP attribution, plan/product, status, dual-eligibility, risk population, provider assignment.
- **Claims:** 837P/I/D where available, 835 ERA, payer CSV/JSON/API. Fields: claim_id, member_id, provider_npi, facility, DOS, POS, dx codes, procedure/HCPCS, revenue, DRG, status, paid/allowed, member responsibility, admit/discharge dates. RETAIN original payer record alongside normalized.
- **Patient Identity (EMPI):** match hierarchy = Solis Member ID → Medicare ID → MDFlow Patient ID → eMedical Patient ID → Name+DOB+Sex → demographic reconciliation. Confidence tiers: exact 1.00 / high / medium / manual_review. Ambiguous → PATIENT IDENTITY REVIEW QUEUE. NEVER auto-merge.

## 6. Canonical Member object
hermes_patient_id · solis_member_id · mdflow_patient_id · emedical_patient_id · demographics · pcp_npi · dates · dual_eligible + risk {current_raf, projected_raf, open_hcc[], suspected_hcc[], recapture_required[]} + quality {open/closed hedis, awv_due} + utilization {ed_visits[], admissions[], readmissions[]} + claims[] + medications[] + care_gaps[] + prior_authorizations[] + interventions[].

## 7. RAF/HCC Engine
Ensure claims + eMedical documentation + MDFlow + labs + meds → HCC opportunity detection.
Condition statuses: CONFIRMED · DOCUMENTED · CODED · RECAPTURE REQUIRED · SUSPECTED · INSUFFICIENT EVIDENCE · RESOLVED.
Each condition: icd10_candidates[], evidence {claims, emr_note, laboratory}, status REQUIRES_PROVIDER_REVIEW, confidence.
**CRITICAL: never autonomously add a diagnosis to increase RAF. Provider validates clinical support + documentation.**

## 8. Annual HCC Recapture
Historical HCC → current-year evidence search → documentation present? YES/NO → Provider Review Queue.
Dashboard: Patient | Previous HCC | Current Evidence (OPEN/DOCUMENTED/REVIEW).

## 9. HEDIS/Quality Engine
Per-member: measure, eligible, numerator_met, evidence[], due_date, recommended_action, status OPEN.
Work queues: Diabetes, HTN, Cancer Screening, Med Adherence, AWV, TOC, Preventive Services. Measure set = configuration-driven (payer/CMS specs change).

## 10. MLR Intelligence
Total member cost, PMPM, ED cost, inpatient cost, specialist cost, pharmacy cost, preventable utilization, readmission cost. Identify populations for care-management review — NEVER withhold medically necessary care.

## 11. Admission/Discharge Intelligence
ADT → Hermes event → patient match → MDFlow update → care-coordinator alert; discharge → TOC workflow → med rec → PCP follow-up. Priority: ED, admission, discharge, readmission, SNF, high-risk transition.

## 12. MDFlow Integration (managed-care ops layer)
Hermes WRITES actionable data: attribution, eligibility, RAF/HCC, HEDIS, care gaps, utilization, outreach, appointments, interventions, provider tasks. Task object: patient_id, task_type (HCC_REVIEW…), priority, payer SOLIS, source ENSURE, reason, status OPEN.

## 13. eMedical Integration
eMedical = provider charting EMR. Hermes never replaces the medical record. Sync: notes, ICD-10, CPT, procedures, problem list, meds, labs, provider documentation. Flow: eMedical → RPA/Interface → Hermes → clinical validation → MDFlow → Ensure reporting.

## 14. RPA Layer (only where eMedical lacks APIs)
Extract: identifiers, encounter date, provider, signed note, ICD-10, CPT, procedures, relevant data.
Store: source_system, source_record_id, extraction_timestamp, hash, RPA_job_id, validation_status. RPA ≠ primary longitudinal DB.

## 15. Mirth Channels
SOLIS_ENSURE_INBOUND · ENSURE_ELIGIBILITY · ENSURE_CLAIMS · ENSURE_QUALITY · ENSURE_RISK · ENSURE_UTILIZATION · EMEDICAL_INBOUND · MDFLOW_OUTBOUND · MDFLOW_INBOUND · HERMES_FHIR · HERMES_ADT.
Mirth = receive, validate, transform, route, retry, quarantine, log. Malformed → HERMES DATA QUARANTINE.

## 16. FHIR Normalization
Eligibility→Coverage · Patient→Patient · Provider→Practitioner · Diagnosis→Condition · Claim→Claim · Encounter→Encounter · Medication→MedicationRequest · Lab→Observation · Procedure→Procedure · Care Gap→DetectedIssue/MeasureReport. PRESERVE raw X12 source.

## 17. Agent Architecture
Hermes Orchestrator → Eligibility Agent · Claims Agent · RAF/HCC Agent · HEDIS Agent · Utilization Agent · Care Gap Agent · Laboratory Agent · Coding Agent · Provider Documentation Agent · Population Health Agent.

## 18. Example Event (claim)
Ensure claim → Mirth → Hermes → identity → Claims/RAF/HCC/HEDIS/Utilization/Care-Gap agents → Action Engine → No Action | Provider Review | Care Coordinator Task | HCC Review | HEDIS Gap | Post-Discharge Follow-Up | Medication Review | Patient Outreach.

## 19. Provider Review (evidence-mandatory)
POSSIBLE HCC RECAPTURE card: condition, evidence (2025 claim I50.9, 2025 cardio note "History of CHF", 2026 loop diuretic, current-year documentation absent), action text, buttons CONFIRM / NOT PRESENT / NEEDS MORE INFORMATION / DEFER. Hermes records the decision.

## 20. Evidence Provenance (mandatory)
recommendation_id, patient_id, source, source_record, source_date, algorithm_version, model_version, rule_version, evidence, confidence, provider_action, provider_id, timestamp.

## 21. Human-in-the-Loop Rules
Hermes MAY: detect, compare, calculate, prioritize, recommend, draft, create work queues, request review.
Hermes MAY NOT: invent diagnoses, upcode, submit unsupported HCCs, alter signed notes, remove appropriate diagnoses, deny medically necessary treatment, change documentation without authorization.

## 22. Solis Command Center Dashboard
KPIs: attributed/active/unmatched members, open HCC reviews, projected RAF, HEDIS gaps, AWV completion, ED utilization, admissions, readmissions, PMPM, high-risk members, pending prior auths, TOC, provider review queue. Filters: provider, practice, location, Solis product, member, risk level, HCC, HEDIS measure, date range, utilization level.

## 23. Member 360
Demographics/Eligibility/Attribution · Clinical (dx/meds/labs) · Claims (procedures/hospitalizations) · RAF (HCC history/opportunities) · HEDIS/care gaps · Utilization (ED/IP/readmission) · Prior Auth · Interventions · Audit History.

## 24. Security (all data = PHI)
TLS 1.2+, encryption at rest, RBAC, MFA, least privilege, tenant isolation, audit logging, secrets management, session expiration, environment separation, immutable security logs, backup/DR. No PHI in app logs.

## 25. Data Zones
01 RAW (original payload, NEVER overwritten) → 02 VALIDATED (schema/integrity) → 03 NORMALIZED (canonical/FHIR) → 04 ACTIONABLE (risk/HEDIS/utilization/workflow).

## 26. Idempotency
key = SHA256(payer + member_id + claim_id + service_date + transaction_type). Exists → compare version, update when appropriate, never duplicate.

## 27. Error Handling
States: RECEIVED · VALIDATING · VALIDATED · PROCESSING · PROCESSED · REJECTED · QUARANTINED · RETRY · MANUAL_REVIEW. Never silently discard.

## 28. Database Domains
members · member_identifiers · eligibility · attribution · claims · claim_lines · encounters · diagnoses · procedures · medications · labs · hcc_history · hcc_opportunities · raf_scores · hedis_measures · care_gaps · admissions · discharges · readmissions · prior_authorizations · provider_tasks · patient_outreach · interventions · source_documents · audit_events.

## 29. Implementation Sequence
P1 Connectivity → P2 Membership → P3 Claims → P4 Risk Adjustment → P5 Quality → P6 Utilization → P7 Hermes Intelligence.

## 30. CRITICAL FIRST ENGINEERING TASK
Obtain the ACTUAL Ensure interface specification for the Solis contract BEFORE writing parsers:
API docs, SFTP specs, file naming conventions, sample files, data dictionaries, X12 companion guides, eligibility/claims/risk/HEDIS/utilization/prior-auth/ADT/pharmacy file specs, error files, transmission schedule, authentication. Build adapters against contracted schemas — never assumed field names.

## 31. Definition of Done (Phase I)
Connectivity authenticated · raw transactions retained · eligibility ingests · Solis reconciles vs MDFlow + eMedical · ambiguous identities → manual review · claims normalize · ICD-10/CPT reconcile · HCC history visible · review opportunities generated · HEDIS/care gaps visible · utilization events → workflows · MDFlow receives tasks · provider decisions recorded · provenance everywhere · quarantined recoverable · HIPAA validated · end-to-end audit.

## 32. Core Design Principle
ENSURE/SOLIS = PAYER TRUTH · eMEDICAL = CLINICAL DOCUMENTATION · MDFLOW = MANAGED-CARE OPERATIONS · HERMES = INTELLIGENCE + ORCHESTRATION.
Flow: DATA → IDENTITY → NORMALIZATION → EVIDENCE → REASONING → HUMAN REVIEW → ACTION → MEASUREMENT → AUDIT.
