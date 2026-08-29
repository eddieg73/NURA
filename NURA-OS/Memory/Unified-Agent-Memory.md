# Unified Agent Memory — ONE memory, ANY channel (2026-08-03)

**Founder directive:** "The agent memory is the same no matter where the call comes to."

### 0. ARCHITECTURE DECISION (founder 08-03): TAVUS = IMAGE ONLY. NURA = INTELLIGENCE.
```
Tavus CVI = the RENDER layer (face, audio, WebRTC) — a commodity terminal, replaceable
            (swap for HeyGen or OSS LivePortrait anytime — the brain doesn't care)
NURA BRAIN = Hermes + MoE routing + the MEMORY API (gateway :8642)
Flow: patient → Tavus (face + STT) → transcript → NURA brain (memory envelope, provider gate)
      → response text → Tavus renders face/audio → patient
Exposure: only session transcript/text goes to Tavus for rendering (de-identified where
          possible); PHI and the memory store NEVER leave the Lattice.
One-brain doctrine: every surface (phone/video/chat/app) feeds the SAME brain + SAME memory.
```

## Current state (VERIFIED live)
- `Medisun Memory — GET (shared)` (MElc4ND04ReAIrnc) — webhook → normalize phone → Redis GET → respond
- `Medisun Memory — SET (shared)` (2fDhVWTHtoiwrkK5) — webhook → normalize phone → Redis GET → merge → SET + PUSH
- Live probe: POST /webhook/medisun-memory-get {"phone": ...} → patient envelope
  (found · is_returning_patient · first_name · last_name · dob · insurance_plan ·
   preferred_pharmacy · known_medications · last_call_reason · last_call_date · last_...)
- Channel today: PHONE ONLY. Redis = shared (Clinic).

## THE DESIGN — one memory API, every door

### 1. Canonical patient envelope (extend the existing schema)
```
patient_key      = normalized phone | patient_id | email   (identity resolver picks)
tenant           = NUR-106 per-tenant prefix (medisun, ...)
found / is_returning_patient
first_name / last_name / dob / insurance_plan / preferred_pharmacy / known_medications
last_call_reason / last_call_date
channel_last[]   = {channel, ts, summary, outcome}          (last touch per surface)
event_log        = append-only (Redis PUSH) — EVERY interaction, any channel (audit)
```

### 2. THE MEMORY API = the existing GET/SET webhooks (generalized)
```
POST /webhook/medisun-memory-get  {tenant?, patient_key}   → full envelope
POST /webhook/medisun-memory-set  {tenant?, patient_key, channel, event, payload}
                               → merged envelope + event_log append (provenance)
Identity resolver node: phone | email | patient_id | session_id → canonical patient_key
```

### 3. Channel adapters → SAME endpoints (the "no matter where" matrix)
| Surface | Adapter | Flow |
|---|---|---|
| Phone — Reception.ai | webhook → memory-get (context) → memory-set (outcome) | caller knows the patient |
| Video — Tavus CVI | session start → get · session end → set | PAL opens with memory, writes back |
| Voice — ElevenLabs convos | conversation end hook → set | same envelope |
| Chat — Chatwoot / GHL | message hook → get/set | same envelope |
| App — nura-medical | /pt command → get/set via gateway | clinician sees the same patient |
| Fax/email — legal/medfax | ingest → set (attachment refs) | same envelope |

### 4. Rules
- **One writer doctrine**: only the memory API writes Redis; channels never write directly.
- **Append-only events**: every touch logged (channel, ts, summary) — tamper-evident audit.
- **PHI stays local**: memory API reachable inside the network only; vendor surfaces (Reception.ai/Tavus) get ONLY the session context they need (de-identified where possible).
- **Per-tenant isolation**: key prefix = tenant (NUR-106 pattern).
- **Provider gate**: clinical content in the envelope read-only by licensed roles (role matrix).

## Build plan (n8n, via CLI — we own the API)
1. `identity-resolver` node → extend GET/SET (accept phone | email | patient_id)
2. Channel adapters as n8n sub-workflows per surface (Reception.ai · Tavus · Chatwoot · app)
3. event_log reader webhook (audit surface for the dashboard)
4. Envelope schema v2 (channel_last[] + tenant prefix)
