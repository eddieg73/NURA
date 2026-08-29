# NURA REPO REGISTRY — GitHub, Fleet, and Upstream Stack

> Master inventory: what every repo does, where it lives, and how it connects.
> Last verified: 2026-08-21 (Hermes, GitHub API + live probes).
> Authority note: this file lives in the NURA monorepo on GitHub AND in the Obsidian vault (vault-real).

---

## 1. OUR REPOS ON GITHUB

### eddieg73/NURA — the canonical monorepo (public)
`git@github.com:eddieg73/NURA.git` · default branch on GitHub UI: `artificial-medic-proposal-10801612749289978288`, working branch: `master`

| Path | What it does |
|---|---|
| `apps/nura_medical/` | The 5-tab NURA Flutter app (clinical / scribe / ops / e6b / account). Flutter SDK 3.47. Login gate = NPI or paramedic license. iOS builds via CodeMagic (Apple Dev ID pending). Local dev: `/opt/data/nura_medical` |
| `ops/scripts/` | The Hermes ops script library: clinical synthesis (`nura-clinical-synthesis.py`, `nura-lab-trends.py`, `nura-dx.py`), fleet manager (`fleetctl.py`, `docker-manager.py`), mso-coder API (`mso-coder/`, port 8643), weatherman (`weatherman-report.py`), Solis puller (`solis-pull-reports.py`), coding agent engine, watchdog/cron tooling. Runtime copy: `/opt/data/profiles/nura/scripts/` |
| `ops/n8n-workflows/` | n8n workflow JSON exports (69 workflows): clinical (lab/OpenEMR/claims/eligibility), EMS/CarePilot, Medisun multi-clinic booking, ElevenLabs voice, Sora/Veo video, GHL/PDFMonkey, KPI reports, Zapier bridge. Credentials file intentionally excluded. Runtime: Edge node n8n container |
| `ops/ems-mesh-monitor/` | Meshtastic/LoRa EMS mesh monitor (T-Beam vehicle clients + Heltec V3 solar towers, custom-PSK, port 8080). Runtime: `/opt/data/meshtastic-monitor` |
| `ops/nura-radiology-intelligence/` | JARVIS radiology lane: ORU/HL7 ingestion (`RISPACS_HERMES :6667`), report orchestration, port 8103. Runtime: `/opt/data/nura-radiology-intelligence` |
| `docs/`, `backend/`, `.github/` | CTO-standard monorepo structure: specs, backend service skeletons, CI |

### Nuratech-ai/hermes-driver (private)
`git@github.com:Nuratech-ai/hermes-driver.git` — Hermes repo-driver: reads/writes repos, issues, agent harness interface. Created 2026-08-03.

### Push mechanics (verified)
- SSH: `id_github` key authenticates as eddieg73 (`ssh -T git@github.com` → "Hi eddieg73!").
- PITFALL: git subprocesses run with `HOME=/opt/data`, which misses `~/.ssh/config` — export `GIT_SSH_COMMAND="ssh -i /opt/data/profiles/nura/home/.ssh/id_github -o IdentitiesOnly=yes"` before pushing.
- The GitHub MCP PAT (fine-grained) is scoped to `eddieg73/NURA` only — read + repo ops on NURA, CANNOT create new repos (403 verified). New repos must be created from the web UI or with a classic PAT, then pushed via SSH.

---

## 2. FLEET + WIRING (how everything connects)

| Node | IP | Role |
|---|---|---|
| Clinic | 72.61.71.211 | OpenEMR, OIE/Mirth, ThaiRIS, orthanc-pacs, Solis/CarePilot lanes |
| Lab | 72.60.163.140 (32GB) | WEB (Traefik/Dokploy), Medplum FHIR backbone, Ollama (11434, tunneled), B2 ops |
| Edge | 195.35.32.113 | n8n (`n8n-n8n-6tp2rd-n8n-1` + `code-n8n-1`), Dokploy apps |
| Hermes box | (this host) | Gateway :8642, Redis 6379, Qdrant 6333, Tailscale, meshtastic :8080, mso-coder :8643 |

