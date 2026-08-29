# NURA Integration-Status (mirrored 2026-08-02)

Live status of every lane/connector. Credentials NEVER here (`.env` 0600 only — vault feeds RAG).

## Telephony (Twilio)
| Item | Value | Status |
|---|---|---|
| Account SID | AC827…31d (stored .env) | ⚠️ **401 — token mismatch** (both candidate files probed) |
| Auth token | NOT stored in vault (secret) | ❌ dead until console refresh |
| Twilio number | **+1 (727) 477-3636** | staged |
| WhatsApp sender | **+1 (305) 206-8697** | staged |
| Bundle SID | BUe1ee3…d67 (10DLC/WhatsApp) | stored .env |
| SMS channel | enabled | blocked on token |
| WhatsApp channel | enabled + whatsapp_cloud | blocked on token |

## Voice
- Edge TTS: ✅ WORKING (voice bubbles on Telegram)
- ElevenLabs: key valid, voice_id 404 — NUR-73 fix queued
- Skill: voice-message-ops

## Medical MCP suite
- openFDA 18 tools ✅ · PubMed ✅ · CDC ✅ (lane built) · BioPortal ✅ · OpenEvidence 🟡 (key pending) · Mirth ✅ lane (creds pending) · OpenEMR 🟡 mock (OAuth pending) · Firebase 🟡 (SA pending) · Documo 🟡 (key pending) · Granola ✅ lane (key pending)

## Messaging & CRM
- Chatwoot: lane configured — token pending
- Perfex: 183-tool lane — token pending
- GHL: NUR-70 — key pending
- Notion: token LIVE, share gate pending (0 pages)
- Moltbook: ✅ CLAIMED — nura_hermes, heartbeat 6h, intro posted
- n8n: token append operator-blocked

## Memory & Knowledge
- Mem0 active · RAG nura-docs **540 chunks** (vault included as source)
- Obsidian vault: Knowledge Hub (15 notes mirrored) — **everything mirrors here now**

## Fleet
- Clinic 1441409 (this box) · Lab 1030183 (empty) · Edge 817449 (no firewall)
- Redis ✅ · Qdrant ✅ (nura-docs 540, nura-os 8)
