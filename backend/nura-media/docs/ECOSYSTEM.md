# NURA Ecosystem — Master Map + Build Runbook (CTO, 2026-08-23)

This is the authoritative map: how the whole NURA stack is laid out, every decision that governs
it, and the runbook of the steps taken to build it. Read this before touching anything.

## 0. Governing decisions (all made as CTO)

| # | Decision |
|---|---|
| **A1** | **Hermes = the spine.** Hermes is the orchestration/tool-control/event/safety/audit layer, model-agnostic. Modules never write each other's DBs; all state changes are Hermes events. |
| **A2** | **Knowledge & Dataset Gateway.** FDA/PubMed/radiology/lab/clinical data behind a controlled gateway (dataset_registry + license/DUA enforcement). No PHI leaves. Clinical engine never calls external evidence directly. |
| **A3** | **Radiology output contract.** NORMAL / ABNORMAL_NONURGENT / ABNORMAL_URGENT / CRITICAL / INDETERMINATE + ranked differential (highest relative likelihood first) + **SEPARATE must-not-miss** (by danger). Likelihood ≠ urgency. |
| **A4** | **EMR risk containment.** AI output = DRAFT → item-level provider approval → **only the approved final** reaches OpenEMR (via Mirth `OPENEMR_HERMES_BRIDGE`). Never auto-post. See `services/../EMR-RISK-GATES.md`. |
| **A5** | **Durable broker = NATS JetStream** for durable clinical events; **Redis = transient only** (locks/rate/cache/idempotency). Postgres = durable state. (Media jobs use Celery+Redis dispatch + Postgres ledger.) |
| **D1–D4** | **HIPAA/Storage.** Hostinger = **NOT HIPAA** → dev/non-PHI/synthetic only. **Backblaze B2 = durable object storage** (execute the B2 BAA before any PHI). Postgres=state · Hermes=events(refs) · Redis=transient · compute=replaceable. No PHI in object keys; private buckets; least-privilege app keys. |
| **MD1** | **Media Engine** (new). Provider-router abstraction, local-first, commercial (HeyGen/Higgsfield/CapCut) = replaceable fallbacks. Medical content = evidence-validated + **clinical approval gate** before publish. |

## 1. Ecosystem map

```
USERS ── Cloudflare/WAF ── NURA API/Gateway
                              │
                    ┌─────────┴──────────┐
                    │ (AUTH / RBAC)      │
                    └─────────┬──────────┘
        ┌─────────────────────┼─────────────────────────────┐
   HERMES (spine)      MODEL GATEWAY               MEDIA ENGINE (nura-media)
   events/tools        reason(task,payload)         script→generate→edit→QA→store→publish
        │                     │                              │
   ┌────┴─────┐        ┌──────┴──────┐                ┌──────┴──────┐
   │ EMR/RIS  │        │ DeepSeek    │                │ Provider    │
   │ OpenEMR  │        │ (cloud, PHI-│                │ Router      │
   │ Mirth    │        │ stripped)   │                │ local-first │
   │ Orthanc  │        │ Qwen3-8B /  │                │ GPU workers │
   │ ThaiRIS  │        │ BioMistral  │                │ (RunPod)    │
   │          │        │ (local)     │                │             │
   └────┬─────┘        └──────┬──────┘                └──────┬──────┘
        │                     │                              │
   ┌────┴─────────────────────┴──────────────────────────────┴─────┐
   │   DATA LAYER                                                 │
   │   Postgres = durable state · B2 = binary objects ·          │
   │   Redis = transient · Qdrant = embedding/semantic           │
   └──────────────────────────────────────────────────────────────┘
```

## 2. The data fabric (separation of concerns — the key to recoverability)
- **Postgres** — durable structured state: patients, study/report metadata, workflow, audit,
  object metadata, model registry, generation ledger. Source of truth.
- **Backblaze B2** — large binary objects: DICOM, docs, audio, media renders, models, datasets.
  `objects/<hash-prefix>/<uuid>.dcm` (no PHI in keys). Buckets: `nura-prod-clinical-*`,
  `nura-prod-ai-derived`, `nura-prod-audit`, `nura-prod-backups`, `nura-research-deidentified`,
  `nura-datasets-public`, `nura-model-artifacts`, `nura-development`.
- **Redis** — transient only: locks, rate-limit, cache, queue coordination, idempotency window.
- **Qdrant/pgvector** — embeddings/semantic index; store refs (object_id, chunk), never dup binaries.