Key lanes:
- **Mirth/OIE 4.6.0** (Clinic): admin :8445, MLLP :6663. Channels: `SOLIS_ENSURE_INBOUND`, `OPENEMR_HERMES :6666`, `RISPACS_HERMES :6667` → radiology-intel, MLLP → `solis_hermes :6665`, ORU :6668. XML 3.8.0 only.
- **OpenEMR**: API-only writes (never DB), sidecar doctrine: chart in NURA → OpenEMR = internal truth → NextGen → destination EMR.
- **Perfex** = pay.nuratech.ai. 183-tool MCP at `/opt/data/mcp-installs/perfex/server.py`; REST API = founder-gated. Perfex never stores clinical data.
- **n8n (Edge)**: API port NOT published — operate via `docker exec` CLI. 13 live workflows incl. `nura-mesh-llm-001|NURA-Mesh-LLM` (Ollama via WireGuard `http://10.10.0.2:11434/v1`), `Eddie Agent`, Vapi call lanes, `HRT`.
- **Imaging**: ThaiRIS 1.8 = NURA RIS (Clinic `/docker/nura-ris`), OHIF mesh :8451, orthanc-pacs, Sirius RIS = eval alternative.
- **Mem0/Qdrant**: embedded mem0 store at `~/.hermes/mem0_qdrant` + Qdrant server 6333 (`/opt/data/qdrant-server/config.yaml`). Stale `.lock` in the embedded dir was removed 08-21; if "already accessed by another instance" persists, restart the gateway so exactly one client opens the embedded store.
- **Storage**: Backblaze B2 us-east-005 (6 nura-* buckets), RustFS hot S3.
- **Mesh**: Tailscale + WireGuard 10.10.0.2; SSH keys: `id_nura_clean` (fleet root), `id_github` (GitHub).
- **MCP lanes wired in Hermes** (live, from config.yaml + tool catalog): github, obsidian, firecrawl, chrome, qdrant, redis, bioportal, cdc, documo, elevenlabs, firebase, freemedical, gemma4, googleflow, granola, hostinger (api/billing/dns/domains/hosting/reach/vps), legal-case-law, mirth, moltbook, notebooklm, nothumansearch, openemr, openemr-clinical, openevidence, openfda, provider_labs, runpod, twilio-docs, gemini (in-house `/opt/data/mcp-installs/gemini/server.py`).
- **X (Twitter)**: `xurl` CLI installed; NO auth configured (OAuth via `xurl --headless` = founder-gated).

---

## 3. UPSTREAM REPOS WE DEPEND ON (full inventory, 2026-08-21)

### Orthanc — canonical dev is Mercurial (`hg.orthanc-server.com`); GitHub = mirrors
- **orthanc-server org (6)**: orthanc-setup-samples, orthanc-explorer-2 (new UI), orthanc-builder (docker/win/osx builds), orthanc-worklists (DICOM worklist plugin), orthanc-pixels-masker (anonymize/modify pixel masking), orthanc-advanced-storage.
- **orthanc-team org (10)**: orthanc-auth-service (study sharing), python-orthanc-api-client, python-orthanc-tools, orthanc-demo, osimis-webviewer-deprecated, dicom-dicomweb-proxy, ot-logging-helpers, orthanc-monitoring, osisync, dicom-web-forwarder (Lua DICOMweb forwarder).
- **jodogne (30, incl. 21 Mercurial mirrors)**: Orthanc (original core), OrthancDocker, OrthancMirror, OrthancContributed, wasm-dicom-parser, orthanc-mammography (DL mass detection), dicom-specification, mirror-orthanc-{indexer,stl,education,webviewer,authorization,ohif,dicomweb,python,gcp,object-storage,imagej,neuro,gdcm,databases,tests,transfers,stone,volview,book,java,tcia,wsi}.
- **We run**: orthanc-pacs (Clinic) + MCP lanes `orthanc-mcp.py` and `ag2-mcp-servers/orthanc-api` (OpenAPI-generated, spec v1.11.3).

