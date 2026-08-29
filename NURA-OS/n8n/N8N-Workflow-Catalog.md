# n8n Workflow Catalog — learned 2026-08-15 (Edge instance, n8n.nuratech.ai)

**52 workflows · 11 credential lanes** (gmail, gSheets, gDrive, GHL, OpenAI, DeepSeek, Ollama, Cloudinary, Redis, SMTP, httpHeaderAuth)

| Status | Workflow | Trigger | Nodes | Integrations |
|---|---|---|---|---|
| ACTIVE | Basic Automatic Gmail Email Labelling with OpenAI and Gmail API | manual | 13 | — |
| ACTIVE | Create API Folder in Google Drive (Webhook) | webhook | 2 | — |
| ACTIVE | ElevenLabs Conversation Initiation (multi-clinic) | webhook | 5 | — |
| ACTIVE | ElevenLabs Creole → Mattermost (multi-clinic) | webhook | 17 | — |
| ACTIVE | ElevenLabs → GoHighLevel Creole Appointment Booking v1 | webhook | 19 | — |
| ACTIVE | ElevenLabs → GoHighLevel Creole Pharmacy Task v1 | webhook | 9 | — |
| ACTIVE | GHL to PDF Monkey Webhook | webhook | 7 | — |
| ACTIVE | Medisun Booking — CREATE APPOINTMENT (REST, multi-clinic) | webhook | 13 | — |
| ACTIVE | Medisun Booking — GET SLOTS (REST, multi-clinic) | webhook | 9 | — |
| ACTIVE | Medisun Kreyol Test Page | webhook | 5 | — |
| ACTIVE | Medisun Memory — GET (shared) | webhook | 5 | — |
| ACTIVE | Medisun Memory — SET (shared) | webhook | 7 | — |
| ACTIVE | Medisun Voice AI Weekly Report (Email) | scheduleTrigger | 5 | — |
| ACTIVE | Medisun — CREATE TASK (REST, multi-clinic) | webhook | 13 | — |
| ACTIVE | NMI Sale Success → GHL Contact | webhook | 9 | — |
| ACTIVE | Provider Labs Ingest Webhook | webhook | 3 | — |
| ACTIVE | Weekly KPI Report - Multi-Location - Monday Morning | scheduleTrigger | 11 | — |
| ACTIVE | ZAPIER — Hermes Bridge (CI/CD, Webhook, API) | webhook | 3 | — |
| off | ASC - Pre-Op Clearance & Checklist | scheduleTrigger | 5 | — |
| off | Automate Instagram Reel Downloads with Google Drive Storage & Telegram Alerts | manual | 4 | — |
| off | Automated SEO Content Creation | manual | 11 | — |
| off | AUTONOMY - Reflexion Loop (Self-Improvement) | scheduleTrigger | 6 | — |
| off | CLIN - Ambient Scribe | webhook | 4 | — |
| off | CLIN - Clinical Decision Support | webhook | 5 | — |
| off | CLIN - Patient Flow Forecast | scheduleTrigger | 4 | — |
| off | CLIN - Sepsis Early Detection | scheduleTrigger | 5 | — |
| off | Create API Folder in Google Drive | manual | 2 | — |
| off | Create API Folder in Google Drive (Webhook 2) | webhook | 2 | — |
| off | Diagnosis-Based Evaluation Form Router | webhook | 30 | — |
| off | ElevenLabs Voice Test | manual | 2 | — |
| off | eMedPractice FHIR → GHL Patient & Appointment Sync | webhook | 17 | — |
| off | Farmer app bot | manual | 4 | — |
| off | Generate AI Videos with Google Veo3, Save to Google Drive and Upload to YouTube | scheduleTrigger | 22 | — |
| off | Generate AI Videos with OpenAI Sora 2 & Upload to Google Drive | manual | 21 | — |
| off | LAB → OpenEMR → CRM Condition Tags (final results) | scheduleTrigger | 10 | — |
| off | My workflow | webhook | 1 | — |
| off | My workflow 2 | manual | 2 | — |
| off | My workflow 3 | manual | 2 | — |
| off | My workflow 4 | webhook | 1 | — |
| off | OpenEMR — Appointment Reminders & Confirmation | scheduleTrigger | 6 | — |
| off | OpenEMR — Claims Submission & Patient Billing | webhook | 10 | — |
| off | OpenEMR — Insurance Eligibility Verification | webhook | 10 | — |
| off | OpenEMR — Lab Result Release & Escalation | webhook | 13 | — |
| off | OpenEMR — Post-Visit Follow-Up & Education | webhook | 13 | — |
| off | OpenEMR — Revenue Cycle Exception Router | webhook | 10 | — |
| off | OpenEMR — Secure Patient Communication | webhook | 13 | — |
| off | OpenEMR — Self-Scheduling & Booking | webhook | 10 | — |
| off | PHYS - Appointment Scheduling & Reminders | webhook | 6 | — |
| off | Sora 2 Automation | manual | 34 | — |
| off | Talk to Your Data — Google Sheets + OpenAI Agent | manual | 5 | — |
| off | tiktok automation | manual | 8 | — |
| off | ZAPIER — Hermes Bridge (CI/CD, Webhook, API) | webhook | 6 | — |

## Node-type usage (the pattern language)

- httpRequest: 106
- code: 83
- if: 43
- respondToWebhook: 36
- webhook: 35
- stickyNote: 23
- set: 12
- googleDrive: 10
- scheduleTrigger: 9
- emailSend: 9
- redis: 8
- telegram: 8
- @n8n/n8n-nodes-langchain.chainLlm: 7
- manualTrigger: 7
- googleSheets: 7
- wait: 7
- @n8n/n8n-nodes-langchain.lmChatOpenAi: 5
- @n8n/n8n-nodes-langchain.agent: 5
- gmailTool: 4
- merge: 3
- @n8n/n8n-nodes-langchain.memoryBufferWindow: 3
- crypto: 3
- @n8n/n8n-nodes-langchain.openAi: 3
- switch: 3
- itemLists: 2

## Credential usage
