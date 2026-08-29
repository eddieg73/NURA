# Provisional Patent — Integrated Agentic Healthcare Platform (FILED 2025-06-16)

Applicant: Nura Tech AI · 818 Chestnut St., Clearwater, FL · Eddie@nuratech.ai
Source: founder-provided document (2026-08-02) — the FILED provisional record.

## Coverage (as filed)
- **Core**: cloud-native healthcare platform — AI avatar interface (Unity), MCP server multi-AI orchestration (Claude/GPT/GatorTron/ClinicalBERT), agentic behavior, specialty context switching, SOAP automation, ICD-10/CPT/SNOMED mapping, evidence-medicine integration (UpToDate/Sanford)
- **Backend**: OpenEMR (EHR) · MEDBASE CRM · Kloud RIS · OpenELIS (LIS) · DoseSpot EPCS
- **Edge**: NVIDIA Jetson (Orin Nano / AGX Orin) mobile + DATA device + URA avatar
- **Comms**: Kore Wireless eSIM · multi-channel (SMS/iMessage/FB/IG/WhatsApp/email) · **BLE device sync**
- **Payments**: FORWARD, PCI DSS, sub-merchant structure
- **Radiology AI**: university datasets (NIH, CheXpert, LIDC-IDRI, LUNA16, BRATS, ADNI, DDSM, INbreast, TCGA) — training pipeline + critical finding alerts

## Delta vs current build (2026-08-02) — IP consistency flags
| Filed (2025-06) | Current build | Action |
|---|---|---|
| Kloud RIS | Orthanc + ThaiRIS + OHIF (self-hosted) | Continuation claim: PACS module change |
| MEDBASE CRM | Perfex + Chatwoot | Continuation: CRM swap |
| FORWARD payments | NMI (Direct Connect v4) | Continuation: processor swap |
| DoseSpot EPCS | WENO EPCS (selected) | Continuation: EPCS vendor change |
| Azure cloud | Self-hosted Hostinger fleet (offline-first) | **Architecture claim shift — MUST amend** |
| BLE device sync (mentioned) | Full device lane + telemetry CDS (NEW 2026-08-02) | **Add continuation claims: IHE PCD, 11073 SDC, NEWS2 CDS engine, provider gate** |

## Rules
Filed provisional = priority anchor (2025-06-16). Any material build change should map to a continuation/provisional update BEFORE public disclosure. See uspto-ai-patent-watch skill for competitive lane.
