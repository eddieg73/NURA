# NURA ECOSYSTEM — MASTER INDEX (the "look-from" spine)

> Single navigation map for the entire NURA platform. Everything is **divided → categorized →
> sectioned → explained**, and every subsystem is linked to: where it lives (repo path / skill /
> server / service), its status, and its owner-rule. Start here.

**Legend:** `[R]`=repo path · `[S]`=skill · `[Srv]`=service/server · `[OK]`=verified · `[WIP]`=in progress · `[GATED]`=blocked/needs decision

---

## 0. MASTER NOMENCLATURE (the mental model)
```
HERMES  = the nervous system  (workflow, tools, events, safety, audit) — model-agnostic
MODEL GATEWAY = the reasoning cortex  (DeepSeek cloud / Qwen3-BioMistral local, replaceable)
IMAGING MODELS = the visual cortex    (TorchXRayVision, qwen3-vl, MONAI) — structured findings FIRST
ORTHANC = imaging memory · B2 = durable object memory · POSTGRES = structured memory
REDIS = working memory · QDRANT = semantic memory · PUBMED/FDA = external knowledge
MIRTH/FHIR = clinical interoperability · OHIF = provider visual interface
NURA-MEDIA = the media engine (script→generate→edit→QA→store→publish, provider-router)
```

---

## 1. INDEX BY DOMAIN (A–P)

### A. VISION & GOVERNING DECISIONS → `docs/NURA-ECOSYSTEM.md` · [S]nura-fleet-command
- NURA Provider Labs · PRIME DIRECTIVE (one app, all EMRs via FHIR/SMART/HL7) · RATCHET+RCM
- NURA Agent OS (Hermes = one interchangeable runtime, no vendor lock-in)
- Governing rules: A1 Hermes=spine · A2 Dataset/Knowledge Gateway · A3 radiology report contract ·
  A4 EMR risk gate · A5 broker=JetStream(+Redis transient) · D1-D4 HIPAA/Storage · MD1 media local-first

### B. ARCHITECTURE → `services/model_gateway/` · `events/README.md` · [S]nura-systems-architect-persona
- Event backbone (canonical envelope: refs not payloads) · outbox/inbox · model-agnostic
- [OK] Model Gateway (`reason(task,payload)`) → routing → policy → consensus → retry → schema → audit

### C. CLINICAL STACK → [Srv]Clinic · [S]nura-clinical-*
- [Srv] OpenEMR (`openemr-zklo`, :32768) — via API/MCP only, never raw DB writes (sidecar)
- [Srv] Mirth/OIE 4.6 (`mirth-oie46`, :8445/:6663) — SOLIS/OPENEMR/RISPACS channels; **admin FIXED**
- [Srv] MedPlum FHIR backbone (Lab) · [Srv] ThaiRIS (:32790) · [Srv] OHIF (:32791)
- [S] sidecar-doctor · openemr-security-hardening · hermes-clinical-* skill family

### D. RADIOLOGY INTELLIGENCE → `nura-radiology-ai/` · [S]nura-imaging-engineer
- [OK] Report contract: NORMAL/ABNORMAL_NONURGENT/URGENT/CRITICAL/INDETERMINATE + ranked diff +
  SEPARATE must-not-miss · 5-assertion provenance
- [WIP-GATED] TorchXRayVision CXR triage = **SHADOW_ONLY** (uncalibrated; abstain gate top-1<0.65)
- [OK] model-registry/registry_schema.sql (Dataset Gateway + model_registry + routing_policy)
- [OK] events/README.md (imaging event catalog) · [OK] EMR-RISK-GATES.md
- Orchestrator: builds valid DICOM-SR + MLLP ORU; NOT yet deployed (dev+shadow, non-HIPAA host)

### E. MODEL LANE (encoder vs generator — decided) → `nura-radiology-ai/services/model_gateway/`
- [OK] Reasoning cortex (generator): cloud **DeepSeek** (PHI-stripped) · local **Qwen3-8B** →
  **BioMistral-7B** → deepseek-r1:8b (CoT). All on Lab Ollama.
