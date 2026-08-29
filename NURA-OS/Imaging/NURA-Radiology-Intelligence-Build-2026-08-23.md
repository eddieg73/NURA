# NURA Radiology Intelligence — Build Spec + CTO Decisions (2026-08-23)

## Governing architecture (adopted from founder spec)
Hermes is the **exclusive event backbone/central spine**, not a peripheral. Modality-aware
imaging intelligence subsystem backing NURA Provider Labs. Full spec: this doc's companion
references + the founder's detailed build spec (modality pipelines, datasets, MCP/API/CLI, events).

## CTO decisions (all made)
- **A1** Hermes = spine; events not DB writes; every module publishes/subscribes.
- **A2** Knowledge & Dataset Gateway: FDA/PubMed/radiology/lab datasets behind controlled gateway
  with dataset_registry + license/DUA enforcement; no PHI leaves; clinical engine never calls them directly.
- **A3** Radiology output contract: NORMAL / ABNORMAL_NONURGENT / ABNORMAL_URGENT / CRITICAL /
  INDETERMINATE + ranked differential (highest relative likelihood first) + SEPARATE must-not-miss
  (by danger). Likelihood ≠ urgency, never merged.
- **A4** EMR risk containment: AI output = DRAFT → provider review (item-level) → approved final
  ONLY to OpenEMR via Mirth `OPENEMR_HERMES_BRIDGE`. Never auto-post; no consequential EHR action
  before authorization. See `EMR-RISK-GATES.md`.
- **A5** Durable broker = **NATS JetStream** (NO-MONEY fit). Redis = locks/rate/cache/idempotency
  only. Postgres outbox/inbox. Do not make Redis the durable record of clinical events.
- **A6** Only verified increments ship; facts over prose.

## Phase 1A (Chest X-ray) — vertical slice, VERIFIED 2026-08-23
- Model: TorchXRayVision DenseNet-121 (`cxr_triage.py`) on Lab (`/opt/radiology-venv`, torch 2.13).
- **Verified on real images:** COVID/abnormal CXR → top mass 0.68 / lung-opacity 0.66 → **CRITICAL**
  + must-not-miss; adult NORMAL CXR → top 0.63 → **INDETERMINATE** (abstain).
- **The model is UNCALIBRATED** → `deployment_status: SHADOW_ONLY`, `requires_provider_review: true`.
  No single threshold cleanly separates the normal/abnormal pair → abstain gate (top-1 < 0.65).
- Output contract: 5-level classification + findings + ranked differential + must_not_miss +
  provenance + five-assertion separations (image ≠ feature ≠ abnormal ≠ disease ≠ provider-diagnosed).
- Orchestrator (`/opt/data/nura-radiology-ai/orchestrator/main.py`): builds valid Basic Text
  DICOM-SR (1.2.840.10008.5.1.4.1.1.88.11) + MLLP-framed ORU^R01; source path proven.
- Orchestrator NOT yet deployed on Clinic (needs compose up + LAB model call); the ORU-in Mirth
  channel + RIS target are the remaining wiring (staged, not live).

## Foundation artifacts built
- `/opt/data/nura-radiology-ai/models/cxr_triage.py` — contract-bearing CXR runner (SHADOW_ONLY).
- `/opt/data/nura-radiology-ai/model-registry/registry_schema.sql` — dataset_registry/dataset_version/
  model_registry/routing_policy (Dataset Gateway + registry, spec §15/§47).
- `/opt/data/nura-radiology-ai/events/README.md` — Hermes radiology events + canonical envelope.
- `/opt/data/nura-radiology-ai/EMR-RISK-GATES.md` — the EMR risk-containment doctrine.
- Skills `radiology-ai-engineering` updated (SHADOW_ONLY + abstain gate).

## Roadmap (spec §59 / §58 order)
1A Chest X-ray → 1B General/MSK XR → 1C Mammo → 1D Breast US → 1E General US → 1F DXA → 2 CT → 3 MRI.
Flow for 1A (once live): Orthanc DICOMweb → Hermes event → DICOM validation → study router →
quality → CXR model → classification → findings → prior comparison → differential → must-not-miss →
evidence (with gate) → draft → provider review → approved → DICOM-SR + DiagnosticReport → Orthanc +
Mirth → EHR → audit.

## Model lane decision (08-23) — encoder vs reasoning cortex
- **Reasoning cortex (generator):** local = **Qwen3-8B-Instruct** (native tool-calling + JSON,
  primary) → **BioMistral-7B** (medical-domain); cloud = **DeepSeek** (fast, PHI-stripped at the
  gateway via phi_policy). Meditron/Med42 = tertiary (weaker structured output). deepseek-r1:8b
  = complex CoT route. All already on Lab Ollama.
- **Encoder/NER + embeddings lane:** **Clinical ModernBERT / BioClinical ModernBERT** (8k ctx,
  modern) or **nomic-embed-text** (on Lab). **GatorTron / ClinicalBERT / Bio_ClinicalBERT are
  ENCODERS (BERT/Megatron MLM) — NOT generators; use only for NER/relation/extraction/embeddings,
  never for radiology reasoning.**
- **CPU-only Lab** → local generation is slow; use small quantized models for bounded/async tasks.
  PHI-can't-leave → local; cloud calls require PHI-strip (opaque refs only).

## OpenEMR embedding directive (08-23)
AI must be **embedded inside OpenEMR** like Tebra/Epic/Cerner — in-context CDS surfaces in the
clinician workflow (encounter/note/orders/results worklist), provider-review-gated. The EMR-risk
gate (EMR-RISK-GATES.md) becomes an in-EHR review surface: AI draft surfaced inline → item-level
provider approval → only the approved final is committed. Never auto-post.

