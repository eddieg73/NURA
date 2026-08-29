# eMedPractice API + FHIR INTEGRATION SPEC (2026-08-04)

**Source:** the vendor's official docs (api_helpdoc.html + fhir_helpdoc.html) · **The eMedical lane = the second EMR rail** (the PRIME DIRECTIVE's agnostic promise — OpenEMR + eMedPractice + any future EMR).
**Creds:** sealed (.env EMED_* · 0600) · **Portal:** service.emedpractice.com (bot-walled to automation — the API = the clean lane).

## 1. THE SURFACE (what the API exposes)
**Stack:** OpenEMR-derived PHP + OIDC/OAuth2 (IdentityServer-class) — the FHIR R4 + US Core 3.1 conformant.

| Surface | Base | Key resources |
|---|---|---|
| FHIR R4 | `https://fhirbackup.emedpractice.com:8443/r4/` | Patient · Encounter · Observation · Condition · MedicationRequest · DiagnosticReport · DocumentReference · CarePlan · Coverage · AllergyIntolerance · Immunization · Device · CareTeam · Goal · Provenance · Procedure · Practitioner · Organization · Location |
| Standard REST | `/api/` | patient · encounter · vital · soap_note · prescription · medication · medical_problem · allergy · appointment · document · insurance · transaction · surgery · procedure · message · facility · drug · immunization · practitioner · insurance_company · insurance_type · list |
| Patient Portal | `/portal/` | patient · appointment · encounter (experimental) |
| BULK | `/r4/$export` · `/r4/Group/{id}/$export` · `/r4/Patient/$export` | NDJSON downloads via the $bulkdata-status job URL |
| CCD/CCDA | `$docref` (US Core OperationDefinition) | the generated CareCoordination Summary (sections: meds, problems, allergies, labs, vitals, encounters, plan...) |

## 2. AUTH (OIDC)
- **Grant:** authorization-code + PKCE (public apps) — refresh via `offline_access` (1h tokens, 3-month refresh, rotating).
- **Scopes:** explicit only (NO wildcards, no post-registration additions): `api:fhir` (the /fhir/ endpoints), `api:oemr` (the /api/ endpoints), `api:port` (the /portal/), plus per-resource `user/*`, `system/*`, `patient/*` read/write scopes.
- **Our scope set (minimum):** `openid offline_access api:fhir api:oemr user/Patient.read user/Encounter.read user/Observation.read user/DiagnosticReport.read user/MedicationRequest.read user/Medication.read user/Condition.read user/AllergyIntolerance.read user/CarePlan.read user/DocumentReference.read` (+ `system/Patient.$export system/*.$bulkdata-status system/Document.read` for the bulk lane when authorized).
- **Response format:** `{validationErrors: [], internalErrors: [], data: {...}}`.
- **Security:** TLS only · PKCE mandatory for public apps · the password grant = discouraged/off · manual approval = the safest admin setting.

## 3. THE SETUP (the founder's 3 clicks in the portal — then I run)
1. Login (E.Garrido — sealed) → **SiteAdmin → FhirSetup → "Enable eMedPractice Standard FHIR REST API"** + **"Enable eMedPractice Standard REST API"**
2. **FhirSetup → 'Site Address (required for OAuth2 and FHIR)'** — set the public base (e.g. https://service.emedpractice.com)
3. **Register the NURA client:** `/admin/fhirclientregistration.aspx` — name "NURA Hermes", redirect_uri (our OAuth callback), launch url, the explicit scope list (above) → the vendor/admin approves (patient-standalone auto; system/user = administrator approval)
→ Then: the OAuth authorization-code flow (founder approves once in the browser) → the MCP lane goes live.

## 4. THE LANE (what Hermes will do with it)
```
1. THE SIDECAR DESTINATION — the chart-in-NURA → eMedPractice delivery (via the NextGen adapter)
2. THE CLINICAL READ LANE — patient search · encounters · labs (DiagnosticReport/Observation)
   · meds (MedicationRequest) · allergies · problems · care plans → the NURA chart context
3. THE CAREPILOT ENRICHMENT — the eMedical EMR data = the "90 enriched encounters" source —
   the FHIR lane replaces the scrape
4. THE BULK/CCD LANE — the $export NDJSON + the $docref CCD → the longitudinal records + the
   care-coordination docs (the Sidecar's C-CDA strategy, vendor-native)
5. THE RCM TIE — the /api/ transaction/insurance/document endpoints → the ClaimRev/RCM lane
```
**Gates (unchanged):** read-heavy first (the minimum-necessary scopes), no writes until authorized, PHI stays on the Lattice, every call audited, the Ensure doctrine's human-review gates for anything clinical.

## 5. THE VENDOR'S NATIVE INTEGRATIONS (the 11-site landscape — founder-supplied 08-04)
| Category | Native links | NURA slot |
|---|---|---|
| Diagnostics/Labs | **Quest · Labcorp** (bi-directional: order from chart, auto-pull results) · allergy-testing hardware | the lab lane — ORU-class results → CarePilot enrichment + the lab-review lane |
| Payments | **Payarc** (embedded payment infra in the EHR) · Patient Portal Payments | the Woo Chat **Pay** module rail (cards/copays/deductibles) |
| Pharmacy | **National Pharmacy Directory** (eRx + electronic prior auths) · **EPCS** (controlled substances) | the prescribing lane — the vendor-native e-Rx/EPCS (the DoseSpot-class rail, already theirs) |
| Patient Engagement | **rater8** (reviews/feedback automation) · **NLSQL + Juno Health** (analytics/visualization) | the Woo Chat **Reviews** module + the analytics comparison |
| Scanners | **TWAIN hardware** (Fujitsu fi-7160 · Brother ADS-2200 · Epson ES-400 · Canon imageFORMULA R40) | the intake/digitization lane (the fax-to-chart pipeline's scanning sibling) |
| Developer APIs | the **REST API** (api_helpdoc) + **SMART on FHIR** scopes | THE lane we're building — the MCP adapter |

## 6. THE NEXT STEP
The founder's 3 clicks (section 3) → I register the client, run the OAuth flow, and probe the metadata endpoint (`/metadata` — the Capability Statement = auth-free) to confirm the tenant's live capabilities before wiring the lane.

**The eMedical rail is fully specified — the vendor's own interface is the path, and the PRIME DIRECTIVE's second EMR goes live on it, boss.**
