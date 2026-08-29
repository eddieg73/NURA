# Integration One-Pager — Plaud (AI voice recorder)

**Date:** 2026-08-19 · **Public sources only** · Feasibility verdict at bottom.

## What it is
Plaud builds dedicated AI recording hardware + a transcription platform: **Plaud Note / Note Pro** (card-size, phone-call + in-person capture), **NotePin S** (wearable pin), and the **Plaud app** (transcription, speaker-labeled segments, summaries, SOAP-note + 30+ clinical templates, 112 languages). Positioning is explicitly ambient clinical documentation / AI scribe.

## Developer ecosystem
- **Plaud Embedded** (portal.plaud.ai, docs.plaud.ai) — a real developer platform: BLE/WiFi device-pairing SDKs for iOS/Android (starter app included), Auth API (Partner Token → per-user JWTs), File Upload API (or bring your own audio URL), and an async **Transcription API** (noise reduction, VAD, language ID, **diarization with speaker labels**, `plaud-fast-whisper` model; poll `transcription_id` until SUCCESS).
- Free tier: **300 transcription hours + 50 connected devices per client**; usage-based billing beyond. Regions: US, JP (EU/SG coming).
- Key quirk: a Plaud device can be **bound to only one app at a time** (offline-encryption design).
- Device → phone sync via BLE or WiFi; transcription is cloud-side.

## NURA fit
- **Scribe lane:** encounter capture → Transcription API (diarization) → NURA scribe skill drafts the chart-ready note → provider review → OpenEMR. Plaud = the capture hardware + STT; NURA = the clinical intelligence + EMR write (Plaud has **no EHR integration** — that part is ours, and it's the moat).
- **Echo voice loop synergy:** same raw audio could feed both the EMH ambient hearing and the scribe (or stay separate lanes).

## Compliance posture (the deciding factor)
- Strong stack: SOC 2 Type II, ISO 27001/27701, GDPR, HIPAA validation report, AES-256 in transit/at rest, no training on user data, user-controlled deletion.
- **BAA:** Plaud states a BAA is available on request (per support docs / Paubox research); one 2026 third-party review found no *public* BAA terms and warns to get it in writing. **NURA rule: no patient audio until a signed BAA is in hand** — plus documented patient consent (FL two-party discipline already standard for NURA) and no use of speaker-embedding features where BIPA-like voiceprint laws could apply.
- Sovereign alternative: same hardware-less flow via local Whisper keeps PHI on-prem — but loses the Plaud hardware + diarization pipeline.

## Risks / constraints
- Cloud transcription = PHI egress → BAA + encryption + retention terms required; data residency (US endpoint exists: platform-us.plaud.ai).
- Device single-app binding; SDK frameworks arm64-only (no simulator); per-region credentials.
- Cost scales with volume; 300 free hours covers evaluation comfortably.

## Feasibility verdict
**HIGH (conditional on BAA).** Plaud is the fastest path to a hardware-backed ambient scribe: real SDK, real API, HIPAA posture, free tier to prototype. Gate: signed BAA before any PHI; patient consent workflow; scribe output stays draft + provider-approved (EMH-Autonomy-Ladder L0–L1). If BAA stalls → fall back to local Whisper capture (EMH hearing lane) and revisit.
