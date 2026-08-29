# NURA MEDICAL STACK — THE FULL DOCKER MASTER PLAN (2026-08-05, founder session)

**e-prescribing = Weno (EPCS) · RIS = ThaiRIS (the radiology information server) · billing = NMI integrated on Perfex (the founder-confirmed 08-05).**

## The stack (the compose topology)
```
hermes-agent (the brain — gateway + api + dashboard)
redis (Dr. Rita — the shared memory backend: mem0 + session + queue)
mirth-connect (the HL7 rail — **BILATERAL sync**: OpenEMR ↔ the destination EMRs, both directions — inbound + outbound)
openemr (the EMR — e-prescribing included)
perfex-crm (the practice CRM — never clinical data)
chatwoot (the omnichannel — SMS/iMessage/Signal/Telegram/email)
twilio (the SMS/voice rail — pass-through billing)
mattermost (the team + the clinician-network lane)
orthanc (the PACS — DICOM C-ECHO/C-STORE/DICOMweb) [+ dcm4chee alternative]
ohif-viewer (the zero-footprint viewer — DICOMweb)
iris-ris (the radiology information server — the modality worklist + reporting)
device-bridge (MQTT — Bluetooth stethoscope/otoscope/ophthalmoscope/vision feeds)
elevenlabs-mcp (the Voice AI — the raw audio stream processing + the conversational synthesis)
cds-hooks (the clinical decision support — ClinicalBERT/BioBERT/OpenEvidence/GatorTron in the 500ms window)
monitoring (prometheus + grafana + the health engine) · backups (restic/rclone)
```

## The lanes (what each does)
1. **DEVICE FEEDS**: capture each device's audio/video stream (via a dock or the mounted MQTT bridge) → feed into Hermes MCP → the agent processes the raw sounds (stethoscope/otoscope/ophthalmoscope)
2. **11-LABS**: register as an MCP provider in the Hermes config (composer connect CLI or MCP endpoint) → the voice synthesis for conversational responses + the audio analysis
3. **REED SKILLS**: extend the Redis-backed skill set to handle the new device intents + link the 11-labs synthesis → the chat history + all conversations visible (the shared-memory lane)
4. **CHATWOOT GATEWAY**: a new messaging gateway in the Hermes config → each channel's traffic routed correctly: SMS (Twilio) · iMessage (Apple Business Chat) · Signal (the bot API) · Telegram (the bot token) · email
5. **CDS**: route the EHR's payloads through a secure middleware layer that calls each service (ClinicalBERT/BioBERT/OpenEvidence/GatorTron) and returns recommendations within the 500 ms window — HL7 CDS-Hooks + SMART-on-FHIR
6. **RIS/PACS**: Iris RIS + Orthanc (or dcm4chee) + OHIF viewer — each in its own container, linked via the docker network, Hermes managing the whole flow (the radiologist signs, the AI = preliminary only)
7. **THE MISSING**: HIPAA-compliant audit logging · billing + subscription layer (the $99/$299/$999 tiers) · patient portal + scheduling · role-based access control · robust monitoring/backup for production

## The existing state (already live on the Clinic)
OpenEMR ✓ · Mirth ✓ · Orthanc ✓ · Chatwoot ✓ · Redis ✓ · Mattermost ✓ · Hermes ✓ · Twilio ✓ — the DELTA: the device bridge, the 11-labs MCP, the CDS hooks lane, the OHIF container, the Iris RIS, the monitoring stack, the audit layer, the billing/subscription.

## The deployment sequence
1. The docker network (one bridge for the whole stack) · 2. The missing containers (OHIF · Iris · CDS-hooks · device-bridge · monitoring) · 3. The gateway config (Chatwoot + the channel routing) · 4. The MCP registrations (11-labs · the devices) · 5. The CDS middleware (the 500 ms contract) · 6. The audit + RBAC + billing layer · 7. The backup/monitoring (restic + the health engine) · 8. The paperclip adapter (hermes_local) for the org orchestration.
