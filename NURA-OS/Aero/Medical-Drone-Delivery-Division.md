# NURA AERO — Medical Drone Delivery Division

> Division charter (2026-08-26). Founder directive: stand up a **swarm-capable medical payload delivery** capability — EMS drones that deliver medications (antivenom, epi, TXA, blood) to a scene, launched from an EMS support vehicle / fire-rescue station, and (North Star) transport organs. This is the **clinical logistics lane** of the Aero division.
>
> Companion: `Aero/EMS-Drone-Spec.md` (technical system spec) · `drones/drone-swarm-division` skill (swarm doctrine).

## Mission
Deliver **time-critical medical payloads** by drone, faster than ground/air transport can reach them, to improve survival for: snakebite envenomation, anaphylaxis, opioid overdose, severe hemorrhage, and (eventually) organ transplantation. One capability, three payload tiers. **Drone-first, truck-follows** response doctrine.

## Why this is real (verified precedents — 2026)
| Precedent | Proof |
|---|---|
| **UMD/UMMC (Apr 2019)** | First-ever human organ by drone: a kidney flown 2.8 mi / 9.5 min, transplanted. 8-rotor + dual powertrains (redundancy), mesh comms, parachute, **HOMAL payload monitor** (temp/altitude/vibration/GPS → live telemetry). |
| **Zipline (Rwanda/Ghana)** | Antivenom + blood at scale. Catapult fixed-wing, 3 kg payload, parachute drop, 2–8°C cold-chain + barcode chain-of-custody. **−67% blood expiries, −51% maternal mortality.** |
| **ArcherFRS + Tampa General + OneBlood + Hillsborough Co Fire Rescue (Aug 2026)** | **The exact model — nation's first EMS-driven whole-blood-to-scene.** Drones staged at fire-rescue stations (Ground Control Hubs), paramedics request from a phone, whole blood to a hemorrhagic trauma scene in **<3 min**, ~6.5–7 lb payload, day/night. (Also: AED + Narcan + EpiPen, Manatee County EMS.) |
| **SUNY Upstate (Apr 2026)** | FAA **BVLOS waiver** over people, moving vehicles, and at night across a ~50-mi corridor (through June 2029). 7,200+ med deliveries. |

## Payload tier ladder
| Tier | Payload | Cold chain | Bar | Status |
|---|---|---|---|---|
| **A — Meds** | Antivenom (crotalidae/coral), epinephrine, TXA, Narcan, albuterol, glucagon, AED | 2–8°C (or room-temp product-specific) | Locked, tamper-evident, RFID + expiry-rotation pod | **MVP — build first** |
| **B — Blood** | Whole blood / PRBC / plasma / components | 2–8°C, validated, chain-of-custody, temp live-streamed (breach = abort/replace) | O-neg first-line doctrine; blood-bank (AABB) protocol | **Proven in FL now** |
| **C — Organ** | Kidney/liver/heart (future) | Temperature + barometric + vibration + altitude monitor (HOMAL-class) | OPO/UNOS coordination; redundant airframe; parachute | **North Star, 2–3 yr program** |

## Launch-from-EMS-vehicle model
1. **Station/vehicle hub (proven, ArcherFRS model):** drone standing ready charged on a Ground Control Hub at a fire-rescue station or on the support vehicle; paramedic requests from a mobile device → autonomous launch → BVLOS to scene. Agency keeps operational control + Certificate of Waiver authority.
2. **Mobile / roof-dock (the spec's "ambulance-mounted drone"):** Tier-1 drone docks on the ambulance roof — auto-dock (launch/land/recover) + battery swap + pod reload; the truck = mobile base (charge while driving, RTK base, mesh relay node, provider console). **Drone launches first, arrives minutes before the truck, runs EMD telepresence.**

## Swarm / Lattice doctrine
- **Redundancy via fleet:** 2–3 drones for one critical payload — one confirmed arrival (UMD did this at airframe level: 8 rotors / dual powertrain).
- **Mass-casualty:** many simultaneous deliveries, one per casualty (MCI/disaster).
- **Mesh everything:** drone↔drone↔truck mesh (Lattice V2V) — no single point of failure; extend range where cellular drops.
- **Fleet-as-a-system (COP):** every drone + payload telemetry on one board; human-on-the-loop autonomy; failsafe ladder (geofence → RTL → avoidance → parachute/controlled descent → safe-land-all).
- **Edge AI on vehicle** (Jetson Orin-Nano class): vision, sense-and-avoid, landing-zone verify, telemetry preprocessing — offline-capable, deterministic safety underneath.

## Regulatory gates (the hard parts)
- **BVLOS (107.31)** — the gate. Night (107.29), over-people (107.39). Achievable (Upstate/ArcherFRS prove it); needs safety case + waiver/COW holder or managed-service path.
- **Chain of custody + temp telemetry** — every payload logged; 2–8°C cold-chain.
- **Deconfliction** — NOTAM, LAANC/UTM, sense-and-avoid, airspace sanitization. Remote ID.
- **Clinical governance** — medical-director oversight; AABB (blood); OPO/UNOS (organ); DEA/drug handling (no autonomous dispensing, ever — provider-supervised pod unlock).
- **Post-drop** — provider (PA) supervises administration via telehealth (drone cam + two-way audio) before/at drop.

## MVP phasing (sim-first, never fly unvalidated)
1. **Phase 0 — SITL swarm proof:** stand up `aerial-autonomy-stack` (PX4/ArduPilot + ROS2 + Jetson), 50–100 drone sim — formation, mesh, redundancy demo. *Deliverable #1.*
2. **Phase 1 — Tier A field pilot:** real BVLOS antivenom/epi/Narcan delivery from a fixed hub; managed-service/partner model.
3. **Phase 2 — Tier B blood:** cold-chain + chain-of-custody, partner blood bank + trauma center (the Hillsborough template).
4. **Phase 3 — Tier C organ:** redundant airframe + HOMAL-equivalent + OPO/UNOS coordination (UMD blueprint).

## Deliverables
SITL swarm sim proof (100+) · FAA BVLOS waiver roadmap · show-safety SOP · payload-pod spec (lights + defib + cold-chain) · chain-of-custody/black-box spec · EMD telepresence runbook.

## Commercial / partnership model
911/municipal + rural EMS contracts + event medical, fund the HEMS/clinical lane. **Strategic note:** the blood-to-scene program is running in Hillsborough (Tampa) — model it, partner with a managed-service vendor, or build in-house (IP doctrine: reference public architecture, build original).

## Security
Encrypted control links (mesh AES) · GPS-spoof/jam detection + INS cross-check · anti-hijack (crypto-authenticated commands) · no PHI on swarm payloads · cyber kill-switch (safe-land all) · flight black box (tamper-evident).
