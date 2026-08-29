# Mirth / NextGen Connect — The NURA Mastery Brief (2026-08-16)

## ⚖️ THE CRITICAL LICENSE FACT (read first)
- **March 19, 2025: Mirth Connect 4.6+ went commercial/proprietary.** Source closed for new releases; sold via NextGen + resellers; the new entry license adds SSL Manager, Channel History, Message Generator + Mirth Command Center (multi-server web management; not available in EU/UK).
- **NURA's engine = OIE 4.6.0 (the Open Integration Engine fork) — the open, self-hosted path.** Doctrine: OIE stays our integration engine; we do NOT depend on commercial Mirth. All channel work targets OIE.
- Official User Guide: https://downloads.mirthcorp.com/connect-user-guide/latest/mirth-connect-user-guide.pdf (walled from our IP — engineer fetches it; the knowledge below = operational truth + the wiki).

## 🏗 Channel architecture (the mental model)
Channel = source connector (in) → transformer chain (JavaScript, E4X/JSON) → filter → destination connectors (out), with:
- **Source connectors**: MLLP (TCP w/ 0B...1C0D framing + ACK/NACK), TCP, HTTP Listener, File Reader, Database Reader, JS Reader
- **Destination connectors**: MLLP, TCP, HTTP Sender, File Writer, Database Writer, JS Writer, Web Service Sender
- **Message types**: HL7 v2.x (ER7/XML), X12, DICOM, Delimited, JSON, XML, FHIR (via mappers)
- **Transformers**: JavaScript steps (msg/msgId/channelMap/globalMap, logger, routing), message templates (inbound/outbound), data-type mapping
- **Filter**: JS boolean per connector
- **Deployment**: channels deploy/undeploy/start/stop/pause; message storage modes (DEVELOPMENT/PRODUCTION/RAW); initial state STARTED

## 🔌 NURA's live OIE estate (the engineer's starting point)
| Component | Where |
|---|---|
| OIE 4.6.0 | Clinic, Docker (host-network), admin :8445 HTTPS self-signed, MLLP :6663 |
| Channels deployed | SOLIS_ENSURE_INBOUND · OPENEMR_HERMES_BRIDGE (:6666→tools API) · RISPACS_HERMES_BRIDGE (:6667→radiology-intel :8092) |
| DB sink | MLLP→solis_hermes :6665 |
| REST API | /api/users/_login (form) · /api/channels (GET/POST XML) · /api/channels/{id} · /api/server |
| Canonical format | Channel XML version 3.8.0 (the ONLY schema OIE 4.6 accepts — never fabricate a different version) |
| Admin creds | sealed vault (mirth-oie-admin) |

## 🎯 The interface roadmap (the engineer's mandate)
1. **OpenEMR bidirectional**: ORU results → OpenEMR observations (outbound from OIE); orders → OIE → labs (inbound). OpenEMR speaks HL7 via its interface module — wire BOTH directions (current: receive-only bridge).
2. **RIS/PACS full loop**: RADRIS ORM → OIE → Orthanc worklist; modality complete → Orthanc → OIE ORU → RADRIS status + radiology-intel drafting.
3. **Vendor gateways**: LIFENET/RescueNet/Eitan HL7 → DEVICE_TELEMETRY :6668 → device-scores.py (NEWS2).
4. **FHIR mapper layer**: HL7 v2 ↔ FHIR R4 Observation/Patient/Encounter (the sidecar doctrine).
5. **Channel governance**: versioned XML in git (nuratech-infra-git), deploy scripts, the hermes-mirth-connect REST recipe, rollback per channel.

## 📚 The engineering references (hand to the hire)
- Skills: mirth-oie-engine-ops (the OIE ops) · hermes-mirth-connect (REST deploy recipe) · hostinger-mirth-docker-connector · medical-device-connectivity (IHE PCD + 11073 MDC map)
- GitHub: nextgenhealthcare/connect wiki (release notes + upgrade guides, the final open source)
- The Mirth User Guide PDF (engineer downloads)
- Our canonical channel XMLs: /opt/data/scripts/mirth/*.xml
