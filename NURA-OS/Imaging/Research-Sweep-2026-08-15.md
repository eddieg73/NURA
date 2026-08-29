# NURATECH.ai Clinical Infrastructure — Research Sweep
*Compiled 2026-08-15 · Sources: GitHub, HuggingFace, PyPI, vendor docs, community blogs (via web search). Unverified claims marked ⚠️. YouTube was NOT used (VPS IP-blocked).*

---

## 1. AI in Radiology — Open-Source Readers (Orthanc/Docker-deployable)

**TotalSegmentator** — the workhorse segmentation model. https://github.com/wasserth/TotalSegmentator
- Segments 100+ anatomical structures in any CT/MR. Apache-2.0. Input: NIfTI **or a folder/zip of DICOM slices**; outputs DICOM-SEG (`--output_type dicom_seg`, needs `highdicom`) or RTSTRUCT (`rt_utils`).
- Official Docker: `docker run --gpus 'device=0' --shm-size=16G -v /data:/tmp wasserth/totalsegmentator:2.11.0 TotalSegmentator -i /tmp/ct.nii.gz -o /tmp/segmentations`. v2.11.0 current.
- **Now ships a built-in MCP server** (stdio/HTTP, Claude Code/Cursor instructions in `totalsegmentator_mcp/README.md`) — the fastest path to agent-driven segmentation.
- `--fast` / `--fastest` flags for 3mm/6mm resolution speedups; `--roi_subset` for targeted tasks.

**nnunet_serve** — production-grade nnU-Net/TotalSegmentator API with native Orthanc. https://github.com/josegcpa/nnunet_serve
- Docker container exposing a REST API + CLI; DICOM/NIfTI in → NIfTI/DICOM-SEG/RTSTRUCT out; model cascades; SNOMED-CT/EUCAIM metadata auto-population.
- **Direct Orthanc integration via env vars**: `ORTHANC_URL`, `ORTHANC_USER`, `ORTHANC_PASSWORD` (defaults `http://localhost:8042`). Port 50422, GPU via `--gpus all`, `MAX_REQUESTS_PER_MINUTE` default 10. License ⚠️ not verified — check before commercial use.

**MONAI Deploy** — the standard for packaging AI as clinical apps. https://github.com/Project-MONAI/monai-deploy · https://monai.io/deploy.html
- Apache-2.0. App SDK v3.0 (Apr 2025, Holoscan SDK v3-based, Triton remote inference supported). MAP = containerized app: DICOM in, DICOM-SEG/SR/PDF out. `monai-deploy package … --platform x64-workstation` builds a runnable Docker image. Informatics Gateway handles DICOM/FHIR I/O; pairs natively with **mercure** as the runtime orchestrator. Operators: `DICOMDataLoaderOperator`, `DICOMSeriesSelectorOperator`, `MonaiBundleInferenceOperator`, `DICOMSegmentationWriterOperator`. Reference: Mayo Clinic runs MONAI MAPs in clinical radiology pipeline.

**Chest X-ray classifiers:**
- **torchxrayvision** (mlmed) — https://github.com/mlmed/torchxrayvision — Apache-2.0, pip-installable, pretrained DenseNet121 weights for NIH/RSNA/CheXpert/PadChest/MIMIC (18 pathologies). Most practical: wrap in a ~100-line FastAPI + Docker service reading DICOM→PNG. PyPI v1.4.0.
- **CheXzero** (rajpurkarlab) — https://github.com/rajpurkarlab/CheXzero — MIT, zero-shot CXR pathology detection (Nat. Biomed. Eng 2022), radiologist-parity on CheXpert. Gotcha: expects images in a single `.h5`; research-grade, no serving layer — use for R&D, torchxrayvision for deployment.
- **RadImageNet** — ImageNet-style pretraining dataset (~1.3M images) whose weights transfer to small datasets; useful as a backbone init, not an off-the-shelf reader. No maintained serving project found ⚠️.

