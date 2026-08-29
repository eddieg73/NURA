# AUTOPILOT 3-PHASE GOAL (founder, 2026-08-02) — secure multi-platform healthcare suite

Archived verbatim intent. Mapped to existing board work — dedupe, don't rebuild.

## Phase 1 — Doximity Replication (Comms Front-End)
- Flutter UI mimicking Doximity Dialer → **NUR-81 (app) Module 3 (Dialer)**
- Twilio proxy-call bridge (provider cell → gateway → clinic Caller ID) → NUR-77 (Twilio wiring; Echo owns)
- Zero-download telehealth via Zoom Video SDK (native) + WebRTC web app on Hostinger → app M3 extension; NOTE: Zoom SDK licensing/approval needed; alternative = Twilio video/WebRTC native (fewer licenses)

## Phase 2 — Medical Core Connectivity
- Perfex ↔ OpenEMR bidirectional via SMART on FHIR → NUR-82 (Mirth/HL7) + NUR-65 (SSO) + openemr-perfex-integration skill
- Incoming fax vision ingestion with Qwen2-VL (local VLM) → NUR-92 (Documo/email ingestion) — vision cascade already has free-VL lane; Qwen2-VL can ride it; pydicom/OCR installed
- ThaiRIS MWL node ↔ Orthanc PACS :4242 + OHIF embedded in Flutter canvas → NUR-75 (ThaiRIS build) + imaging-stack (Orthanc :8042/:4242, OHIF :3000) — OHIF-in-Flutter = WebView embed of OHIF viewer

## Phase 3 — Medicare RAF Scoring Analytics (PRIMARY MISSION)
- Cross-modal correlation engine: LOINC lab trajectories + radiology matrices + voice-transcribed manifestations → unified health memory → NUR-91 (Provider Labs) + RATCHET + predictive-clinical-analytics + hermes-laboratory-intelligence
- LangGraph/Ruflo audit node BEFORE note commit to OpenEMR: intercepts vague docs ("kidney disease"/"angina") vs severe labs → real-time warning: "Increase documentation specificity to unlock controlling HCC category codes and optimize the patient's global RAF score." → review-node pattern: INTERCEPT + WARN, PROVIDER DECIDES (never auto-commit — clinical doctrine); ties to hermes-coding-quality-compliance + compliant-coding-support (RAF 1.27 panel, Solis MA)
- WORM audit ledger in Supabase (immutable snapshots: AI output → human modifications → finalized) → FLAG: Supabase deferred per NUR-58 ruling (app data); ledger is audit-only (no PHI app surface) — CTO to rule on a Qdrant/SQLite-backed WORM alternative (content-addressed hashes + R2 object storage) vs Supabase

## Compliance flags
- RAF nudging = documentation-specificity guidance (legitimate query practice) — never coaching upcoding; provider gate mandatory
- Zoom SDK = licensing + BAA review; Twilio video alternative considered
- WORM ledger: immutability via hash-chain + external snapshots (R2) — verify before claiming "immutable"

## Board
NUR-99 filed → CTO: sequence these into the existing NURs (81/75/77/82/91/92 + RATCHET); evidence per phase.
