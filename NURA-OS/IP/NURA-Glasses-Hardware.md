# NURA Glasses — Wearable AI Hardware (spec 2026-08-02, founder: "Incorporate Nura into glasses like Meta")

Sibling of the NURA Capsule (nRF52840). Meta Ray-Ban class form factor, NURA brain.

## Form factor (Meta-class target)
- Frames + camera + mic array + bone-conduction speakers, ~50-60 g, 4+ h battery, IPX4
- Sensors: 12 MP camera (POV video/photo) · 2-4 mic array (beamforming) · IMU (gesture/snap) · touch + voice controls
- Connectivity: Bluetooth (phone bridge) + WiFi (direct uplink) — the PHONE is the brain, glasses are the senses (same doctrine as Capsule: ears/mics → phone/Jetson compute)
- Option: glasses dock/charge case (Capsule-style pogo)

## NURA lanes in the glasses (what the AI does)
1. **Ambient clinical scribe** — hands-free encounter documentation (CORA lane): listen → structured note → chart (provider review gate)
2. **POV telehealth** — live scene/encounter video to the medical director (telehealth exam lane + vision cascade); EMS/fly-car: scene streaming to dispatch/hospital
3. **Voice assistant** — Hermes in your ear: med lookups, protocols, dispatch, hands-free (EMS ops)
4. **Audio Ddx** — stethoscope-pod link (BLE) → heart/lung audio → classifier → ranked Ddx (suggestive only, provider gate)
5. **Photo/document capture** → vault/LiveSync (auto-OCR)
6. **Sky lane** — hands-free UAP/sky observation capture ([V]/[U] tags, no claims)
7. **Navigation/context** — turn-by-turn scene nav, patient context whisper (from EHR, PHI-gated)

## Architecture
Glasses (sensors) ↔ BLE/WiFi ↔ phone app ↔ Hermes edge/Jetson (truck) ↔ VPS lanes. Offline-capable (offline-ai-agent: on-device STT + small LLM + deterministic CDS). E2EE on the wire; PHI never on glasses storage (ephemeral buffer only).

## Regulatory / ethics (hard rules)
- **Recording consent**: FL two-party consent — POV capture requires consent flows (beep/indicator, opt-out, deletion)
- Medical use = accessory/decision-support framing; never diagnosis from glasses alone; provider gate unchanged
- HIPAA: encrypted streams, no PHI at rest on device, audit trail (Hermes Agent)
- Military-grade: kill-switch, tamper-evident, encrypted mesh when paired with truck/drone stack

## IP
Continuation-worthy: wearable embodiment of claim 1 (avatar-as-orchestrator) + claims 14-15 (BLE proximity context — glasses see what the wearer sees). Add to the patent continuation package.

## Team/ownership
Hardware lane under the product org (NUR-112 devices family); prototype path: eval Snapdragon AR1 Gen 1 + open SDKs; sim-first, founder-gated hardware purchases.
