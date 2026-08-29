# NURA Meshtastic Deployment Plan — FULL DEVICE MESH + RIS/PACS (2026-08-16)

License-free LoRa mesh (915 MHz US, FCC Part 15). Zero-infrastructure comms + device telemetry backbone. **The mesh carries METADATA ONLY — never PHI** (device IDs, statuses, accession numbers, GPS — no names, no images, no results).

## 1. The complete device topology
| Layer | Devices | Payload |
|---|---|---|
| **Radiology** | CT · US · XR modalities (gateway bridges), portable US, workstation nodes | Modality status (IDLE/SCANNING/COMPLETE), study-complete + accession, DICOM echo |
| **Patient monitors** | Lifepak · Hamilton T1 · vitals carts (via existing device-integration lane) | Telemetry signals (score only), alarm state, battery |
| **Vehicles** | 2× T-Beam Supreme (NURA-2/3) | GPS 120s, status texts |
| **Drones** | Payload node (Phase 4) | GPS, flight state, landing-zone ping |
| **Base** | Heltec V3 gateway at the Clinic (NURA-1) + roof relay | Mesh → MQTT → Hermes → RIS/PACS/Telegram |
| **Go-bags** | 1× T-Beam spare | GPS + SOS beacon |

## 1B. EMS VEHICLES + MEDISUN TOWERS (founder directive 2026-08-16)
- **EMS vehicles**: T-Beam Supreme + 5.8dBi NMO whip + 12V power, role CLIENT, smart-position GPS → the live fleet map
- **Medisun towers (each building incl. affiliates)**: Heltec V3 + 8dBi rooftop omni + lightning arrestor + solar/battery, role ROUTER, fixed lat/lon
- **Comms best practices**: EMS-OPS channel with custom 256-bit PSK (rotated quarterly) · 915MHz LongFast · role discipline (towers ROUTER, vehicles/handhelds CLIENT) · max 3 hops · the N Miami↔Little Haiti 4.6mi leg = direct LoRa; the 19.6/23.4mi legs = MQTT/Tailscale backhaul · clinical data = TLS backhaul; LoRa = telemetry/metadata
- **BOM**: 3 sites + 4 vehicles ≈ $300-400 total

## 2. RIS/PACS integration (the point)
The gateway router parses structured mesh payloads and routes them:
```
{MOD:CT1,ST:SCANNING}          → RADRIS: modality status update
{MOD:CT1,ST:COMPLETE,ACC:1234} → RADRIS: study ready for read → OHIF worklist
{DICOM:ECHO}                   → Orthanc /echo → series count
{DEV:LIFEPAK,SC:3,BAT:82}      → device-lane telemetry CDS (NEWS2 scoring)
```
- **RADRIS API**: POST modality/study status (Clinic, radris-stack).
- **Orthanc**: /system echo + /studies polling for worklist freshness.
- **Hermes**: every notable event → Telegram to the founder (`📡 MESH:` prefix).
- No DICOM data over the mesh (bandwidth + PHI doctrine). The mesh tells the RIS *that* a study is done; Orthanc moves the pixels over the wire.

## 3. Hardware buy list (unchanged starter + radiology adds)
- Starter: 2× Heltec V3 ($36–60) + 2× T-Beam Supreme ($80–110) + 2× 18650 + 2× SMA antennas + RAK solar repeater later ($80–120).
- Radiology adds: per-modality WiFi→mesh bridge (ESP32/Heltec V3 in the room, wired to the modality's network via a sanctioned relay — no direct modality tampering), ~$25/room.

## 4. The bridge software
- `/opt/data/scripts/meshtastic/mesh-router.py` — gateway-side router: mesh JSON → RADRIS / Orthanc / device-lane / Hermes (built 2026-08-16).
- `config-gateway.yaml` — radio config (NURA-1, LONG_FAST, US).

## 5. Phases
1. **Day 1:** flash + range-test the Heltec pair.
2. **Gateway live:** monitor stack + router → Telegram.
3. **Vehicles + go-bags:** GPS on the map.
4. **Radiology rooms:** modality bridge nodes → RADRIS statuses + OHIF worklist notifications.
5. **Solar repeater + drones:** full coverage + air nodes.

## 6. Hard rules
- NO PHI on the mesh, ever (no names, no images, no results) — metadata only.
- PSK-sealed channel; unsealed defaults never deployed.
- Modalities are never directly modified — the bridge sits on the network side, read/status only.
