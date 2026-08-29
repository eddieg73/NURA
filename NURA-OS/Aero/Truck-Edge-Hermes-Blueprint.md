# TRUCK-EDGE HERMES INSTANCE — BLUEPRINT v1.0 (2026-08-02)

**Founder-approved 2026-08-02. A lightweight, sovereign Hermes node per EMS unit — local AI, offline-first, sync-on-reconnect. The brain's field body. (One brain, many nodes, zero lane collisions.)**

---

## 1. MISSION & ROLE
The truck-edge Hermes is the unit's LOCAL agent: it hears (whisper), sees (vision), scores (NEWS2 deterministic), speaks (EMH voice), gates device data, and bridges the drone — with ZERO cloud dependency for clinical function. It is a NODE on the Lattice, not a second brain.

**Lane ownership (single-owner doctrine):**
| Lane | Edge (truck) | Core (home Hermes) |
|---|---|---|
| Device ingestion (BLE/11073, Lifepak/Siemens/Hamilton T1) | OWNS | reads via sync |
| NEWS2 scoring + trend alerts | OWNS (deterministic) | audit copy |
| EMD scripts (offline) | OWNS | versioned from core |
| Drone gateway (MAVLink + QGC + pods) | OWNS | mission files pushed |
| Scene capture (cam/audio clips, consent-compliant) | OWNS | archive on sync |
| Provider gate / final clinical decisions | **NEVER** — stages recommendations | OWNS (provider = founder/crew) |
| Records, fleet board, analytics | never | OWNS |
| Crons / org / board | never | OWNS |

## 2. HARDWARE (per unit — the interchangeable small-computer spec)
- Jetson ONE / Orin-Nano class (16GB RAM), NVMe 1TB, IP65 enclosure, EMI-screened
- Radios: Bluetooth (devices/pods) · WiFi (scene AP + hotspot) · Cellular KORE eSIM (data) + Twilio (SMS/voice app lane) · mesh (Lattice V2V) · Starlink roam (backhaul)
- Power: 12V truck feed + battery pack; cold-boot < 60s; graceful shutdown on ignition-off

## 3. SOFTWARE STACK (containerized — Docker pattern, same image, per-unit identity)
- **Hermes edge profile** — headless agent core (no messaging gateway): local memory (SQLite/JSONL — NOT the shared Qdrant; PHI-local), skills subset (device/EMD/drone lanes), cron subset (device sweeps, battery/watchdogs)
- **whisper.cpp** — STT (crew voice, directed queries, scene audio)
- **llama.cpp GGUF** — local LLM (Qwen3-4B / Gemma-3-4B class — Jetson-class; hummingbird lane = heavier units/docked)
- **telemetry-cds-engine (NEWS2)** — deterministic scoring, 13/20-validated, NEVER the LLM
- **EMH voice** — local TTS (piper/edge offline voice pack) + barge-in
- **mavlink-router + QGC + MAVSDK bridge** — drone gateway (roof dock, missions, pods)
- **Device parsers** — Lifepak serial, Hamilton MEDIBUS, Siemens HL7 (via Mirth on-dock or direct)
- **Sync agent** — store-and-forward, E2EE, delta sync (vault-style), event log append-only (black box)

## 4. SYNC & SECURITY
- **Sync-on-reconnect**: clinical state + events + scene artifacts → core (E2EE, AES) when WiFi/cell/sat available; never in transit without encryption; PHI stays on the truck until connected
- **Per-unit identity**: sealed env per unit (unique keys), KORE fleet API provisioning, remote wipe/kill-switch
- **Audit**: append-only event log (tamper-evident) = the unit's black box (drive + clinical + drone events)
- **No secrets in sync**; .env sealed per unit; updates via signed OTA images (NUR-110 docker gate)

## 5. FAILURE & ESCALATION
- Offline = full function (dead-zone doctrine, claims 12-13)
- Provider gate: recommendations staged; escalation relayed via cellular/Starlink to core → founder/crew screen
- Failsafe: determinism first (NEWS2/EMD tables), LLM assist-only, kill-switch, black box preserved

## 6. BUILD PLAN (sim-first, evidence-gated)
| Phase | Deliverable | Date | Owner |
|---|---|---|---|
| 1 | Container image v0 (Hermes headless + whisper + GGUF + NEWS2) on Lab, SITL-validated | 08-14 | Hermes + Bridge |
| 2 | Device parsers (Lifepak sim, Hamilton MEDIBUS sim) + NEWS2 feed | 08-21 | Device specialist + Meridian |
| 3 | Drone gateway (mavlink-router + QGC + MAVSDK bridge) | 08-28 | Bridge |
| 4 | Sync agent + E2EE + black box | 09-04 | Hermes |
| 5 | In-truck pilot (one unit, simulated calls) | 09-15 | EMS team + QA |

## 7. INTEGRATIONS
EMSAgency-Spec (truck stack, local-AI doctrine) · nura-device-integration · emergency-medical-hologram · offline-ai-agent · telemetry-cds-engine · drone-swarm-division / Aero spec (roof dock, QGC, state machine) · nura-fleet-command (6h sweep heartbeat) · hermes-saas-productization (per-tenant profile pattern, NUR-106)
