# NURATECH.ai App — FULL Product Spec v2 ("Clinical & Business Command Center", 2026-08-02)

SOURCE: founder spec (Doximity × NURA Practice OS merger). This + FlutterFlow-Implementation-Guide.md + App-Product-Spec = the BUILD TRUTH (scope freeze).

## Core identity
All-in-one Clinical & Business Command Center: ambient scribe + VoIP/eFax + omnichannel comms + surgical tools + RCM in ONE app.

## Navigation
- **Bottom nav (5)**: News/Feeds · Ask (NURA/DoxGPT AI) · Dialer (phone+video) · Scribe (ambient) · Fax (secure hub)
- **Header**: provider profile, network status (Cloud/Offline SLM), alert badges (messages/appointments/voicemails/recalls)
- **Practice OS hub grid (3×4)**: Phone System · Omnichannel Inbox · Online Schedule · Patients · Patient Lists · Team Chat · Payments & Financing · Reputation & Reviews · Analytics · Secure eFax · Digital Forms · Practice Settings

## Modules
1. **NURA Scribe** — waveform recorder (flutter_sound/record), note-type dropdowns (Progress/H&P/Consult/Pre-Chart/Procedure/Discharge), multi-language, "audio never retained" indicator, SOAP + treatment plans + eRx + lab orders, FHIR/OpenEMR mapping via API/MCP, sample-encounter onboarding button
2. **Ask NURA / Clinical Copilot** — chat + prompt pills (brow-lift endoscopy, rhino post-op, DDI checks), text/voice input, RAG (peer-reviewed + RxNorm + ICD-10/CPT)
3. **Clinical Dialer & Omnichannel** — keypad, custom caller ID, VoIP WebRTC/Twilio, video (telehealth link via SMS), direct-to-voicemail drops, two-way SMS/MMS, **24/7 AI voice receptionist** (answers after-hours, qualifies leads, FAQ, books appointments, intake)
4. **Secure eFax** — Inbox/Sent/Drafts/Archive tabs, doc cards (caller/pages/timestamp/thumb), **AI fax summarizer** (OCR+LLM, 3-sentence), outbound scanner + e-sign overlay
5. **Surgical & Aesthetic Suite** — before/after vault (grid overlay, tagging), digital consents (signature package), treatment plans + inventory decrement (toxins/fillers/packs on sign-off)
6. **RCM** — CPT/ICD-10 auto-suggest from notes, auth/claims/denials, **Stripe/Plaid native payments** + memberships + financing, reputation engine (review requests to Google/FB/RealSelf)

## Integrations
OpenEMR/FHIR (bi-directional) · GHL + Perfex (pipelines) · Twilio (WebRTC/SMS/voicemail) · n8n/webhooks (WooCommerce, GetFWD)

## Offline failsafe
Quantized SLM (MedGemma 4B / Qwen3-8B via mlc_llm or llama.cpp) — offline transcription + formatting → local SQLite/Isar queue → sync on reconnect

## UI styling tokens (build standard)
- Accent: Neural Blue #007AFF · Cyber Cyan #00E5FF
- Surface: Deep Slate #0A0E1A (dark) · Clinical White #F8FAFC (light)
- Type: Inter / SF Pro, high-contrast, fast clinical navigation

## Auth (Hermes recommendation — founder decision pending)
PRIMARY: OpenEMR OAuth2 (PKCE) — provider identity = OpenEMR user; secure storage + biometric session; offline = local session + queued sync, re-auth on reconnect. Supabase deferred (NUR-58 ruling pending; no second PHI surface). Filed on NUR-81.
