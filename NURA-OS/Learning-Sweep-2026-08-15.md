# Learning Sweep — 2026-08-15 (Firecrawl batch)

Distilled from primary sources via the Firecrawl lane. Full raw captures on disk where noted.

## 1. Google Health API (developers.google.com/health)
- **Scopes (verified):** `.activity_and_fitness.readonly|writeonly` · `.health_metrics_and_measurements.*` · `.sleep.*` · `.nutrition.*` · `.profile.*` · `.settings.*` · `.location.readonly` · `.ecg.readonly` (unlisted but real) · `.irn.readonly` · `.mindfulness.writeonly` · `.logged_symptoms.writeonly` · `.reproductive_health.writeonly`
- **31 data types** with per-type method support. Gotcha: `floors`, `total-calories`, `active-minutes`, `calories-in-heart-rate-zone`, `time-in-heart-rate-zone`, `daily-heart-rate-zones` do NOT support `:list` — rollup-only.
- Path: `GET /v4/users/me/dataTypes/{type}/dataPoints`. → wired into skill `fitbit-connection`.

## 2. eMedical FHIR (emedpractice.com) — THE INTEGRATION SPEC
- **FHIR 2.0 API: USCDI v3 compliant** — resources: Patient, SmokingStatus, Condition, Medications, AllergyIntolerance, Laboratory DiagnosticReport + Observations, VitalSign, Procedure, Care Team, Immunization, Assessment & Plan, Goal, Health Concern, All Data Retrieve.
- **FHIR R4** (§ 170.315(g)(10)) — client registration: `https://service.emedpractice.com/admin/fhirclientregistration.aspx` · help: `emedpractice.com/fhir/fhir_helpdoc.html` + `api_helpdoc.html`.
- Based on DSTU2 + R4 with ONC DAF profile → USCDI v3.
- FULL raw capture: `/tmp/hermes-results/call_00_hfw4CzH89eRwnm6ZsOxO0586.txt` (174KB) — the authoritative field-level doc for the eMedical→Mirth→Hermes adapter (spec Section 30 gate partially open for eMedical!).

## 3. Orthanc REST API (Book of Orthanc — full cheatsheet captured)
Key endpoints for the NURA imaging spine:
- **Worklist (the missing piece for OpenEMR→imaging orders):** `POST /modalities/{id}/find-worklist` (C-FIND SCU worklist)
- Query/Retrieve: `/queries/*`, `/modalities/{id}/query|move|get|store|store-straight|echo`, `/peers/{id}/store`
- Studies/Series/Instances full trees + anonymize/modify/reconstruct/bulk tools
- Storage commitment: `/modalities/{id}/storage-commitment` + `/storage-commitment/{id}`
- System: `/tools/{dicom-echo,find,lookup,bulk-anonymize,bulk-modify,create-dicom,metrics-prometheus,reset,shutdown}`, `/system`, `/statistics`
- Lua scripting: `/tools/execute-script`
- Book index: users.html · dicom-guide.html · plugins.html · users/rest.html · users/advanced-rest.html · users/lua.html

## 4. Solis/Ensure portal (live-crawled)
Full map in `hermes-ensure-operations` skill + `Ensure-Program-Guide.md` (Products/).

## Standing blockers (unchanged)
- YouTube cookies (founder drop → /opt/data/cookies/)
- Ensure/Solis interface artifacts (SFTP/API specs, sample 834/837) — Section 30 gate
- Google Health redirect URI (founder's Google Cloud console value)
