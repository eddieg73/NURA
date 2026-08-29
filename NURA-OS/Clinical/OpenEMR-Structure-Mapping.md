# OpenEMR Structure Mapping — where every NURA artifact lands (2026-08-17)

OpenEMR = the internal truth (the sidecar doctrine). Its structure = the hospital-system standard:
**FHIR R4 (30+ resources)** at :9300/apis/default/fhir + the SMART-on-FHIR + the REST /api lane —
the same standard Epic/Cerner/NextGen speak. Verified against the repo's FHIR_README + API_README.

## The mapping (artifact → the correct FHIR/native location)
| NURA artifact | FHIR R4 resource | OpenEMR native home |
|---|---|---|
| **Lab values** (the serial results) | `Observation` (category=laboratory) | Procedure Results (procedure_order/procedure_result) + the MCP lab_trends |
| **The interpretation text** (impression/recommendations) | `DiagnosticReport` (the narrative + conclusion) | the encounter/result narrative |
| **The faxed/emailed PDFs** | `DocumentReference` (the Documents tree) | Documents → category (Lab Reports / Imaging) → patient |
| **Vital signs** | `Observation` (category=vital-signs) | the vitals form + the MCP vital_trends |
| **The encounter context** | `Encounter` (+ the SMART launch) | form_encounter |
| **Who/what generated it** | `Provenance` | the audit trail (Hermes = the agent attribution) |
| **The orders/referrals** | `ServiceRequest` · `MedicationRequest` | the orders tree |

## The endpoints (verified)
- `GET /apis/default/fhir/Observation?patient=123&category=laboratory` — the labs
- `POST /apis/default/fhir/DocumentReference/$docref` — the CCD/document generation
- `GET /apis/default/fhir/Patient/$export` — the bulk export
- `GET /api/patient/123/encounter` — the native REST encounters
- SMART scopes: `patient/Observation.rs patient/Patient.rs` (+ the API/fhir scopes)

## The lab-intake placement (the founder's directive)
```
fax/email PDF   → DocumentReference (Documents → the right category)
extracted labs  → Observation (laboratory) with the provenance
interpretation  → DiagnosticReport (the narrative) — "DRAFT — PROVIDER APPROVAL REQUIRED"
trends          → the Observation series (the serial points)
```

## The doctrine
- API/FHIR only — never DB writes.
- The provider approves every interpretation before it's final.
- The Provenance resource records the Hermes attribution on every artifact.
