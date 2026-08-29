# NURA Clinical Communications App — the canonical spec (the founder's reference, 2026-08-19)
The HIPAA-ready mobile workspace: the secure calling, the messaging, the fax, the AI assistance, and the clinical documentation. The saved as the product's the reference-grade spec.

## The 5-tab structure
1. **Inbox** — the unified calls/texts/voicemails/faxes/tasks/alerts
2. **NURA AI** — the clinical + operational assistant
3. **Dialer** — the secure clinical phone/video/messaging/voicemail
4. **Scribe** — the ambient documentation + the note generation
5. **Fax** — the secure inbound/outbound
(+ the optional Patients tab)

## The 21 roles (the RBAC — the no universal permission set)
The clinical (the physician, the PA, the NP, the RN, the MA, the therapist, the pharmacist, the care manager, the scribe, the surgical coordinator) + the administrative (the owner, the admin, the front-desk, the referral, the auth, the billing, the RCM, the compliance, the IT, the fax admin, the call-center) + the external (the consulting, the locum, the specialist, the patient, the caregiver, the vendor, the legal).

## The AI safety law (the baked)
The AI never independently diagnoses, prescribes, or communicates the final patient-specific treatment without the authorized clinical review. The every output: the DRAFT + the human review + the source traceability + the confidence + the uncertainty flags.

## The key integrations (the revised native layer)
- **Chatwoot** = the omnichannel conversation engine (the ours — the Clinic's the running!)
- **NURA Bridge** = the Mirth-based interoperability (the ours — the OIE 4.6!)
- **Perfex CRM** = the business ops (the ours — the REST module's the pending)
- **OpenEMR** = the clinical system of record (the ours — the 20-tool MCP!)
- **DoseSpot** = the eRx/EPCS (the the WENO-EXCHANGE's the our lane)
- **UpToDate Connect** = the CDS (the pending)
- **OpenEvidence** = the partner-dependent

## The DB + API
The PostgreSQL's the transactional core (the ~20 tables: the organizations, the users, the roles, the patients, the consents, the conversations, the messages, the calls, the voicemails, the faxes, the encounters, the scribe_sessions, the transcripts, the clinical_notes, the diagnoses, the tasks, the documents, the ai_requests, the audit_logs) + the object storage (the B2!) for the documents/audio/fax. The API: the /v1/ domains (the auth, the patients, the calls, the conversations, the faxes, the scribe, the ai, the tasks...).

## The AI governance schema (the every output)
{ output_id, output_type, patient_id, source_documents, source_transcript_id, model, prompt_version, generated_at, confidence, uncertain_items, clinical_review_required: true, reviewed_by, signed_by, status: draft }

## The stack match (the ours vs the spec)
| Spec says | NURA has |
|---|---|
| Flutter mobile | ✓ the 5-tab (the built) |
| Chatwoot | ✓ the Clinic's the running |
| Mirth (the NURA Bridge) | ✓ the OIE 4.6 |
| OpenEMR | ✓ + the 20-tool MCP |
| Perfex | ✓ the 183-tool MCP (the module pending) |
| Fax | ✓ the Documo lane |
| AI scribe | ✓ the /scribe + the Echo voice |
| Object storage | ✓ the B2 (the 6 buckets) |
| PostgreSQL | ✓ the fleet |
| eRx | ⏳ the WENO (the queue) |
| UpToDate | ⏳ the pending |
| OpenEvidence | ⏳ the partner-pending |

## The primary workflows (the spec's the five)
1. **Incoming call** → the caller-ID match → the snapshot → the consent → the transcribe → the AI intent → the task → the summary → the timeline
2. **Incoming fax** → the OCR → the classify → the extract → the match → the urgency → the route → the chart
3. **Scribe** → the select → the consent → the record → the transcript → the note → the flags → the edit → the sign → the EHR
4. **Refill** → the detect → the extract → the verify → the task → the clinical queue → the review → the disposition
5. **Referral** → the OCR → the match → the extract → the record → the coordinate → the schedule → the notify → the close

The full spec's the canonical — the reference only.
