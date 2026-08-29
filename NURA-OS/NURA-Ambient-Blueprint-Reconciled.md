# NURA Ambient Clinical Intelligence — Reference Blueprint (v1.0, 2025-06-21)

Founder's vendor-neutral blueprint: Unity-based ambient scribe + specialty LLMs + LangGraph memory + MCP gateway + EPCS + PACS + HIE. Stored verbatim-intent; **reconciled against live architecture 2026-08-15 below — where our stack is newer, the blueprint is superseded.**

## Core blueprint (condensed)
- **Ambient capture**: Twilio media streams → Azure STT → intent classifier → specialty LLM (≤300ms captions, ≤2s commits)
- **Specialty LLMs**: per-specialty fine-tunes + dropdown templates + allowed-code bundles (ICD-10/CPT/SNOMED) + MoE router
- **Memory**: LangGraph nodes (Patient/Encounter/Specialty), LRU + time-decay, 1-yr purge, GDPR delete
- **Automation**: ICD combiner (HCC/MRA max), FHIR transaction Bundles (ProcedureRequest, MedicationRequest, ImagingStudy)
- **MCP gateway**: /mcp/transcript · /note · /memory/update · /history · /crm/ghl · /ehr/epic · /dosespot/prescribe · /kloudris/dicom-store; SMART-on-FHIR + JWT; 100 req/min/provider
- **Radiology**: fo-DICOM Unity viewer + Orthanc REST + TorchServe segmentation + CDS-Hooks
- **Labs/HIE**: HL7v2→FHIR, SFTP polling (Quest/LabCorp), PDF→FHIR OCR, Bamboo Health patient-matching
- **Security**: AES-256-GCM field-level, TLS 1.3/HSTS, immutable EventStoreDB audit, DoseSpot EPCS OAuth+2FA
- **Tiers**: Starter $199 (20h) · Growth $999 (100h/5 seats) · Enterprise (on-prem inference)
- **Roadmap**: Q3'25 MVP → Q4'25 multi-specialty+EPCS → Q1'26 imaging+labs → Q2'26 hardening

## Reconciliation vs LIVE architecture (2026-08-15) — ours is newer here
| Blueprint (2025-06) | Live (2026-08) | Verdict |
|---|---|---|
| GPT-4 fine-tunes + Azure STT | OpenRouter multi-model (deepseek primary), Gemini vision lane, Whisper-class ASR via Wispr/others | SUPERSEDED — provider-agnostic routing (founder's free-lane + $9 budget doctrine) |
| Kloud RIS + MeBase EMR (OpenEMR fork) | RADRIS (built from source) + Orthanc hybrid + OIE 4.6.0 engine + live OpenEMR container | NEWER — OIE replaced commercial Mirth; RADRIS built 08-15 |
| Azure AKS / Bicep | Docker-native Compose on Hostinger fleet (K8s explicitly rejected by founder) | SUPERSEDED — Docker remains production |
| MongoDB/Supabase PGVector | Postgres (solis_hermes multi-tenant, 25 tables) + Qdrant + Redis | NEWER — tenancy layer live |
| LangGraph memory 0.2 | Hermes memory + mem0 + Obsidian vault brain (obsidian-second-brain skills) | EVOLVED — vault = human-readable source of truth |
| MCP gateway spec | Live MCP lanes: OpenEMR, Qdrant, Redis, GitHub, Firecrawl, ElevenLabs, Hostinger… | ALIGNED — blueprint validated the pattern; more lanes live |
| DoseSpot EPCS | WENO-EXCHANGE-eRx (NURA-Clinical spec) | ADJUSTED — WENO chosen |
| Solo voice pipeline | CarePilot/Solis/Ensure MSO stack + n8n voice workflows (ElevenLabs Creole family live) | OPERATIONAL — voice in prod via n8n |

## Still-valuable blueprint items NOT yet built (adopt when scheduled)
- fo-DICOM Unity viewer + TorchServe segmentation masks (imaging phase)
- Bamboo Health patient-matching (HIE)
- CDS-Hooks (UpToDate/NIH references)
- EventStoreDB immutable audit (we use Postgres audit_events — adequate for now)
- Red-team prompts in CI (partially covered by nura-clinical-regression-suite)

## Section-by-section verdict (founder's re-paste, 2026-08-15)
| § | Item | Verdict |
|---|---|---|
| 4.4 | HL7v2→FHIR mapper | ✅ ALREADY BUILT — OIE 4.6.0 SOLIS_ENSURE_INBOUND + Zone-01/02 transaction engine (live-verified) |
| 4.5/5 | TorchServe lesion segmentation | ⏳ FUTURE — local-inference container phase (radiology vision = specialty container #2) |
| 6 | SFTP lab polling + PDF→FHIR OCR | ⏳ FUTURE — Quest/LabCorp feeds (gated on lab contracts) |
| 6 | Bamboo Health patient-matching | ⏳ FUTURE |
| 7 | Voice prompt wrappers (Azure/Twilio/Unity) | ✅ USEFUL — pattern already live in n8n ElevenLabs Creole family; Unity wrapper pending |
| 8 | Security (AES-256-GCM, TLS 1.3, audit) | ✅ MOSTLY LIVE — sealed vault + TLS + Postgres audit_events; EventStoreDB not adopted (adequate) |
| 9 | Licensing tiers ($199/$999/Enterprise) | ✅ USEFUL — keep as pricing reference for the SaaS rollout |
| 10 | UI/UX guidelines (swipe-accept, two-panel diff, ADA) | ✅ USEFUL — apply to the Flutter nura_medical review screen + accessibility spec |
| 11 | Analytics (encounter metrics, MRA uplift, error heat-maps) | ✅ USEFUL — fold into the NURA Command Center dashboard KPIs |
| 12 | DevOps (AKS/Bicep) | ❌ SUPERSEDED — Docker-native Compose is production (founder's amendment) |
| 12 | CoT validation + red-team CI | ✅ USEFUL — partially in nura-clinical-regression-suite; extend |
| 13 | Roadmap Q3'25-Q2'26 | ❌ SUPERSEDED — live stack has outrun it (OIE, RADRIS, Solis DB, tenancy all live) |
| 15 | AR overlay, ONNX edge inference, FR/ES packs | ⏳ FUTURE — after core phases
