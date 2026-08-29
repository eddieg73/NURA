# NURA × OAKLEY META — product scheme (2026-08-02, [D6] board)

Hardware = Oakley Meta (Meta SDK verified camera streaming). Software = NURA (our VLM core, sovereign).

## SKUs
| SKU | Hardware | Use | Features |
|---|---|---|---|
| **NURA Access** | Oakley Meta **HSTN** (prescription-ready, 8h) | Civilian — blind/low-vision | scene/text/obstacle audio cueing · wayfinding (OSRM) · remote assist (self-hosted Be My Eyes-class) · prescription + accessibility channels |
| **NURA Tac** | Oakley Meta **Vanguard** (9h, action) | Military / LE / PJ | CIVTAK/ATAK feed · threat cueing + spatial audio (L/R) · drone feed overlay · PJ comms earpiece lane · audio-only NV-friendly UI |
| **NURA Field** (EMS) | HSTN or Vanguard per role | Paramedic hands-free | EMH voice layer (audio-first CDS) · scene descriptions · telepresence to provider · device telemetry glance (OBD2/NEWS2 audio) |

## Architecture (one VLM core)
```
Oakley cameras → Meta SDK (phone app streams) → NURA VLM CORE
  (Qwen2.5-VL/Phi-4-vision on sovereign stack — offline-first, PHI-safe)
→ EMH voice layer → open-ear speakers (ambient sound preserved)
→ Lattice: TAK/CIVTAK · dispatch · remote assist · audit trail
```

## Rules
- NURA = software/service per seat (SaaS, NUR-106); hardware stays Oakley retail
- Camera/audio: FL two-party consent; privacy shutter doctrine; no always-on recording
- Tactical SKU = export-controlled review (EAR/ITAR variants); civilian SKU = open
- No PHI on Meta cloud — camera stream stays on our stack
- Claims 12-13 embodiment: Capsule/Glasses IP continuation

## Gates
08-14 HSTN/Vanguard + SDK PoC (camera → NURA VLM) · 08-28 Access v0 · 09-12 Tac v0 · 09-30 pilots (1 civilian + 1 LE/EMS partner)