## 3. Model lane (encoder vs generator — decided)
- **Reasoning cortex (generator):** cloud **DeepSeek** (fast, PHI-stripped at the gateway via
  `phi_policy`); local **Qwen3-8B-Instruct** (tool-calling + JSON, primary) → **BioMistral-7B**
  (medical). Meditron/Med42 = tertiary. deepseek-r1:8b = complex CoT. **All already on Lab Ollama.**
- **Encoder/NER + embeddings:** **Clinical ModernBERT / BioClinical ModernBERT** (8k ctx) or
  **nomic-embed-text** (on Lab). **GatorTron / ClinicalBERT are ENCODERS — never reason with them.**
- **Visual cortex (pixels):** qwen3-vl / minicpm-v / llama3.2-vision (on Lab) → structured findings
  FIRST; the reasoning model never sees raw pixels.
- **CPU-only Lab** → local generation is slow; bounded/async only. PHI-can't-leave → local; cloud
  calls require PHI-strip (opaque refs only).

## 4. Fleet topology (existing deployed medical stack — document, don't rebuild)
- **Clinic** `72.61.71.211` (Hostinger, dev/non-PHI): **OpenEMR** (`openemr-zklo`), **Mirth-connect
  + Mirth-oie46**, **MedPlum** (FHIR backbone), **Orthanc**, **ThaiRIS/RIS**, **OHIF**, **DocsGPT**,
  **Chatwoot**, **Hermes gateway/dashboard**, **Perfex**, **n8n**, **nura-coding**, **qdrant**, **redis**,
  **nginx-proxy-manager**. Control-plane only; large AI models do NOT run here.
- **Lab** `72.60.163.140` (Hostinger, CPU): `/opt/radiology-venv` (TorchXRayVision + TotalSegmentator),
  **Ollama** (Qwen3-8B, biomistral, vision, deepseek-r1), **Celery+Redis** workers (`docker-worker`),
  **Qdrant**, **n8n**, **langfuse** (LLM observability), **medisun** (population-health/RAF),
  **medplum**, **kaggle-mcp**, **sovereign-ollama**.
- **Edge** `195.35.32.113`: **nginx-proxy-manager**, public edge.
- **Backblaze B2** = dataset/object lake (founder: datasets→B2, servers compute-only).
- **No GPU** anywhere → local video/avatar models gated; use Hermes built-in **FLUX3** tools or
  (once RunPod key valid) ephemeral GPU workers.

## 4.1 Existing vs net-new (reconcile, don't duplicate)
| Layer | Existing (deployed) | Net-new (this build) |
|---|---|---|
| RIS/PACS | Orthanc, ThaiRIS, OHIF | — (keep) |
| Interface engine | Mirth 4.6 (SOLIS/OPENEMR/RISPACS channels) | — (keep) |
| EMR | OpenEMR + MedPlum FHIR | — (keep) |
| Vet/RAG/docs | DocsGPT, Qdrant | — (keep) |
| Model gateway | — | `services/model_gateway` |
| Radiology AI | TorchXRayVision (SHADOW_ONLY) | `nura-radiology-ai` (contracts/registry/events) |
| Storage | B2 (dataset lake) | `nura-radiology-ai/storage` blueprint + `nura-prod-*` buckets |
| Media | video-studio-stack skills | `nura-media` (engine MVP) |

## 5. Build runbook — every step taken (2026-08-23), with evidence

### 5.1 Mirth 4.6.0 admin login — FIXED in-place (was the blocker)
- Root cause: Mirth/OIE ≥4.4 verifies passwords with **PBKDF2WithHmacSHA256 @600,000 iters,
  8-byte salt, 256-bit**, stored `base64(salt[8]‖digest[32])`. The DB was **seeded with a legacy
  single SHA-256 hash** (`SHA256(salt‖'admin')` — the <4.4 default) and **no fallback** configured,
  so NO password could verify (prior "custom KDF" claim was wrong).
- Fix: `UPDATE person_password SET password='<base64(salt‖PBKDF2-sha256(pw,salt,600000,32))>'`
  for `person_id=1` → `/api/users/_login` = **SUCCESS**, `/api/channels` = 200.
- **CRITICAL: the engine is NOT empty** — holds `SOLIS_ENSURE_INBOUND` (STARTED :6661→:6663),
  `OPENEMR_HERMES_BRIDGE`, `RISPACS_HERMES_BRIDGE`. **Never redeploy-fresh to reset it.**
- New admin pw sealed: `/opt/data/mirth-oie-admin.txt` (0600). PG user `mirth`, db `enginedb`.