- Encoder/NER + embeddings: **Clinical ModernBERT** / BioClinical ModernBERT / nomic-embed-text.
  **GatorTron / ClinicalBERT = ENCODERS — never reason with them.**
- Visual cortex (pixels): qwen3-vl / minicpm-v / llama3.2-vision (Lab) → findings FIRST.

### F. MEDIA ENGINE → `nura-media/` · [S]video-studio-stack · content-video-pipeline
- [OK] MVP proven: script→render(FFmpeg)→QA(ffprobe)→generation_ledger→store(B2). `MEDIA-MVP-PASS`.
- [OK] infrastructure/media_schema.sql (generation_ledger, media_model_registry, media_job,
  authorized_identity_registry)
- Provider router: local-first (ComfyUI/Wan/LTX/FLUX/HeyGem/MuseTalk/LivePortrait/OpenCut/FFmpeg) +
  commercial fallback (HeyGen/Higgsfield/CapCut) — replaceable, no hard dependency.
- [GATED] video+avatar models need GPU (Lab CPU-only; RunPod key 401) → use Hermes FLUX3 now.

### G. STORAGE / DATA FABRIC (HIPAA) → `nura-radiology-ai/storage/B2-STORAGE-BLUEPRINT.md`
- **Hostinger = NOT HIPAA** → dev/non-PHI/synthetic only. **B2 = durable object storage** (BAA first).
- Postgres = state · Redis = transient · Qdrant = semantic · compute = replaceable.
- Buckets: nura-prod-clinical-{imaging,documents,audio} · nura-prod-ai-derived · nura-prod-audit ·
  nura-prod-backups · nura-research-deidentified · nura-datasets-public · nura-model-artifacts · nura-development
- No PHI in object keys (opaque UUID) · Object Lock on audit/backup · least-privilege app keys ·
  signed URLs. Orthanc S3 plugin → B2 (validate w/ synthetic DICOM first).

### H. INFRASTRUCTURE / FLEET → docs/NURA-ECOSYSTEM.md §4 · [S]fleet-*, docker-*, nura-fleet-command
- [Srv] Clinic 72.61.71.211 (control plane: OpenEMR/Mirth/MedPlum/Orthanc/ThaiRIS/OHIF/DocsGPT/
  Chatwoot/Hermes gateway/Perfex/n8n) — **no large AI models**
- [Srv] Lab 72.60.163.140 (CPU: radiology-venv, Ollama, Celery+Redis, Qdrant, n8n, langfuse, medisun)
- [Srv] Edge 195.35.32.113 (nginx-proxy-manager) · **No GPU** anywhere
- [S] docker-architect · fleet-load-distribution · swap-fleet-watchdog · incident-commander

### I. COMMUNICATIONS & CHANNELS → [S]mattermost-*, telegram/@Nuratechbot · email · signal · sms
- Telegram (lifeline, CRITICAL-only) · Gmail (nura@nuratech.ai) · WhatsApp/iMessage (Jade lanes) ·
  Moltbook (beachhead) · Walled: X/Reddit/LinkedIn founder-gated · YouTube ✓
- Delivery doctrine (08-23): scheduled = **weather only**, skip cron notifications.

### J. AVIATION → [S]aviation-* · foreflight-integration · weather-lightning-monitor
- PPL+IR · PA-32R-300 + PA-46 · turboprop/Vision Jet · Avionics → Atlas · ForeFlight · Mesa/Tampa weather

### K. VEHICLES / AV → [S]openpilot-* · obd2-vehicle-telemetry · comma-av-control
- Hermes=brain, openpilot=driver (sim-first, human override). Escape Hybrid 2020-22 = official
  openpilot (Q3 harness + comma four) · dongle ESP32-S3 · OBD2/ELM327 telemetry · LOM/Needle-2.

### L. DRONES / EMS → [S]drone-swarm-division · ems-agency-ops · meshtastic-node-monitor
- Orange Star 🍊 = EMS · 'EMS DRONE' · EMS mesh (:8080, T-Beam client/towers, LoRa custom-PSK) ·
  drone swarm division.