**LLM report readers (newest wave):**
- **CCI-Bonn/OHIF-AI** — https://github.com/CCI-Bonn/OHIF-AI — OHIF viewer + server-side AI: SAM2/MedSAM2/SAM3/nnInteractive/VoxTell interactive segmentation AND radiology-style **report generation from 3D CT/MRI** via local MedGemma (HF), Gemini/GPT/Claude APIs, HF router (Kimi/Qwen/Gemma 4) or self-hosted vLLM (InternVL). Docker compose + `.env` keys; `bash start.sh`; localhost:1026. Apache-2.0 (OHIF lineage) ⚠️ verify.
- **odelia-viewer-platform** (StratifAI-Research) — https://github.com/StratifAI-Research/odelia-viewer-platform — EU ODELIA project: OHIF + Keycloak OIDC + Orthanc + **Orthanc Router** that routes studies to AI models and wraps results as DICOM; MedGemma MRI (HF_TOKEN) + MST classification (auto-downloaded weights).

## 2. Orthanc PACS + AI Integration

**mercure DICOM Orchestrator** — the reference AI-routing layer. https://github.com/mercure-imaging/mercure · https://mercure-imaging.org/docs
- Python + DCMTK; routing rules + processing modules **as Docker containers**; native MONAI MAP support; web GUI + monitoring; single-server via Docker Compose or Nomad cluster. Current 0.4.0-beta.7. **Ships an Orthanc+OHIF quickstart in its docs.** License Apache-2.0 ⚠️ verify.

**Orthanc official AI gateway sample** — https://github.com/orthanc-server/orthanc-setup-samples/tree/master/docker/ai-gateway
- Canonical pattern: site gateway anonymizes series → STOW-RS to cloud Orthanc → AI adds "- PROCESSED" series → gateway polls QIDO/WADO-RS, re-identifies via local KV store, C-STOREs back to local PACS. Includes authorization-service + api-key auth. Direct template for NURA's PACS↔AI lane.

**nnunet_serve** (above) — env-var-level Orthanc integration; **medai-segmentation-server** (npm) — https://www.npmjs.com/package/medai-segmentation-server — MCP server driving a Docker pipeline: pull/push series from Orthanc, dcm2niix → TotalSegmentator → DICOM-SEG, stats JSON, conversational PACS query.

**OHIF**: NURA already runs `ohif/viewer` — point its DICOMweb config at `orthanc:8042/dicom-web`. For AI-in-viewer, evaluate OHIF-AI (above) as a drop-in replacement image.

## 3. RADIS (openradx/radis)

https://github.com/openradx/radis · docs: https://openradx.github.io/radis/ · PyPI client: `radis-client`
- **Latest: v0.7.0 (2026-05-11)**, 15 releases, very active (last push 2026-07-03). AGPL-3.0-or-later. 14★, 8 contributors. Research-only (not a medical device).
- Stack: Python 3.12+ / Django 5.1+ / **PostgreSQL 17 + pgvector + pg_search hybrid search** / Procrastinate task queue / HTMX+Alpine.js. **Deploys via Docker Swarm** (local-first, hospital data stays on-prem) with provided scripts.
- Hot PRs: #226 hybrid search (PG FTS + Qwen3-Embedding-4B dense vectors, RRF fusion, HNSW; degrades to FTS-only if embedder down); #231 auto-labeling (LLM gate-question + 5-bucket PRESENT/LIKELY/POSSIBLE/ABSENT/UNMENTIONED, nightly scan, partial-unique-index singleton job).
- Gotchas: (1) early phase — breaking changes expected; (2) **hybrid search is negation-blind** ("no pneumothorax" ≈ "pneumothorax") — known issue for radiology, mitigation in flight; (3) semantic features need an LLM — OpenAI-compatible API or local llama.cpp; (4) needs Postgres 17 + pgvector image (`pgvector/pgvector:pg17`); (5) Swarm-based deployment may need translation to plain compose on a single Hostinger VPS.
- **No HuggingFace org/models found** — project lives entirely on GitHub/docs/PyPI.
- Companion: **ADIT** (same org) — https://github.com/openradx/adit — web-fronted DICOM transfer utility with DICOMweb client (useful as Orthanc↔RADIS glue).

## 4. OpenEMR — Docker, FHIR, Mirth

