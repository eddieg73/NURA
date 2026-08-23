# 03 — RADIOLOGY INTELLIGENCE

The AI imaging subsystem on top of the deployed RIS/PACS. Reconcile-and-wire, NOT rebuild.

## Flow
`DICOM (modality) → Orthanc C-STORE/DICOMweb → study.received event → DICOM validation → study router`
`→ quality → modality pipeline → imaging model (visual cortex) → structured findings`
`→ DeepSeek/Qwen3 (reasoning cortex) → report classification + ranked differential + MUST-NOT-MISS`
`→ evidence (via gateway) → DRAFT report → provider review → approved → DICOM-SR + DiagnosticReport`
`→ Orthanc + Mirth → EHR → audit`.

## Report contract (spec A3)
- `classification.status`: NORMAL / ABNORMAL_NONURGENT / ABNORMAL_URGENT / CRITICAL / INDETERMINATE
- `differential[]` ranked (highest relative likelihood first)
- `must_not_miss[]` **separate**, by clinical danger (NOT merged with likelihood)
- 5-assertion separation: image_seen ≠ feature_detected ≠ abnormal ≠ compatible_with_disease ≠
  provider_diagnosed. Never conflate.

## Model status — SHADOW_ONLY (verified 2026-08-23)
- TorchXRayVision DenseNet-121 on Lab (`torch 2.13`), `models/cxr_triage.py`.
- COVID CXR → top mass 0.678 / lung-opacity 0.658 → **CRITICAL**; adult normal → top 0.629 →
  **INDETERMINATE** (abstain gate top-1 < 0.65).
- **UNCALIBRATED** → `deployment_status: SHADOW_ONLY`, `requires_provider_review: true`. Promote only
  after AUC + calibration + external validation + clinical governance.

## Artifacts (in `backend/nura-radiology-ai/`)
- `model-registry/registry_schema.sql` — dataset_registry / dataset_version / model_registry /
  routing_policy (Dataset Gateway + model registry; spec §15/§47).
- `events/README.md` — imaging event catalog + canonical envelope.
- `EMR-RISK-GATES.md` — EMR risk containment.
- `storage/B2-STORAGE-BLUEPRINT.md` — buckets + Orthanc S3 plugin + storage_object schema.
- `services/model_gateway/` — the reasoning layer (see 04).
- `orchestrator/main.py` — FastAPI: builds valid Basic-Text DICOM-SR (1.2.840.10008.5.1.4.1.1.88.11)
  + MLLP-framed ORU. **NOT deployed** (dev + shadow on a non-HIPAA host until BAA host + B2 BAA).
- Orchestrator not deployed on Clinic; ORU-in channel + RIS target remain staged (risk-unconfirmed).

## Dataset Gateway (A2)
Radiology/lab/FDA data behind `dataset_registry` with license/DUA enforcement; `dataset_use_allowed()`.
Research data (NCI-IDC/TCIA/MIMIC/VinDr/CBIS-DDSM/SIIM) vs production PACS. No PHI leaves.