### M. VOICE / AI PERSONA → [S]voice-message-ops · elevenlabs-tts · emh-clinical-persona
- Hermes (JARVIS cadence) · EMH variant (clinical) · Echo :8000 (local) · ElevenLabs (TTS) ·
  Chatterbox/Qwen3-TTS (emotion/cloned) · VAPI (inbound, key dead) · Tavus face (gated).

### N. BUSINESS / CORPORATE → [S]self-hosted-accounting-ops · perfex-mcp · payment-gateway-integrations
- Perfex = pay.nuratech.ai (MCP 183 tools; REST $149 founder-gated) · RCM · NMI payments ·
  Paperclip org (lean healthcare SaaS) · hiring · Solis full-risk MA + Oscar FFS · CarePilot+Ensure.

### O. DATA SCIENCE / DATASETS → [S]kaggle-ops · huggingface-hub · clinical-evidence-lanes
- B2 dataset lake (13.25GB / 3-6 Kaggle) · radiology datasets (COVID-19, MIMIC, VinDr, CBIS-DDSM,
  SIIM) · model training files · Dataset/Knowledge Gateway (license/DUA gated).

### P. SECURITY & COMPLIANCE → [S]agent-security-scanning · credential-bootstrap · openemr-security-hardening
- HIPAA (BAA: B2 + production compute) · credential SOP (SEAL→PROBE→REGISTER→WIRE→DOC→REPORT) ·
  zero secrets in git · least-privilege per-service keys · authorized_identity_registry
  (no voice/face/avatar cloning w/o authorization) · PHI no in media prompts.

### Q. DEVOPS / OPS → [S]master-systems-audit · cron-status-board · docker-health-check-ops
- Docker fleet (48 Clinic / 48 Lab) · cron roster · incident commander · swap/disk watchdogs ·
  monitoring (langfuse, sentry) · hermes-gateway-repair.

### R. AGENT ECOSYSTEM (Hermes agents) → [S]agent-harness-routing · human-team-management
- VERONICA (reception) · AURA (web/brand) · CORA (docs/coding) · JARVIS (radiology) · LEXA (legal) ·
  NURA (clinical intel) · Hermes (spine). Team: Jade (EA/content), Amrit (Flutter), Oussama (VP CRM),
  Nancy (billing), Natalie (CarePilot).

### S. GIT / REPO / NOTION
- [R] GitHub **eddieg73/NURA** (monorepo; `build/` gitignored → use `backend/`, `infra/`, `docs/`).
  Feature branch `nura-platform-builds-2026-08-23` (50 files). SSH push (`id_github`+GIT_SSH_COMMAND).
- Notion = **mirror only** · Obsidian VAULT = **memory authority** (specs/history vault-first).
- REGISTRY.md / REPO-MAP.md in repo.

---

## 2. QUICK "WHICH IS WHICH" (resolution for any task)
| You want to… | Go to |
|---|---|
| Fix Mirth/HL7 | [S]mirth-oie-engine-ops · ssh clinic :8445 (`admin`, pw in mirth-oie-admin.txt) |
| Read a patient | OpenEMR MCP (`get_patient_clinical_summary`) — never raw DB |
| Run the CXR model | `ssh lab /opt/radiology-venv/bin/python .../cxr_triage.py <cxr>` (SHADOW_ONLY) |
| Call an LLM | `model_gateway.reason(task,payload)` (routing→policy→consensus→schema) |
| Generate a video | Hermes FLUX3 tools (now) / nura-media orchestrator (CPU) / GPU workers (GATED) |
| Store a binary | B2 via storage-service (signed URLs, opaque keys, no PHI) |
| Commit code | feature branch on eddieg73/NURA → PR to main/master (never push prod branch) |
| Recall a fact | Obsidian vault (authority) · Notion (mirror) |

## 3. FIND A COMMAND
- Mirth admin: `curl -sk -u admin:<pw> -H 'X-Requested-With: OpenAPI' https://127.0.0.1:8445/api/...`
- Gateway verify: `python nura-radiology-ai/services/model_gateway/verify_gateway.py`
- Media MVP: `python3 /opt/data/nura-media/apps/orchestrator.py`
- Fleet audit: [S]master-systems-audit · api_server/telemetry dashboards.

---
*Maintained 2026-08-23. Sections 0-3 are the index; per-category deep docs live alongside in this KB.*