**Official production compose**: https://github.com/openemr/openemr/tree/master/docker/production — `openemr/openemr` + `mariadb:11`, healthchecks (`service_healthy` + `depends_on` conditions), env: `MYSQL_HOST`, `MYSQL_ROOT_PASS`, `OE_USER/OE_PASS`. Pin tags (`7.0.2`, `8.0.x`), never `latest`. Volumes: `sitevolume` (sites/ = config + documents) + `logvolume01`. amd64+arm64. Auto-install runs on first boot when env set — healthcheck should gate on `sites/default/sqlconf.php` existing.
- **Hostinger VPS notes**: min 4 GB RAM VPS for OpenEMR+MariaDB+Mirth alongside the imaging stack; keep DB port private (NPM proxies :443 only); daily `mysqldump` off-box.
- **FHIR**: built-in FHIR R4 server at `https://<host>/apis/default/fhir` — enable via **Admin → Globals → Connectors** (also register an OAuth2 client for API access). Older "push to external HAPI FHIR" flow still exists but native R4 API is the modern path.
- **HL7 out**: OpenEMR has no native TCP/MLLP push — the proven NURA pattern (from our runbooks): ORM via Procedure `Mirth_Radiology_Routing` → local dir `/opt/openemr/hl7_out/` + pusher script to Mirth :6002 (MLLP, move to `sent/` on ACK, `failed/` on error); ADT via Mirth **Database Reader** polling `patient_data` with read-only SQL user. Verified working against ThaiRIS :6001/:6002.

## 5. Mirth Connect / OIE / Ballista

**OIE (Open Integration Engine)** — https://github.com/OpenIntegrationEngine/engine · docker: https://github.com/OpenIntegrationEngine/engine-docker — community fork of Mirth 4.5.2, MPL-2.0. Images: `openintegrationengine/engine` (+alpine/ubuntu, jre/jdk tags, amd64+arm64). **Postgres backend via env**: `DATABASE=postgres`, `DATABASE_URL=jdbc:postgresql://db:5432/enginedb`, `DATABASE_MAX_CONNECTIONS`, retry settings; compose `stack.yml` example in repo. `VMOPTIONS=-Xmx512m` for heap.
- **Ballista launcher** — https://github.com/kayyagari/ballista — Tauri-based admin launcher (replaces Java Web Start; JRE 8+ on host), dark theme, connection manager, works with Mirth/OIE/BridgeLink. NextGen MCAL is the commercial alternative.
- **BridgeLink** (Innovar Healthcare fork, MPL-2.0) — third option. Commercial Mirth 4.6+ = NextGen paid license; **last open-source Mirth = 4.5.2**.
- **Channel templates**: nextgenhealthcare/connect-examples (code templates + example channels) — https://github.com/nextgenhealthcare/connect-examples. **openemr-hl7v2-bidirectional recipe** (Nirmitee mirth-connect-cookbook) — PID-2 vs PID-3 MRN promotion, phone normalization, HL7 escape handling. Patterns that matter (nirmitee.io): content-based router → per-type channels; ADT fan-out; dedicated ERROR_HANDLER channel; keep thread count 1 for order-sensitive flows (A01 before A03).
- **DICOM nuance (conflicting vendor claims — both true in different versions)**: Mirth's strength is HL7 + **DICOMweb over HTTP** (QIDO/WADO/STOW via HTTP Sender). Raw DICOM protocol (C-STORE/C-FIND/C-MOVE) historically requires pairing with **Orthanc or dcm4che**; newer Mirth/OIE builds include DICOM Listener/Sender connectors ⚠️ — verify in your exact OIE release before relying on it. Recommended NURA posture: **Mirth = HL7 + DICOMweb plane; Orthanc = raw DICOM plane** (already matches our live stack).
- Postgres tips: never run Derby in prod; watch `d_` message tables growth; prune stats; PG 13+.

## 6. MCP Connectors for Healthcare (2026 state)

