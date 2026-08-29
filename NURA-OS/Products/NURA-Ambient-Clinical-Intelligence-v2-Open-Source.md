# NURA — Advanced Ambient Clinical Intelligence Platform
## Reference-grade blueprint v2.0 (2026-08-19) — the ALL-OPEN-SOURCE stack (the replaces the commercial v1.0)

The v1.0's the every commercial dependency → the our open equivalents. The reference only.

---

## 1. Purpose & Vision
The NURA listens, thinks, and documents in the background — the every encounter becomes the structured, billable, HIPAA-secure data while automating the orders, the prescriptions, the imaging, and the follow-up across the OpenEMR, the Perfex, the NURA PACS/RIS, and the e-prescribing hubs. The vendor-neutral, the local-first, the $0 inference.

## 2. High-Level Feature Matrix (the open replacements)
| Domain | v1.0 (the commercial) | v2.0 (the OURS) |
|---|---|---|
| Ambient Capture | Azure Speech + Twilio | **faster-whisper (the local STT)** + the Twilio media streams (the wired) |
| Specialty LLMs | GPT-4 fine-tunes | **med42 / meditron / biomistral** (the Lab's Ollama) + the dropdown templates |
| Memory | LangGraph + Supabase PGVector | **LangGraph + the local Qdrant + the Postgres** (the deployed) |
| Automation | the FHIR-JSON notes + the ICD combo | the **nura-coding-agent + the MSO Coder** (the built, the tested) |
| Integrations | MeBase / Epic / DoseSpot / Kloud RIS | **OpenEMR (the API+MCP) · the WENO-EXCHANGE eRx · the NURA RIS (the ThaiRIS) · the Orthanc PACS** |
| Review Loop | Unity console | the **Flutter 5-tab** (the Scribe/Clinical/Ops/E6B/Account) |
| Voice | ElevenLabs (the paid) | **piper (the local TTS) + the Echo voice loop** — the ElevenLabs's the reserve |

## 3. Target Stack (the all open)
| Layer | v2.0 |
|---|---|
| Client | **Flutter** (the iOS/Android/macOS/Windows/web — the one codebase) |
| Voice | **faster-whisper (the STT) + piper (the TTS)** + the Twilio streams; the Echo's the browser loop |
| LLM | **the local Ollama (the 16 models)** + the NVIDIA NIM free tier; the med42's the clinical |
| Memory | **LangGraph + the Qdrant + the Postgres** (the Lab) |
| Server | **FastAPI** (the Python — the mso-coder + the tools API) + the MCP gateway |
| Containers | **Hostinger VPS fleet** (the Clinic/Lab/Edge — the Docker) |
| Data | **PostgreSQL (the FHIR JSONB) + Redis + Qdrant** (the deployed) |
| Security | the OAuth 2.1 / SMART on FHIR + the sealed vault (the 0600) + the mTLS |

## 4. Component Details
### 4.1 Ambient Capture
The Twilio streams → the faster-whisper (the local) → the intent classifier (the qwen3/med42 few-shot) → the specialty LLM. The latency: the whisper's the ~2-4s per the segment (the CPU); the interim's the faster on the GPU.

### 4.2 Specialty Agents
The dropdowns (the same): the Derm/Aesthetics, the Gen Surg/EM/Critical Care — the prompt header's the same (the specialty, the allowed_codes, the output_style) — the the model's the med42/meditron instead of the GPT-4.

### 4.3 Memory
The LangGraph nodes (the PatientMemory/EncounterMemory/SpecialtyMemory) + the Qdrant's the vectors; the decay's the LRU + the time-weighted; the purge's the 1-year/GDPR.

### 4.4 Coding & Orders
The **MSO Coder** (the mso-coder/ — the /review → the ICD-10+HCC+RAF+MEAT+audit) + the nura-coding-agent's the engine — the ICD combiner's the the RAF-weighted (the V28's the ground).

### 4.5 MCP Gateway (the our endpoints)
- POST /review (the MSO coder)
- POST /scribe (the tools API — the dictation → the SOAP)
- POST /dx, /synthesis (the tools API)
- POST /mcp/ehr/openemr/* (the OpenEMR MCP's the 20 tools)
- POST /mcp/pacs/* (the Orthanc MCP's the 19 tools — the built tonight)
- POST /mcp/ris/* (the NURA RIS — the HL7 lane)
- POST /mcp/e-prescribe/* (the WENO — the queue)

## 5. Radiology Interoperation
The OHIF viewer + the Orthanc REST (the /instances/{uid}/file) + the AI annotation (the TorchXRayVision + the TotalSegmentator on the Lab) + the CDS (the UpToDate/OpenEvidence).

## 6. Lab & HIE
The FHIR Observation via the HL7 v2→FHIR (the OIE Mirth) + the SFTP polling (the Quest/LabCorp) + the lab-intake-interpreter cron (the Med42's the interpretation).

## 7. Voice Prompt Wrappers (the same)
The system prompt's the same (the empathetic scribe) — the output's the piper/edge-tts instead of the Azure SSML.

## 8. Security
The AES-256 (the field-level), the TLS 1.3, the immutable audit logs, the sealed vault, the penetration tests.

## 9. Licensing (the ours)
The **$0 SaaS** — the local inference's the free, the cloud's the only the storage (the B2's the $6/TB).

## 10. UI/UX (the Flutter)
The 5-tab (the Scribe's the live transcript, the Clinical's the engines, the Ops's the inbox) — the swipe gestures, the ADA.

## 11. Analytics
The encounter duration, the word count, the coding mix, the MRA uplift — the the mso-coder's the queue metrics.

## 12. DevOps
The /nura_medical (the Flutter) + the /opt/data/scripts (the engines) + the docker-compose's the fleet — the GitHub Actions's the CI, the pings the health.

## 13. Roadmap (the DONE vs the next)
- ✅ THE DONE: the scribe lane, the coding engine + the MSO Coder, the OpenEMR MCP, the PACS/RIS, the voice loop (the Echo), the 16 local models, the B2 storage
- ⏳ THE NEXT: the WENO eRx wire, the UI polish, the referring portal, the insurance eligibility
