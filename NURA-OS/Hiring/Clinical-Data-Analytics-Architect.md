# CLINICAL DATA ENGINEER & HEALTHCARE ANALYTICS ARCHITECT — the role spec (2026-08-04)

**Position:** Clinical Data Engineer & Healthcare Analytics Architect · **Funnel:** the AI hiring manager · **Signer:** the founder

## 1. MISSION
Build the data spine of NURA: the pipelines that move clinical and operational data (OpenEMR, labs, claims, messaging, device telemetry) into governed, analytics-ready stores — and the analytics that drive the founder's decisions: population health (CarePilot), RAF/HCC opportunity, revenue operations (the RATCHET/RCM lane), and the Assurance reporting. **The doctrine: analytics never invents — it measures; PHI stays on the Lattice.**

## 2. CORE OWNERSHIP
**ETL/ELT:** ingestion pipelines (HL7 ORU/ADT → FHIR → canonical → warehouse) · claims + revenue data · the lab lane · device/IoT telemetry (the 11073/BLE lanes) · change-data-capture · quality gates (schema, dedupe, PII checks).
**Modeling:** the canonical clinical data model (the Sidecar spec's entities) · star/snowflake schemas · the patient 360 · the population-health cohorts (HF/T2DM/CKD conditions — the CarePilot logic) · risk-adjustment (HCC/RAF) modeling · revenue analytics.
**Analytics:** dashboards + reports (the exec scorecard, the fleet health, the revenue ops) · cohort/trend analysis · the predictive lanes (readmissions, gaps) — provider-gated, never autonomous clinical action.
**Governance:** data dictionaries · lineage · quality monitoring · retention · the deidentification pipeline (test data from PHI safely) · access controls (minimum necessary).

## 3. REQUIRED STACK & EXPERIENCE
Python · SQL (PostgreSQL) · dbt · Airflow (or n8n for lighter lanes) · ClickHouse/BigQuery-class warehouses · Qdrant/vector for embeddings · FHIR/HL7 parsing · Parquet/Arrow · Metabase/Superset-class BI · Git/CI.
**Experience:** 5+ yrs data engineering · 3+ yrs healthcare data (EMR/labs/claims) · HL7/FHIR hands-on · warehouse modeling · analytics products for non-technical leaders · HIPAA discipline. Preferred: HCC/RAF · population health · revenue-cycle data · medical-device telemetry.

## 4. RECOMMENDED CERTIFICATIONS
AWS Data Analytics/Specialty · dbt training · Airflow certification · HL7/FHIR training · HIPAA training · Databricks/Snowflake-class certification. Certs ≠ ability — the exam decides.

## 5. THE PRACTICAL EXAM (the gate)
Given a raw dataset (labs + encounters + claims for a synthetic population), deliver: the pipeline (HL7/CSV → canonical model → warehouse with dbt-style transformations), the quality gates (dedupe, missing data, unit sanity), the population-health view (the HF/T2DM/CKD cohorts with RAF-adjacent scoring), the exec dashboard (3 charts answering: where is the revenue risk, where are the gaps, what changed), and the lineage docs. **Evaluation: modeling correctness, pipeline quality, analytics insight, governance, clarity for the founder.**

## 6. FIRST 90-DAY DELIVERABLES
**1-30:** the data inventory (what exists, where, quality) · the canonical model v1 · the first ingestion lane (the lighthouse's lab data) · the quality baseline.
**31-60:** the claims/revenue lane · the CarePilot cohort logic v2 · the patient 360 view · the deidentification pipeline · lineage + dictionaries.
**61-90:** the exec analytics (revenue ops + population health) · the predictive pilots (readmission/gap risk — provider-gated) · the data-quality SLA · the Assurance report baseline.

## 7. KPIs
Pipeline reliability (success rate, latency) · data-quality score · modeling coverage (canonical entities) · analytics adoption (the founder's dashboard views) · cohort accuracy vs chart review · lineage completeness · deidentification coverage. **Targets: PHI leakage in analytics = 0 · unreconciled pipeline failures = 0 · fabricated metrics = 0.**

## 8. THE JD SUMMARY
The Clinical Data Engineer & Analytics Architect turns NURA's data into the company's nervous system's reports: clean, governed, and honest. The role requires heavy data craft, healthcare fluency, and the discipline that every number shown to the founder is traceable to its source.