### RIS
- **SoftwareThaiRIS (3)**: thairis18free (DEPLOYED as NURA RIS, Clinic `/docker/nura-ris`), thairisfree15 (PHP7), thairisfree10 (PHP5). Local fork: `/opt/data/imaging-stack/www` (thairis18free).
- **opendicom/sirius-ris**: open-source RIS, active (pushed 2026-08-21). Local study copy: `/opt/data/docs/sirius-ris`. Eval candidate vs ThaiRIS.

### OpenEMR — openemr org (31 repos)
Core: openemr/openemr. Ops: openemr-devops, openemr-on-ecs, openemr-on-eks, docker-madness, demo_farm_openemr. Quality: oe-cqm-service, cqm-parsers, oe-cqm-parsers, oe-cda-schematron, oe-schematron-service, oe-module-cqm. Extensions: oe-module-faxsms (fax/SMS), oe-module-installer-plugin, contrib-encounter-forms, sunset-patient-portal, smart-on-fhir-standalone-skeleton-app, app-flutter-openemr, app-golang-openemr. Support: demo-data-generator, translations_development_openemr, wkhtmltopdf-openemr, website-* , wiki-openemr, drupal-theme, foundation-minutes, openemr-analytics, blue-button.

### Perfex — NO official core on GitHub (closed, CodeCanyon); community only
- MCP lanes: Descomplicar-Marketing-e-Tecnologia/mcp-perfex-crm (30+ tools, MySQL direct) + mcp-perfex-crm-sql; Biftekic/PerfexCRM-MCP; parthamjangir2020/claude-connector-perfexcrm.
- n8n: OBSTechnologies/n8n-nodes-perfexcrm (API + webhooks).
- Deploy/dev: ferronicardoso/perfexcrm-docker, 0x1100010010/perfex-crm (docker), LunarDevelopment/PerfexCRM-Module-Boilerplate, danielwpsouza/perfex-module-builder, Yuri-Lima/Perfex-Hook-List, abcoder0101/perfex-dev-tools (VSCode), Granulr/perfex_calls.
- **Ours**: 183-tool custom MCP (built in-house) at `/opt/data/mcp-installs/perfex` — this is what wires pay.nuratech.ai into Hermes.

---

## 4. KNOWN GAPS / NOTES (08-21)
- Gateway: UP (health ok, v0.20.0, PID 1416912 manual). Model now deepseek-v4-pro via DeepSeek (was gpt-5.6-luna on OpenAI → "no credits remaining" 20:33/20:40 = the earlier "model not running" cause).
- Vision lane: Gemini fallback 404 + local ollama llama3.2-vision 500 → screenshot analysis degraded. Fix = point vision fallback at a live model.
- mem0: stale embedded-Qdrant lock removed; restart gateway if contention persists.
- Hermes upgrade pending: v0.20.0 → Hub v2026.8.18 (docker pull, blocked).
- X lane needs OAuth re-auth before "Check X" requests can run.

### 08-28 CTO Session Ledger
- `docs/CTO-Session-Ledger-2026-08-28.md` — sovereign free-first model lane (dock Ollama :11435, qwen2.5:3b verified) + Telegram gateway fix (valid @Nuratechbot token, s6 restart, connected).

### Medisun Health-Ware (sovereign clinical edge, 2026-08-28)
- `medisun-health-ware/` — ingest bridge (:8108) + clinic identity/safety-cam flow (:8107 face lane) + wearable firmware skeleton + spec. Local-first, provider-gated, PHI-safe. See README.md + SPEC.md.

### CLI-Anything audit + wire-in (2026-08-28)
- Audited HKUDS/CLI-Anything (Apache-2.0): all 79 CLIs = pip strategy (no shell=True); telemetry ON by default -> disable with CLI_HUB_NO_ANALYTICS=1. Adopted methodology as skill `gui-to-cli-harness`. Wired (verified live): cli-anything-ollama (drives sovereign dock :11435 -> "OK"), cli-anything-exa (EXA_API_KEY valid, live CMS 2026 risk-adjustment search). Venv /opt/data/cli-anything-venv.