- **openemr-mcp** (PyPI v0.1.0) — 17 tools (patient search, meds, FDA drug safety, lab/vital trends, visit prep); sources: `mock` (24 patients, zero-config eval) / `db` (direct MySQL) / `api` (**FHIR R4 + OAuth2** — recommended for prod). `uvx openemr-mcp`.
- **TotalSegmentator MCP** (built-in) + **medai-segmentation-server** (npm) + **dcmclient MCP** — https://github.com/dcmkit/dcmclient — single static binary, 65 DICOM tools, `dcmclient mcp` serves them over stdio; `manifest` emits JSON schemas; Apache-2.0. Covers DICOM agent-ops in one install.
- **MCP + n8n** (three modes): MCP Server Trigger (n8n publishes workflows as tools — this is how you build an "n8n MCP"), MCP Client Tool (agent borrows external tools), and the **instance-level n8n MCP server** (Public Preview Apr 2026, self-hosted CE ≥ v2.18.4) letting Claude/Cursor build workflows. Use **Streamable HTTP** transport (SSE deprecated in 2026; SSE behind reverse proxies drops connections).
- **Best practices 2026** (firearrow.io FHIR-MCP architecture paper + chatforest guide): trust boundary at the **FHIR backend**, not the prompt; two-layer identity (agent + on-behalf-of user); narrow clinical-action tools (read-only by default); idempotency keys on writes; stateless proxy (no PHI persistence); PHI-scrubbed logs; patient-scoped SMART-on-FHIR tokens; audit correlation IDs. MCP passed 97M installs (Mar 2026); Innovaccer pushing **HMCP** healthcare extension; 2026 HIPAA Security Rule proposal makes encryption-at-rest, MFA, annual pentesting mandatory — design for it now.

## 7. n8n — Healthcare Automation (self-hosted)

