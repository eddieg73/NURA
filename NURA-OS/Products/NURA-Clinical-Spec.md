# NURA CLINICAL — the definitive product-spec (2026-08-09, founder-delivered!)

## The product
NURA Clinical (aka NURA Connect / NURA HealthDesk / NURA One / NURA Clinical OS) — a HIPAA-ready unified clinical communications platform: secure calling, messaging, fax, AI assistance, and clinical documentation. One app: Inbox · NURA AI · Dialer · Scribe · Fax (+Patients).

## The roles (RBAC, not universal!)
Clinical (physician · PA · NP · RN · MA · therapist · pharmacist · care-manager · scribe · surgical-coordinator!) · Administrative (owner · admin · front-desk · referral-coordinator · auth-specialist · billing · RCM · compliance · IT · fax-admin · call-center!) · External (consulting/locum clinicians · outside-specialist · patient · caregiver · vendor · legal/records!)

## The feature-domains
Unified-Inbox (the 18-sources + the 15-views + the 20-actions + the 12-AI-functions!) · NURA-AI (clinical + coding + administrative — the human-review-mandate!) · Clinical-Dialer (the call-controls + the patient-snapshot + the AI-call-functions!) · Secure-Messaging (the channels + the clinical-safeguards!) · AI-Scribe (the 23-note-templates + the 12-step-workflow + the voice-commands!) · Fax (the 30-functions + the AI-processing + the confirm-patient-matching-rule!) · Patients (the profile + the timeline!) · Contacts · Video · Tasks!

## The architecture
Flutter-app · Next.js-web · NestJS/FastAPI-backend · Postgres · Redis · object-storage · WebSocket · event-queue · AI-orchestration!
Communications: Twilio-Voice/Conversations/Video + HIPAA-fax + APNS/FCM!
AI: STT · medical-transcription · LLM-gateway · RAG · clinical-safety-engine · human-review · audit!
Integrations: SMART-on-FHIR · FHIR-R4 · HL7-v2 · Direct · the EMR/lab/imaging/pharmacy/scheduling/payment/IdP-APIs!

## The NATIVE integration-layer (the revised-mandate!)
Chatwoot (the embedded-omnichannel: the mapping-table + the 3 link-tables!) · NURA-Bridge (the Mirth-orchestration: the EMR-connector-interface + the 17-standards + the 20-functions!) · Perfex-native-module (the business-CRM + the separation-rule!) · OpenEMR-native (the reference-EHR: the sync-domains + the operating-model!) · Weno-Exchange-eRx/EPCS (Phase-1-embed!) · UpToDate-Connect (the context-package + the buttons!) · OpenEvidence (the partner-gated-connector + the honest-status!)

## The governance (the non-negotiables!)
The AI-governance-schema (output_id · source · model · prompt-version · confidence · review-required · status!) · the human-review-before-finalization · the no-autonomous-diagnosis/prescribing/signing · the immutable-audit-logs · the field-level-encryption · the MFA/SSO/RBAC/ABAC · the device-controls (no-PHI-in-push · screenshot/clipboard-restrictions · remote-wipe!) · the HIPAA/HITECH/BAA/state-compliance!

## The MVP-Phases
P1: auth · org/location · dialer · SMS · voicemail · unified-inbox · contacts · patients · fax · push · audit!
P2: AI-assistant · transcription · fax-OCR · summaries · drafts · ambient-scribe · structured-notes!
P3: EHR-integration · FHIR-sync · encounter-export · referrals · labs · imaging · timeline · task-automation!
P4: multi-practice · contact-center · analytics · RCM · prior-auth · care-management · population-health · white-label · patient-app!

## The build-state (08-09!)
LIVE: Flutter-scaffold+APK · OpenEMR-MCP (20-tools!) · Chatwoot-self-hosted · Perfex-MCP · Mirth-authed · Twilio-numbers · DocsGPT-brain (18-textbooks!) · Documo-fax-lane · the-fleet!
QUEUED: the unified-inbox-UI · the scribe-pipeline · the NURA-Bridge-UI · the Weno-Exchange-API · the UpToDate/OpenEvidence-connectors · the RBAC-matrix · the Postgres-schema!
