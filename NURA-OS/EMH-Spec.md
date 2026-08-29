# EMH — EMERGENCY MEDICAL HOLOGRAM — PRODUCT SPEC v1.0 (2026-08-02)

**Founder directive: develop the emergency medical hologram with audio for clinical decision support. Wire vision and hearing for NURA through all devices.**

## 1. THE PRODUCT
The EMH is NURA's emergency clinical voice — the Voyager-Doctor persona made real: **speaks protocols, hears the scene, sees the patient, stays deterministic underneath**. It is the audio face of the clinical stack in emergencies — in the ear of the provider (Eddie, the PA-C), at the scene, in the truck, in the field, in the drone feed.

## 2. ARCHITECTURE
```
SENSORS (hearing + vision, all devices)
  ├─ Mic array (glasses/app/Capsule/truck)
  ├─ Cameras (phone/glasses/body cam/drone/truck 360)
  └─ Telemetry (BLE monitors, 11073/IHE PCD)
        │
        ▼
NURA PERCEPTION LAYER
  ├─ Whisper STT (hearing) ── directed + ambient
  ├─ Vision cascade (scene/trauma/waveform/meds — assistive)
  └─ Deterministic CDS: NEWS2 + TCCC decision tables (NEVER the LLM)
        │
        ▼
EMH VOICE LAYER (audio OUT)
  ├─ EMH persona voice (ElevenLabs Sarah/Edge, barge-in)
  ├─ Protocol scripts: MCI triage · cardiac arrest · hemorrhage · anaphylaxis · stroke · NEWS2 escalation
  └─ Provider gate: every output reviewed by the licensed provider
        │
        ▼
OFFLINE CORE (dead-zone capable)
  └─ Hummingbird (GLM-5.2 sovereign) + on-device models — EMH works with zero connectivity
```

## 3. DEVICE MATRIX (vision + hearing through ALL devices)
| Device | Hearing | Vision | Voice out | Status |
|---|---|---|---|---|
| NURA app (phone) | mic ✓ | camera ✓ | speaker ✓ | build (app priority a0054c6c) |
| NURA Glasses | mic array ✓ | POV ✓ | bone-conduction ✓ | dev (8b1d2cd2) |
| Capsule (BLE) | mic ✓ | — | in-ear ✓ | hardware roadmap |
| Axon body cam | ✓ | ✓ livestream | — | tactical directive aa49bb8c |
| Aero drones | — | scene ✓ | — | Aero division |
| EMS truck | cabin ✓ | 360 ✓ | PA ✓ | truck stack banked |

## 4. SAFETY DOCTRINE (non-negotiable)
- **The LLM never scores or decides** — NEWS2/TCCC run deterministic (telemetry-cds-engine)
- EMH assists the provider; the provider (founder, PA-C) remains THE decision authority
- Assistive-only vision outputs (no autonomous diagnosis from camera alone)
- FL two-party consent: beep/indicator discipline on recording devices
- Theatrical persona voice only — clinical framing stays strict (no wit, uncertainty preserved)
- PHI stays local/encrypted; offline lanes never phone home

## 5. EMERGENCY SCRIPT LIBRARY (v1 scope)
MCI triage (START) · Cardiac arrest (BLS/ACLS verbal prompts) · Hemorrhage control (TCCC) · Anaphylaxis · Stroke (Cincinnati) · NEWS2 escalation · Hypothermia (TCCC cold chain) · Burn triage · Pediatric emergency prompts

## 6. MILESTONES
1. Voice layer + script library — 08-15 (Hermes + voice lanes)
2. Hearing loop (whisper live) — 08-22
3. Vision cascade wiring (app camera first) — 08-31
4. MCI simulation test (sim-first, with Aero/EMS sims) — 09-15
5. Glasses/body-cam lanes — per device directives

## 7. INTEGRATIONS
emh-clinical-persona (voice) · emergency-medical-hologram (skill) · telemetry-cds-engine (NEWS2) · tactical-medicine-swat · disaster-response-mass-casualty · vision-routing · offline-ai-agent (hummingbird) · medical-device-connectivity · emergency-critical-care-practice · critical-care-ventilator-management

*Spec v1.0 — every device row maps to a live or tasked lane. No fiction.*