- **Self-host on the VPS**: `N8N_ENCRYPTION_KEY` mandatory (else credentials plaintext); Postgres backend (execution history = audit trail; `EXECUTIONS_DATA_MAX_AGE` for retention; 6-year HIPAA documentation floor); reverse proxy TLS (NPM/Caddy); webhook HMAC verification; disable public API unless needed; RBAC per user.
- **Patterns**: webhook patient intake → validate → FHIR create; poll FHIR `Appointment` every 30 min → Twilio/SMS reminder with reply-driven confirm/reschedule (writes back via FHIR); lab result webhook → parse → route + critical-value alerts; AI Agent node with human-in-the-loop approval on any send/delete tool. bonFHIR community node gives native FHIR node support (https://bonfhir.dev/docs/build-workflows-with-n8n). Template: "Orchestrate patient admission/discharge with NVIDIA+Claude" (n8n.io/workflows/13308).
- **BAA**: n8n Cloud requires a signed BAA; self-hosting shifts BAA duty to your infra provider (Hostinger — check BAA availability ⚠️; if none, treat VPS as your own infra boundary and keep PHI flows internal).

## 8. Twilio — Patient Messaging

- **BAA required** for any PHI: twilio.com/hipaa → sign Business Associate Addendum (Security/Enterprise editions); use only **HIPAA-Eligible Products** (SMS, Voice, Video, and — since June 30, 2026 — Consent Management API). WhatsApp Business API historically NOT HIPAA-eligible ⚠️ verify current list before routing PHI.
- **SMS guidance** (Twilio blog + OCR comments): reminders without PHI are low-risk; PHI in SMS requires patient consent + documented warning that SMS is unsecure; verify phone numbers at capture (2FA code), re-verify at visits.
- Patterns: appointment reminders (biggest no-show reducer; $150B/yr missed-appointment cost), waitlist fill, med reminders, post-op instructions, two-way confirm/reschedule. n8n+Twilio+FHIR is the standard low-code combo (see §7).

## 9. Hostinger VPS — Docker Best Practices for Healthcare Stacks

- Hostinger VPS = KVM; Docker via Docker Manager or SSH. **Cloud firewall is a separate gate from iptables** (known NURA pitfall — public 000s were the cloud firewall).
- Hard rules (virtua.cloud + 1vps + eastondev guides, all consistent):
  1. **Pin image tags**; healthchecks + `depends_on: service_healthy`; `restart: unless-stopped`.
  2. **Memory/CPU limits on every container** (`deploy.resources.limits`); DB 2–4 GB, Java (Mirth) 1–2 GB + `-Xmx`, PHP 1 GB; load-test then ×1.5.
  3. **Swap**: set `--memory-swap` = memory (disable) or ≤ +50%; unlimited swap (`-1`) thrashes the disk. This VPS has a known swap-full history — apply strictly.
  4. **Log rotation**: `/etc/docker/daemon.json` json-file `max-size`; weekly `docker system prune` cron.
  5. **Network**: expose only 80/443 via NPM; DICOM 4242 and DB ports private; `iptables DOCKER-USER` rules (Docker bypasses UFW by default).
  6. Named volumes + encrypted off-box backups (mysqldump/pg_dump + GPG).
  7. Min 4 GB RAM / 40 GB NVMe for a 5–8 container clinical stack; monitor `docker stats` + htop; upgrade plan before swap thrash begins.

## 10. CLI Tooling for Radiology Ops

- **DCMTK 3.7.0** (`apt install dcmtk`) — echoscu/storescu/storescp/findscu/movescu/dcmdump/dcm2json/dcmodify. The AET↔host↔port sanity-tester is `echoscu <ip> <port> -aet <AET> -aec <AET>`.
- **dcmclient** (dcmkit) — one static binary, 65 tools incl. DICOMweb verbs (`search/pull/push/forward`, `qido/wado/stow/ups`), transcoding (JPEG-XL/HTJ2K), de-identification, radiomics, + MCP/manifest. Apache-2.0.
- **dicomweb-client** (JS/npm, dcmjs-org) — STOW/QIDO/WADO-RS for scripts/Node tools; pairs with OHIF ecosystem. "Not for clinical use" disclaimer.
- **dcm4che** — Java toolset (`dcm4che-tool-storescu`, `findscu`, `hl7snd` etc.) — heavier but the industry standard for DICOM+HL7 conformance testing.
- **Python**: `pydicom` + `pynetdicom` (DICOM network SCP/SCU) + `python-hl7` (parse/build HL7) + `hl7apy` — base for NURA's existing `send_mllp.py` simulator.
- **dcm2niix** (rordenlab) — DICOM→NIfTI for any AI pipeline.
- **PACSAdminTool** (bobvmierlo) — https://github.com/bobvmierlo/PACSAdminTool — portable web/desktop DICOM+HL7 workstation: QIDO/STOW/WADO-RS, C-STORE send, **HL7 MLLP send/receive with ORM/ORU/ADT/SIU templates** — ideal for ThaiRIS/Orthanc UAT without writing code.

---

# Top 10 Recommendations for NURATECH.ai This Week

1. **Deploy TotalSegmentator in Docker on the imaging VPS** and wire it to Orthanc via the env-var pattern (nnunet_serve `ORTHANC_URL` or the official ai-gateway compose). Shadow-mode only; DICOM-SEG roundtrip proof-of-concept closes the first NURA Rad cascade gap.
2. **Adopt mercure as the DICOM orchestration layer** between Orthanc and AI modules — routing rules + Docker modules + native MONAI MAP support = the long-term AI gateway, replacing ad-hoc scripting.
3. **Pilot OHIF-AI (CCI-Bonn)** as a drop-in upgrade to the current `ohif/viewer` image — interactive segmentation + VLM report drafts directly against DICOMweb; matches the NURA Rad "cascade v0" spec.
4. **Install dcmclient on the VPS** — one binary gives agent-driven DICOM ops (QIDO/WADO/STOW, validation, de-identification) plus an MCP surface for Hermes.
5. **Evaluate openemr-mcp in mock mode** (zero-config), then wire to OpenEMR's FHIR R4 API + OAuth2 — instant agent access to the EHR without building custom connectors.
6. **Pilot OIE (OpenIntegrationEngine) Docker + Postgres** as the Mirth lane successor (MPL-2.0, no NextGen license risk); keep the existing Mirth 4.5.2 channel XML as golden templates and validate via REST before cutover. Use Ballista for admin access.
7. **Deploy RADIS 0.7.0** (Docker Swarm or translated compose) as the radiology report archive; feed it ThaiRIS/Orthanc reports; use `radis-client` for ingestion. Note AGPL + research-only status; track PR #226/#231 (hybrid search + auto-labeling) before relying on semantic search.
8. **Self-host n8n on the VPS** with `N8N_ENCRYPTION_KEY` + Postgres + NPM TLS; build the Twilio appointment-reminder workflow (FHIR poll → SMS with reply-confirm); enable MCP Server Trigger to expose it to agents. Sign a Twilio BAA and keep PHI out of SMS until patient consent is documented.
9. **Harden the Hostinger stack this week**: pin all image tags, add `deploy.resources` limits + swap caps + log rotation to ThaiRIS/Orthanc/OHIF composes, and finish sealing the known default credentials (orthanc/orthanc, admin/admin123) — the highest-risk open items on the live stack.
10. **Standardize the Mirth channel library**: import connect-examples code templates, refactor into content-based router + fan-out ADT + dedicated ERROR_HANDLER channels, and document the DICOM plane split (Mirth = HL7/DICOMweb; Orthanc = raw DICOM) as the standing architecture decision.
