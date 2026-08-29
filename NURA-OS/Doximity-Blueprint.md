# NURA-OS/Doximity-Blueprint.md

# Doximity-Style Platform Blueprint (founder 2026-08-02) — mapped + deltas

## Architecture (adopt)
Zero-trust: TLS 1.3 + app attestation → API Gateway (MFA/JWT/timeouts) → NON-PHI services (news, directory) vs **HIPAA Secure Zone** (E2E chat, fax/dial engine, ephemeral AI) → isolated PHI store (AES-256 at rest) → **immutable audit log**.

## Pillars
1. **Directory/Verification (trust wall)** — public cannot self-register; verify via NPPES + state board + photo-ID/MFA handshake → **BUILT: scripts/provider-verify.py (NPPES v2.1 API) — LIVE TEST: NPI 1154381580 = verified A, PA-C, Surgical PA ✓**
2. **Secure comms** — WS over TLS 1.3, AES-256 at rest / app-layer encryption, **SQLCipher encrypted SQLite** on device (wipe on logout), **masked push notifications** ("New secure message" — never PHI in APNs/FCM), Twilio/SignalWire BAA tiers
3. **Clinical AI (DoxGPT)** — enterprise instances w/ BAA + zero retention, or LOCAL models; **ephemeral processing** (in-memory, purge after copy) — matches our draft-only + no-retention doctrine

## Stack (our delta vs their recommendation)
| Their pick | NURA (verified reason) |
|---|---|
| AWS/GCP | **Hostinger fleet + local-first** (Clinic/Lab/Storefront; PHI stays on Clinic) — BAA via self-hosting, not vendor contracts |
| PostgreSQL Aurora | OpenEMR/Perfex local DBs + Qdrant + Mem0 (SQLite/state.db) — RLS-equivalent = per-site isolation |
| Stream/Sendbird | **Chatwoot self-hosted** (no third-party PHI transit) — BAA-free by isolation |
| CloudTrail | **WORM ledger plan** (hash-chain + R2 snapshots, NUR-99) — immutable + verifiable |
| Bedrock/Vertex/Azure | **Local models for PHI** (Bio_ClinicalBERT, Qwen2-VL on Lab); consumer APIs = NON-PHI only |

## GOLDEN RULE (register — vendor BAA matrix)
Every vendor touching PHI must sign a BAA or be self-hosted/isolated. Register in data/vendor-baa.json:
- Twilio 🔶 (BAA tier pending creds) · Documo 🔶 · Firebase FCM 🔶 (SA pending — masked payloads only) · OpenEMR/Perfex/Mirth/Orthanc ✅ self-hosted · DeepSeek/Gemini/OpenRouter ⚠️ NON-PHI lanes only · ElevenLabs ⚠️ no PHI in audio · Qdrant/Mem0 ✅ local
- Rule: if no BAA and not self-hosted → no patient data through it (masked/derived only)

## Board
NUR-101 → CTO: adopt into app build (Directory module w/ NPPES verify live; SQLCipher offline store; masked notifications policy; ephemeral AI; BAA register).
