# NURA Off-Grid / Polar / Remote Field-Operations Program
## Mission Charter & Scope of Work (SOW)

**Standing module owner:** Hermes (CTO) · **Program lane:** Field-Operations
**Docs:** vault `NURA-OS/Programs/` (mirrors to Notion via vault-sync) · **Code/docs mirror:** `eddieg73/NURA` monorepo → `docs/field-ops/`
**Program rule (license gate):** research + use permissive/open-source only; never copy a competitor's proprietary implementation; route "too close" to LEXA.

---

## 0. Executive summary
Stand up a **self-sufficient, offline-first, autonomy-first field-operations capability** that lets NURA operate anywhere — a defined site (sovereignty/off-grid analog), a low-connectivity clinical/EMS deployment, and space-grade resilience (Starlink/LEO uplink, Iridium polar fallback). Deliver original, testable capability in: **drone flight + GPS/coordinate telemetry**, **photogrammetric mapping**, and **resilient multi-band comms (Wi-Fi/GPS/Starlink/GPRS/GMRS/Meshtastic-LoRa/Iridium)**. Every document and position paper must carry a clear SOW, objective, and method.

---

## 1. Scope of work — what we intend to achieve
1. **Drone / UAS flight + navigation skill** — autonomous mission planning & execution (multi-rotor + fixed-wing), waypoints, geofence, failsafe, return-to-home, obstacle awareness.
2. **GPS / coordinate telemetry** — live position, heading, speed, altitude; coordinate frames (WGS84/EPSG), georeferencing, RTK/GPS accuracy; telemetry ingest into the control plane.
3. **Mapping / photogrammetry** — aerial imagery → orthophoto, point cloud, DSM/DTM/DEM, 3D model; georeferenced survey-grade products (WebODM/QGIS).
4. **Resilient communications** — a layered, red/grey/black comms stack: Wi-Fi mesh (AREDN/802.11s), LoRa/Meshtastic encrypted mesh, GMRS voice, GPRS/cellular, Starlink (LEO), Iridium (polar/global voice + M2M SBD). **Hybrid routing** (internet when available → mesh/satellite/store-and-forward when not) with **zero data loss** (the `resilient_uplink` primitive).
5. **AI-agent over comms** — Hermes controls/monitors the whole stack; agents speak over LoRa/Meshtastic/Starlink/Iridium (short structured messages: GPS coords, status, sensor readings, telemetry).

## 2. How (approach / architecture)
- **Control plane:** "Hermes = brain, executors = hands" — the `executor_control` abstraction binds any drone/vehicle/radio/mod; human-override-absolute + black-box audit.
- **Resilience:** store-and-forward uplink (`resilient_uplink` — durable local journal, buffered blackout, dedupe back-fill); offline-first clinical inference on-device; autonomous failover with bounded retries.
- **Provenance/geography:** every artifact georeferenced + auditable; EPSG/WGS84; GCP/RTK for accuracy validation.
- **Safety:** safety-gated consequential actions (NFP — no autonomous action with clinical/legal consequence without provider/human approval); sim-first (SITL) before real flight; license/spectrum compliance per band (FCC Part 95 GMRS, unlicensed ISM for LoRa, satellite ToS).

## 3. Capability stack + real, verifiable sources (license-gated)
**Drone autopilot / telemetry:**
- PX4-Autopilot — BSD-3, autopilot stack (docs.px4.io). 
- ArduPilot — GPL-3 (ArduCopter/Plane/Rover/Sub; ardupilot.org). ⚠️ GPL — use as library/separate, not linked into closed component.
- MAVLink — MIT (generated libs usable in closed-source) — the telemetry/messaging protocol (mavlink.io).
- QGroundControl — open-source GCS for MAVLink; PX4+ArduPilot (qgroundcontrol.com).
- MAVSDK / MAVROS — programmatic control (+ ROS2/DDS).

**Mapping / photogrammetry:**
- WebODM — AGPL-3.0, drone mapping (orthophoto, point cloud, DEM/DTM, 3D model), REST API, offline.
- ODX — photogrammetry engine (faster than ODM).
- QGIS (GPL) + WebODM Importer plugin; MicMac/LGT engines; CameraLib (projection).
- GPS: `.srt` (DJI) for frame geolocation; RTK/GCP for accuracy; COG (Cloud-Optimized GeoTIFF).

**Resilient comms (compare/select by mission):**
| Band | Range | BW | License | Use | Source |
|---|---|---|---|---|---|
| LoRa/Meshtastic | 2–15km/hop | ~5kbps | ISM (none) | encrypted status/GPS/mesh | resilientcomms.org |
| GMRS | 5–50W, 25+mi via repeats | voice | $35/10y family | local voice | comparisonmath.com |
| WiFi mesh (AREDN/802.11s) | 1–30km/link | Mbps | Ham (Tech+) | fixed broadband | resilientcomms.org |
| Starlink | global | 50–200×10–20 | sub | broadband, needs power+sky | resilientcomms.org |
| Iridium (GO! / inReach / SBD) | 100% incl poles | 2.4kbps, SBD 340–1960B | none | polar voice/M2M | resilientcomms.org |
| GPRS/cellular | regional | variable | carrier | when towers up | — |
| **Hybrid routing** | — | — | — | internet→mesh→sat|store-fwd | resilientcomms.org/ai-agent-comms |
- **AI-agent comms:** MeshClaw (OpenClaw plugin, LoRa/Meshtastic), MESH-APIO (off-grid AI router), Iridium SBD M2M. Agent sends short structured msgs (GPS, status, sensor).

## 4. Phases + definition of done
- **M0 (mo 1–2)** — Standing module + docs (this SOW → Notion/GitHub); research the capability stack; SITL + simulation; radio/spectrum compliance plan. *Done: docs mirrored, sim flies, band plan approved.*
- **M1 (mo 3–4)** — Drone autopilot + GPS telemetry integration into `executor_control`; MAVLink telemetry ingest; mapping pipeline (WebODM/QGIS) run on a test dataset. *Done: drone+telemetry bound to control plane; verified orthophoto produced.*
- **M2 (mo 5–6)** — Layered comms stack live: LoRa/Meshtastic mesh + GMRS + Starlink/Iridium gateway; hybrid routing + `resilient_uplink` (zero-loss blackout). *Done: mesh live; blackout drill with zero data loss.*
- **M3 (mo 7–9)** — Field/polar test: cold-soak, power lifecycle, degraded-uplink store-and-forward, autonomous failover + human-override; end-to-end remote ops console. *Done: unattended field test with audit trace.*

## 5. Governance & standing references
- Every doc/position paper: **objective · SOW · method · definition of done · owner.** 
- **License gate** before any code is merged; SBOM + `THIRD_PARTY_NOTICES.md` (per `Borg-Assimilation-Playbook`).
- **Safety:** sim-first; human-override absolute; no consequential autonomous action w/o provider/human approval; spectrum/ToS compliance.
- **Standing references:** `Extreme-Environment-Autonomy-Node-and-Robotic-Integration.md` (node spec) · `NURA-Competitive-Capability-Blindspot-Audit.md` · `Patent-Landscape-...` (whitespace) · tools `claim_chart` / `executor_control` / `resilient_uplink`.
