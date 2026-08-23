# 02 — CLINICAL STACK

The clinical spine on Clinic. **Sidecar doctrine: NURA chart → OpenEMR = internal truth → NextGen →**
**dest EMR. OpenEMR via API only (never raw DB writes). Perfex never stores clinical data.**

## Components (all deployed)
| Service | Where | Notes |
|---|---|---|
| **OpenEMR** | Clinic `openemr-zklo-openemr-1` :32768 | Clinical truth. Lanes: OpenEMR MCP (screen + 20 tools), FHIR. Login gate = NPI/paramedic license. |
| **Mirth/OIE 4.6** | Clinic `mirth-oie46` :8445 admin / :6663 MLLP | HL7 interface. Channels: SOLIS_ENSURE_INBOUND (STARTED :6661→:6663), OPENEMR_HERMES_BRIDGE, RISPACS_HERMES_BRIDGE. **Admin password FIXED (PBKDF2-600k)** — sealed in `/opt/data/mirth-oie-admin.txt`. **Never redeploy-fresh** (would destroy SOLIS). |
| **MedPlum** | Lab | FHIR backbone. |
| **ThaiRIS / RIS** | Clinic `nura-ris-web` :32790 | The RIS. |
| **OHIF** | Clinic `ohif-viewer` :32791 | Provider viewer; DICOMweb auth-forwarding needs reconcile. |
| **Orthanc** | Clinic :8042 / :4242 | PACS (index in Postgres, objects in B2 via S3 plugin). |
| **Chatwoot / DocsGPT** | Clinic | Comms / docs RAG. |

## Mirth verify ladder
`curl -sk -u admin:<pw> -H 'X-Requested-With: OpenAPI' https://127.0.0.1:8445/api/channels`
→ 200 = auth good. PGP user `mirth`, db `enginedb`. `DATABASE_PASSWORD` is PG, not admin.

## EMR risk gate (non-negotiable)
AI output = **DRAFT → item-level provider approval → ONLY the approved final** reaches OpenEMR via
Mirth `OPENEMR_HERMES_BRIDGE`. Never auto-post a draft. No consequential EHR action before
authorization. See `nura-radiology-ai/EMR-RISK-GATES.md`.

## OpenEMR AI embed (Tebra/Epic/Cerner pattern)
AI CDS surfaces **inside OpenEMR** in the clinician workflow (encounter/note/orders/results
worklist), provider-review-gated. Realized via the **OpenEMR MCP** (`get_patient_clinical_summary`,
`append_encounter_note` = chart mutation provider review required, `submit_encounter_billing` =
billing mutation). Never hand-roll PHP modules when the MCP lane is the sanctioned interface.