### 5.2 Radiology CXR vertical slice — VERIFIED (SHADOW_ONLY)
- Model: TorchXRayVision DenseNet-121 (`models/cxr_triage.py`) on Lab `torch 2.13`.
- Real results: COVID CXR → top **mass 0.678 / lung-opacity 0.658** → **CRITICAL** + must-not-miss;
  adult normal CXR → top **0.629** → **INDETERMINATE** (abstain gate top-1<0.65).
- **The model is UNCALIBRATED** → `deployment_status: SHADOW_ONLY`, `requires_provider_review`,
  5-assertion separation (image≠feature≠abnormal≠disease≠provider-diagnosed). Promote only after
  AUC + calibration + external validation + clinical governance.

### 5.3 Model Gateway — BUILT + VERIFIED
- `services/model_gateway/`: `router.py`(GatewayRouter.reason), `routing.py/.yaml` (task-driven),
  `schemas.py` (radiology reasoning I/O contract), `tool_registry.py` (14 allow/12 deny),
  `phi_policy.py` (redacts MRN/DOB/phone, whitelists internal), `policy.py` (escalate+review),
  `consensus.py` (flag disagreement, never average), `retry.py`, `telemetry.py`, `audit.py`,
  `providers.py` (DeepSeek/OpenAI/Local/Stub). Verified `GATEWAY-VERIFY-PASS`; two defects fixed
  (StubProvider stray method, telemetry missing json import).

### 5.4 Foundation artifacts
- `model-registry/registry_schema.sql` — dataset_registry / dataset_version / model_registry /
  routing_policy (Dataset Gateway + model registry, spec §15/§47).
- `events/README.md` — Hermes radiology event catalog + canonical envelope (refs, never payloads).
- `EMR-RISK-GATES.md` — the EMR risk-containment doctrine (AI DRAFT → provider review → final only).
- `storage/B2-STORAGE-BLUEPRINT.md` — buckets, Orthanc S3 plugin, storage_object schema, keys.

### 5.5 Media Engine MVP — BUILT + RUNNING
- `apps/orchestrator.py` proves script→render(FFmpeg)→QA(ffprobe)→generation_ledger→store(B2).
  Ran `MEDIA-MVP-PASS` (1280x720, 2.0s, output_sha256, zero cost).
- `infrastructure/media_schema.sql` — generation_ledger / media_model_registry / media_job /
  authorized_identity_registry (the "all databases" durable record).
- Providers: local-first (ComfyUI/Wan/LTX/FLUX/HeyGem/MuseTalk/LivePortrait/OpenCut/FFmpeg) with
  commercial fallback (HeyGen/Higgsfield/CapCut) behind the router; **no hard dependencies.**

## 6. Git / repo / Notion / DB conventions
- **GitHub:** `eddieg73/NURA` monorepo. Push via `GIT_SSH_COMMAND` + `id_github`. **Feature
  branches, PR to `main`/`master`; never push to protected production branches.**
- **Notion = mirror only**; **Obsidian VAULT = memory authority**. Specs/history vault-first;
  mirror the day's arc to Notion daily.
- **Databases:** schemas live in the repo (`model-registry/registry_schema.sql`,
  `nura-media/infrastructure/media_schema.sql`). Never raw DB writes to OpenEMR (API only).

## 7. Security & clinical gates (non-negotiable)
- No PHI in media prompts / external calls (phi_policy strips). Medical-edu = synthetic/
  de-identified. **External medical publish requires human clinical approval** (Hermes prepares,
  never bypasses the gate).
- **Voice/face/avatar cloning only for identities in `authorized_identity_registry`.**
- Zero secrets in git; env-based secrets; least-privilege credentials; signed storage URLs;
  per-service app keys; tenant isolation; no `latest` (pin versions).

## 8. How to operate (quick ref)
- Mirth admin (Clinic): `curl -sk -u admin:<pw> -H 'X-Requested-With: OpenAPI' https://127.0.0.1:8445/api/...`
- Re-run the CXR contract: `ssh lab "/opt/radiology-venv/bin/python /tmp/nura/cxr_triage.py <cxr>"`.
- Re-run the gateway verify: `python nura-radiology-ai/services/model_gateway/verify_gateway.py`
  (or the inline `-c` form if the shell guard misfires).
- Re-run the media MVP: `python3 /opt/data/nura-media/apps/orchestrator.py`.
- Orchestrator not yet deployed to Clinic (needs compose up + Lab model call) — staged, not live,
  correctly (SHADOW + dev on a non-HIPAA host until the BAA host + B2 BAA exist).
