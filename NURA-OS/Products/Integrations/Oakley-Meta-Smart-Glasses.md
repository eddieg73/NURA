# Integration One-Pager — Oakley Meta Smart Glasses

**Date:** 2026-08-19 · **Public sources only** · Feasibility verdict at bottom.

## What it is
Meta's Performance AI glasses line with Oakley: **Oakley Meta HSTN** (June 2025, from $399) and **Oakley Meta Vanguard** (launched Oct 21 2025, $499). Vanguard: 12MP centered camera, 3K video, 122° lens, five-microphone wind-noise array, open-ear speakers (6dB louder than HSTN), IP67, up to 9h battery, helmet-friendly button placement, **programmable button that triggers a custom AI prompt**, Garmin/Strava integration (heart-rate queries, autocapture on milestones, metric overlays), Meta AI assistant built in.

## Developer ecosystem (the part that matters)
- **Meta Wearables Device Access Toolkit (DAT)** — developer preview, iOS + Android SDKs (GitHub): `MWDATCore` (registration/sessions), `MWDATCamera` (video stream, photo capture), `MWDATDisplay` (on Meta Ray-Ban *Display* glasses only — not Oakley today).
- Integration model: your app registers with the glasses via the Meta AI app (one-time), requests camera/mic permissions, runs **sessions** — live camera frames, mic via Bluetooth HFP (8kHz mono), audio playback to open-ear speakers, pause/resume by hinge/gesture.
- Explicitly supported devices include **Oakley Meta HSTN and Oakley Meta Vanguard**.
- Tooling: Mock Device Kit (test without hardware), Wearables Developer Center (orgs, release channels), AI-coding skills for Claude Code/Cursor/Copilot. **Publishing is not GA yet** — Developer Preview, select partners publish; GA targeted 2026. Country-limited (AI-glasses supported countries only).
- Not yet exposed: Meta AI voice-command access to third-party apps (explored for future).

## NURA fit
- **EMS field lane:** provider POV capture (trauma scene, wound assessment) streaming into the NURA vision cascade — assistive-only per EMH-Spec safety doctrine.
- **Ambient hearing:** HFP mic → local Whisper → EMH voice layer; open-ear speakers = provider hears EMH prompts over scene noise.
- **Device matrix:** EMH-Spec already lists "NURA Glasses" — Oakley Meta is the buy-vs-build path: $499 commodity hardware with an official SDK instead of an in-house glasses R&D program.
- **Flutter note:** DAT is native iOS/Android — bridge via platform channels in the 5-tab app, or wait for Web Apps (display glasses only). No display on Oakley today → no HUD; audio-first.

## Risks / constraints
- Developer Preview: API may shift; publishing gated; Meta AI app required for pairing.
- **PHI:** camera/audio of patients = PHI. Use NURA's own pipeline (local Whisper, sovereign models) — never route clinical audio to Meta AI. FL two-party consent + indicator discipline already in EMH-Spec §4.
- One-session-at-a-time per device; HFP audio is 8kHz mono (fine for voice, not for auscultation-grade capture).

## Feasibility verdict
**HIGH for a prototype EMS/ambient lane** — real SDK, supported devices, ~$499 hardware. Build: buy one pair (Vanguard, IP67), integrate DAT via native bridge, wire mic→Whisper→EMH voice loop and camera→wet-read-adjacent vision cascade (draft-only). Treat as assistive capture, never as diagnostic hardware. Production rollout waits for GA publishing (2026) + a PHI review of the data path (which stays off Meta's rails by design).
