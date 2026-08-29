# NURATECH.ai — FlutterFlow Implementation Guide (founder's step-by-step, 2026-08-02)

SOURCE: founder-pasted implementation guide. The Flutter team builds against THIS + App-Product-Spec.

## 1. Offline Failsafe (SQLite)
- Settings > Integrations > SQLite → Enable; upload base .db (sqlitebrowser); table `PendingNotes`
- No boolean type: 0 = queued locally, 1 = synced to OpenEMR
- Action Flows: `INSERT INTO PendingNotes (Context, AudioPath, IsSynced) VALUES ('${context}', '${audio}', 0);`

## 2. API Routing Engine (API Manager)
- Groups: `Mirth_Router` (HL7 SIU/ADT POST), `Documo_Fax`, `Twilio_Voice` — shared base URLs + auth headers
- Variable substitution: `[patientId]` in JSON body → bind to UI widgets
- Bind responses: expand JSON tree → e.g., `response.fhir.id` → page state

## 3. Custom Code — Local SLM & Audio
- Custom Code > Actions: custom actions return Future (async inference + DB without UI freeze)
- Inputs: raw transcript → SLM; Returns: formatted SOAP string
- Deps (flutter_sound / FFI wrapper) below the "do not remove" line; Exclude From Compilation for breaking experimental packages

## 4. Native Revenue Cycle (GHL)
- NO external checkout — process payments/memberships/financing NATIVELY via GHL API Manager binding
- Transaction state stays in the GHL pipeline schema

## 5. Webhook Orchestration — CRM Sync
- "Sign Note" button stack: 1) SQLite UPDATE IsSynced=1 → 2) n8n API call → n8n fans out: clinical note → OpenEMR via Mirth; billing trigger → Perfex CRM

## Auth decision (Hermes recommendation 2026-08-02)
PRIMARY: OpenEMR OAuth2 (PKCE) — provider identity = OpenEMR user (one identity, PHI boundary intact, matches NUR-65 SSO + OAuth gate). App session: secure storage + biometric; token refresh via gateway; offline = local session + queued writes, re-auth on reconnect. Supabase = NOT now (NUR-58 ruling pending; another PHI surface; only if non-EMR users are needed later). Filed on NUR-81.
