# NURA AUTONOMOUS MEDICAL PRACTICE — MCP ARCHITECTURE v1 (2026-08-06)

**The founder's directive: the MEDBASE-supervisory-MCP architecture, defined as the v1 — the NuraTech-MCP as the PARENT orchestrator, the strongest MCPs underneath, the human-approval gates, the READ/WRITE/HITL classifications. The compare-baseline: the NURA already runs 24+ MCP lanes + n8n-live + OpenEMR + Twilio + the imaging-stack — this v1 = the orchestration-layer + the gaps.**

## 1. THE LAYERED STACK (the parent → children!)
```
NURA (voice/avatar/AI!)
  └── NURA SUPERVISORY MCP (identity · policies · RBAC · HITL · audit!)
        ├── FHIR-MCP (MEDBASE/OpenEMR — clinical READ/WRITE-gated!)
        ├── n8n-MCP (the automation control-plane — workflows!)
        ├── COMMS-MCP (Twilio-execution: voice/SMS/email/fax!)
        ├── IMAGING-MCP (Orthanc-DICOM → OHIF → the vision-agent!)
        ├── RCM-MCP (FHIRfly-class: ICD/CPT/NCCI/MUE/RVU/HCC!)
        ├── TERMINOLOGY-MCPs (RxNorm · SNOMED · LOINC · ICD-10!)
        ├── EVIDENCE-MCP (openFDA/PubMed/BioPortal — LIVE ✓!)
        └── SAFETY-MCP-GATEWAY (PHI-redaction · consent · AuditEvent ·
            HMAC-step-up · fail-closed de-identification!)
```

## 2. THE TOOL-CLASSES (the 75-100 map — the classes + the gates!)
| Class | Examples | Gate |
|---|---|---|
| PATIENT | book/reschedule/cancel · create/update-demographics · get-chart | READ-free · WRITE=HITL |
| INTAKE | start_intake · check-forms · request-missing | READ-free · WRITE=auto |
| CLINICAL-NOTES | consult/followup/procedure-note (the SOAP-drafts!) | WRITE=HITL (the provider-sign!) |
| ORDERS-LABS | prepare-lab-order · retrieve/interpret-results | WRITE=HITL (the orders!) |
| RX | prepare_rx · check-drug-interactions | WRITE=HITL+EPCS-gate (Weno!) |
| IMAGING | retrieve_imaging · open_study · radiology-summary | READ-free · the summary=HITL |
| RCM | verify-insurance · prior-auth · claim-gen · NCCI/MUE · RVU · HCC | READ-free · the claim=HITL |
| COMMS | send-sms · voice-call · email · fax | auto (the templates!) |
| PAYMENTS | collect_payment · issue-invoice | HITL + the NMI-gate (the refunds=step-up!) |
| MARKETING | recall-campaign · request-review · reactivate | auto (the Oussama-CRM-lane!) |
| OPS | create_task · escalate-to-staff | auto |

## 3. THE GATES (the founder's non-autonomous list — codified!)
- **NEVER autonomous**: final-diagnosis/treatment · controlled-substance-Rx (the EPCS!) · high-risk-med changes · abnormal-critical-disposition · invasive-orders (the clinician-authorization-policy!)
- **STEP-UP required**: refunds · large-financial · irreversible-chart-deletes · destructive-admin (the HMAC-step-up + the human!)
- **The PHI-rule**: the guardrail-gateway in FRONT of every public-MCP (the fail-closed de-identification — the HealthClaw/Umbryn-principles, OUR-gateway!)

## 4. THE BUILD-ORDER (the engineering-first-five!)
1. **NuraTech Supervisory MCP** (the parent — the identity/RBAC/HITL/audit!)
2. **n8n-MCP** (the control-plane — the n8n-API-key SEALED ✓!)
3. **FHIR/CDS-Hooks MCP** (the MEDBASE/OpenEMR-lane + the consent/RBAC/AuditEvent!)
4. **FHIRfly-class RCM MCP** (the ICD/CPT/NCCI/MUE/RVU/HCC — the economic-core!)
5. **Orthanc-DICOM MCP** (the PACS/OHIF-imaging!)
Then: the Twilio-execution · the terminology-lanes · the payments · the labs/pharmacy-connectors!

## 5. THE MEDBASE-OPENEMR RULE (the auditability!)
```
MEDBASE → FHIR-R4 → CDS-Hooks/FHIR-MCP → NURA   (the NEVER-SQL-direct!)
The sidecar-doctrine holds: OpenEMR-via-API-only, the audit-trail-everywhere!
```

## 6. THE VERIFICATION
- Every tool = the READ/WRITE/HITL class + the audit-log + the evidence!
- The build-milestones = the board-issues (the MCP-1..5 + the gates!)
