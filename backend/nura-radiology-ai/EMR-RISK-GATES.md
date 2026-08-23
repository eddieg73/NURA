# EMR Risk Containment — NURA Radiology Intelligence (non-negotiable)

**The risk:** an AI radiology finding is a DRAFT. If it auto-flows into OpenEMR as a completed
observation or finalized report, it crosses a patient-safety + regulatory line and corrupts the
"source of truth." This document is the gate any radiology output must pass before the EHR.

## Gate chain (nothing auto-posts)
```
AI inference event (nura.imaging.inference.completed.v1)
   -> report.classification (Normal/Abnormal/Critical/Indeterminate)
   -> differential + must-not-miss (separate dimensions)
   -> nura.imaging.report.draft-created.v1   (DRAFT — PROVIDER REVIEW REQUIRED)
   -> nura.imaging.provider-review.requested.v1
   -> [ RADIOLOGIST/PROVIDER: modify / approve / reject / escalate — ITEM-LEVEL ]
   -> nura.imaging.provider-decision.recorded.v1
   -> nura.imaging.report.approved.v1
   -> Action Executor -> DICOM-SR/FHIR ORU -> Mirth -> EHR (OpenEMR)   <-- ONLY the approved final
```

## Hard rules
1. **Never auto-post the AI draft to OpenEMR or its DB.** The AI output is an event awaiting
   provider authorization. OpenEMR receives only a **provider-signed final** via the
   `OPENEMR_HERMES_BRIDGE` channel — gated on a human approve action.
2. **No consequential EHR action before authorization (spec §14).** Rejected actions are not
   transmitted; modified content is preserved separately from the AI draft.
3. **The five assertions stay separate (spec §60):** image seen ≠ feature detected ≠ abnormal ≠
   compatible-with-disease ≠ provider-diagnosed. Provenance-bearing objects each.
4. **No patient identifiers in external evidence queries** (the Knowledge Gateway strips
   MRN/name/DOB/phone/email before FDA/PubMed).
5. **Deterministic CRITICAL escalation config, clinically validated** (spec §56): pneumothorax,
   tension physiology, malpositioned device, acute hemorrhage, PE, aortic emergency, perforation,
   acute fracture, unexpected malignancy. Not auto-derived from a research model.
6. **Shadow-only until governed approval (spec §61).** The current TorchXRayVision model is
   uncalibrated → `SHADOW_ONLY`. It must be validated (AUC/calibration/external test) and receive
   clinical governance before any `CLINICALLY_ENABLED` promotion.
7. **Sidecar doctrine (unchanged):** OpenEMR via API only (never DB writes); Perfex never stores
   clinical data; no PHI in any test.
