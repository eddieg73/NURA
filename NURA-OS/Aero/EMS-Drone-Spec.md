# NURA AERO — EMS Drone System Specification (2026-08-02)
> Companion: [[NURA-OS/Aero/Medical-Drone-Delivery-Division]] — the 2026-08-26 division charter (swarm medical-payload delivery, launch-from-EMS-vehicle, BVLOS roadmap).
Mission: 911 first-response drones — civilian + military. References (ARCHITECTURE concepts only, clean original code): Verge Aero (swarm choreography/redundancy) · Anduril Lattice (mesh + common operating picture + human-on-the-loop) · Amazon Prime Air (cloud flight management, sense-and-avoid, geofenced corridors, FAA certification approach).

## LIVERY (founder 08-02) 🍊
- **ORANGE** airframe (high-visibility — same family as Orange Star 🍊 agency identity)
- **WHITE REFLECTIVE STRIPE** with **"EMS DRONE"** text (night/thermal visibility, emergency-services recognition)
- Applies to all airframes + pods (both civilian and tactical variants keep the marking)

## PAYLOAD DOCTRINE (founder 08-02 — drugs · blood · anti-venom · etc.)
- **MEDS POD**: epinephrine (anaphylaxis/cardiac), Narcan (opioid OD), albuterol (respiratory), glucagon, TXA (hemorrhage), nitroglycerin — locked, tamper-evident, RFID-tracked, expiry-rotated; drop supervised
- **BLOOD POD (cold-chain 2-8°C)**: whole blood / packed RBC / plasma — cold-chain telemetry (temp streamed into the NURA lane, breach = red-line alert + abort/replace), O-neg first-line doctrine
- **ANTI-VENOM POD (cold-chain)**: CroFab/Anavip (crotalidae — FL diamondback/copperhead/moccasin) + coral snake antivenin — heavy, cold-chain, time-critical: drone beats ground transport in rural/trail zones (Bayshore/wilderness tie); provider-supervised administration
- **HEMORRHAGE KIT**: tourniquets, hemostatic gauze, chest seals (TCCC) — Tier 1 staple
- **ADMINISTRATION LANE (compliance)**: every Rx/controlled item = LOCKED pod + telehealth supervision (drone cam + EMH audio to the licensed provider — the founder PA prescribes/authorizes BEFORE drop) · state pharmacy-board drone-delivery rules flagged for counsel · no autonomous dispensing, ever
- **STOCK ROTATION**: RFID + expiry sweep in the 6h fleet sweep lane; blood bank partnerships (REVA/Medisun tie)

## EMD MODE — LAYPERSON ASSISTANCE (founder 08-02 — the drone is a flying telepresence clinician)
**When the drone arrives before the truck and the only hands are a bystander's:**
- **Scripted EMD decision tree (deterministic, dispatch-grade)**: unresponsive → CPR instructions + metronome (100-120/min) · bleeding → direct pressure · seizure → recovery position + timing · choking → back blows/Heimlich · anaphylaxis → EpiPen usage (pod unlock on authorization) · opioid OD → Narcan administration guidance · snakebite → immobilize + bandage (no tourniquet for venom) · childbirth → emergency delivery prompts. Layperson language, one-step-at-a-time, confirm-after-each-step
- **Telepresence flow**: drone hails via loudspeaker → bystander's CELL PHONE joins (QR/SMS link) → **AUDIO + VIDEO both ways**: drone cam (scene/patient view) + phone mic → provider screen (Hermes/EMH/TAK pin) · two-way audio via drone speaker/mic + phone speaker · EMH speaks the script; licensed provider can take over LIVE (escalation at any step)
- **The loop**: truck ETA displayed ("truck 4 min — keep pressure"), provider sees video, EMH keeps the layperson on script, every action timestamped + logged (audit)
- **Compliance**: FL two-party consent — recording notice + beep discipline · scripted EMD = deterministic (no LLM improvisation in the critical path) · provider override always available · no Rx unlock without authorization

## Tier 1 — SMALL EMS DRONE (first response, <55 lbs)
**Mission (founder 08-02): 911 RESPONSE — drugs · blood · anti-venom · etc.** — AED/defib, hemorrhage kit (tourniquets, hemostatics), Narcan, EpiPen, albuterol, glucagon, TXA, trauma dressings, **anti-venom pod (CroFab/Anavip + coral antivenin, cold-chain)** — and blood/plasma pods on request (cold-chain, O-neg first). Every Rx/controlled drop = locked pod + telehealth-supervised by the licensed provider.
- Airframe: quad/octo eVTOL, <55 lbs (Part 44809/107 lane), IP65+
- Performance: 15-25 mi range · 50-70 mph dash · 15-30 min endurance · 15 lb payload pod
- **Avionics**: RTK GPS + IMU/baro dual-redundant · **sense-and-avoid** (camera + radar + LiDAR — Amazon-model) · ADS-B in/out · Remote ID
- **Comms**: LTE/5G primary + **Lattice mesh** (drone-to-drone relay, no single point of failure) · AES-256 links · jamming/spoof detection with INS cross-check
- **Flight guidance (Amazon model)**: cloud mission planner → geofenced 911 corridors → dynamic reroute (weather/airspace) → UTM integration → BVLOS waiver stack
- **Delivery**: precision drop (winch/tether) or landing zone marker; audible/visual scene alert; onboard camera for dispatch scene assessment
- **EMS integration**: dispatch via 911 CAD integration · first-responder app (arrival ETA, payload status, live video) · voice link responder↔dispatch through the drone relay

## Tier 2 — LARGE EMS DRONE (logistics-scale, 50-250 lb payload)
**Mission**: blood products (whole blood/PRBC/plasma), meds resupply, lab samples, organs (future), mass-casualty resupply.
- Airframe: hybrid VTOL (lift+cruise), 50-150 mi range, 60-120 mph cruise, redundant propulsion
- Avionics: same stack + dual autopilot (failover), weather radar, icing tolerance
- Comms: mesh + satellite failover (military lane)
- Ground: auto-docking stations with battery/swap + cold-chain pods (blood temp monitoring telemetry into the NURA lane)

## Tier 3 — HEMS (helicopter-scale air medical, crewed-first)
**Mission**: critical-care patient transport — "NURA in every seat" includes the air.
- Platform: eVTOL (Joby/Lilium class) or hybrid; 100+ mi range; Part 135 air-carrier path
- **Cabin (the clinical spec)**: ventilator · multi-param monitor (telemetry) · suction · O2 · stretcher · drug/IV storage · **telemedicine uplink = live telemetry into the NURA CDS lane** (NEWS2 engine + provider gate in the air)
- Crew: 1-2 clinicians + pilot (autonomous co-pilot later); payload 500-1000 lbs
- Autonomy: full stack + airspace integration (UTM/ATM), emergency auto-land corridors

## COMMON SYSTEMS (all tiers)
- **SENSOR SUITE (founder 08-02 — LiDAR + vision + constant GPS, plus what was missing)**:
  - NAVIGATION: **LiDAR** (SLAM mapping, obstacle field, precision landing) · **vision cameras** (EO forward/down) · **constant GPS comm** (RTK cm-precision — truck dock = RTK base; dual GPS) · radar (mmWave — rain/fog/dust that kills LiDAR) · dual IMU + baro + magnetometer (attitude redundancy) · ADS-B In/Out (manned-aircraft deconfliction) · Remote ID (FAA)
  - SCENE: **thermal/IR camera** (night ops, victim search in brush/water, fire scenes) · **IR illuminator + spotlight** (light the scene for the layperson/crew) · **mic array** (EMD two-way audio — the drone HEARS) · strobe + PA speaker (hail, scene marking)
  - PODS: **RFID reader** (pod verify before drop) · **cold-chain temp probe** (blood/anti-venom — breach = abort) · **precision drop + winch** (lower pods where landing is impossible: brush, water, windows, roofs — no free-drop of fragile/medical pods)
  - SAFETY/COMPLIANCE: emergency parachute (failsafe ladder) · **flight data recorder (black box — tamper-evident, FAA/audit)** · geofence + LAANC/UTM integration · AES mesh · cyber kill-switch
  - ENVIRONMENT: onboard weather probe (wind/temp for landing + cold-chain ambient) · optional pods: **gas detection (CO/LEL/H2S)** + **radiation probe** (HazMat/MCI scenes — disaster-response tie)
- **AMBULANCE-MOUNTED DRONE (founder 08-02 — mobile base doctrine)**: Tier 1 drone docks ON TOP of every ambulance — roof auto-dock (launch/land/recover) + battery swap + pod reload at the dock · the truck = mobile base station: charge while driving, mesh relay node, provider console, second drone bay optional. **Response model: "DRONE FIRST, TRUCK FOLLOWS"** — on dispatch, the drone launches ahead (15-25 mi at 50-70 mph), arrives minutes before the truck, delivers the pod + runs EMD telepresence (audio/video to the crew + provider); the truck catches up with the stretcher. **EXEMPLAR — MANATEE COUNTY (founder 08-02)**: rural east (Myakka City, Parrish, Lakewood Ranch east), beach zones (Anna Maria), I-75 corridor + long rural roads = 15-25+ min response zones — the roof-mounted drone cuts first-contact to under 5 min; county EMS partnership lane (Manatee County EMS) + fire districts; launch safety: cleared airspace check, no launch while lights/siren in congested traffic without crew verification, RTL to truck or scene
- **EDGE COMPUTE & COMMS ON EVERY DRONE (founder 08-02)**: small Jetson (Orin-Nano class) per drone — onboard AI: vision (scene, target, AED-drop verification, landing zone), sense-and-avoid assist, payload status, telemetry preprocessing — LOCAL-AI doctrine same as trucks (offline-capable, deterministic safety underneath). ALL COMMS: WiFi mesh (Lattice V2V — drone↔drone↔truck) · cellular KORE eSIM (BVLOS/roaming) · BLE (payload pods, ground links) · Remote ID (FAA) · sat link on LARGE/HEMS tiers. Weight/power honesty: Orin-Nano 7-15W fits SMALL tier (<55lb); LARGE/HEMS carry full Jetson + sat; tiny close-range quads may run lighter NANO SKUs
## TACTICAL MEDICAL ROLE (founder 08-02 — TEMS/TCCC drone support)
**The drone as the tactical medic's wingman — point-of-injury support in high-threat environments (TEMS/SWAT, PJ/special-forces lane, active scenes).**
- **CARE-UNDER-FIRE SUPPORT**: pod delivery to the POINT OF INJURY (hemorrhage kit, tourniquets, chest seals, TXA) without exposing the medic — precision drop/winch into cover; casualty location via thermal (who's down, where, moving?) relayed to the team's TAK
- **REMOTE MEDICAL DIRECTION**: drone cam + mic gives the remote physician/PA eyes-on the casualty DURING extraction prep — provider-gated guidance (tactical-medicine-swat + hermes-clinical-safety-escalation lanes)
- **TACTICAL INTEL FOR THE MEDIC**: route/cover analysis (best covered approach, danger areas), overwatch while the medic works (perimeter watch + alert), extraction route recon + landing coordinates for CASEVAC
- **DISCIPLINE (tactical doctrine)**: team-authorized ops only · position/noise discipline (hover behind cover, no unnecessary light/audio) · medical mission PRIMARY (never weaponized, never offensive) · works in the tactical COP (Lattice + TAK + earpiece lane — PJ integration) · every action logged for after-action review + evidence chain
- **Handoff**: tactical scene → casualty evacuation → overwatch converts to medical assist (EMD/landing protocols) the moment the team says "medic up"

## OVERWATCH MISSION MODE (founder 08-02 — launch for overwatch for paramedics or law enforcement)
**The drone becomes the eye-in-the-sky for ground teams — OBSERVE + RELAY + ALERT, never intervene or interfere.**
- **PARAMEDIC OVERWATCH**: crew on scene in dangerous/isolated zones (night, rural, MCI, wilderness, hostile environments) — drone holds overhead: scene camera + thermal (victim/subject/vehicle detection), perimeter alert (movement outside scene = warning to crew), route recon (best ingress/egress + landing coordinates for air/ground assets), extraction support, live feed to truck console + provider + TAK pin; pod pre-stage (hemorrhage/AED) in case the crew needs a resupply without leaving the patient
- **LAW ENFORCEMENT OVERWATCH** (partnership lane — agency MOU): tactical scenes (barricade, pursuit, search), thermal subject tracking, crowd/perimeter monitoring, scene documentation (evidence-preservation aerial photos), K9/search support (thermal for missing persons in brush/water). DISCIPLINE: agency-authorized only (MOU + request protocol) · jurisdictional + privacy/4th-Amendment review by counsel · recording notice where required · evidence-chain data retention (black box + audit) · NEVER weaponized — medical drone, observation-only
- **OVERWATCH DOCTRINE**: observe + relay + alert only · altitude discipline (public-safety ops altitude, above ground-team heads, below manned traffic) · battery-aware loiter (10-15 min at altitude → auto-RTL/replace) · auto-switch to EMD/landing protocols if the ground team calls for pod delivery or the scene becomes a medical scene (overwatch → assist handoff) · every overwatch logged (start/end, subject events, handoffs)

## AUTONOMOUS MISSION STATE MACHINE (founder 08-02 — the drone flies itself and renders assistance)
**Dispatch → "DRONE FIRST": the drone flies ITSELF to GPS/address coordinates, then executes arrival protocols and renders assistance — human-on-the-loop (override + failsafe ladder always armed).**

### States
1. **TRANSIT** — autonomous flight to GPS/address (RTK + LiDAR SLAM + geofenced corridor + ADS-B deconfliction); KORE cell + mesh + sat telemetry; speed 50-70 mph
2. **ARRIVAL / SCENE ASSESS** — hover at safe altitude (300-400 ft default → descend): LiDAR + vision + thermal classify the scene — caller/patient located? landing zone clear/obstructed/water? hazards (wires, traffic)? → MODE SELECT (deterministic table)
3. **ARRIVAL PROTOCOLS (the four modes):**
   - **HOVER PROTOCOL** — hold position: scene camera + EMD telepresence live (audio/video to crew + provider), monitoring until truck arrives; no landing needed (observation/remote assist)
   - **911 CALLER PROTOCOL** — caller/witness located: hail via PA + strobe, connect the caller's CELL PHONE (QR/SMS link) → EMD scripted guidance + provider live; caller guided to the patient if separated
   - **PATIENT PROTOCOL** — patient identified: descend toward patient (LiDAR-verified), deliver pod (precision drop or winch) + EMD guidance to the hands AT the patient; thermal confirms patient position at night
   - **SAFE LANDING PROTOCOL** — clear zone + hands-on pod needed (AED pads, anti-venom admin): LiDAR-verified clear landing zone → auto-land → deploy (bystander opens pod; EMD talks them through) → monitor → auto-relaunch/recover
4. **ASSIST** — pod deployed + EMD script + vitals/visual monitoring streamed (NEWS2 context), truck ETA relayed; provider override any time
5. **RECOVERY** — RTL to truck roof dock (RTK cm landing) / new mission / safe-land + parachute failsafe

### Mode-select table (deterministic)
| Scene finding | Mode |
|---|---|
| Patient visible + clear zone | SAFE LANDING (hands-on) |
| Patient visible + obstructed/water | PATIENT (winch/drop) |
| No patient visual + caller connected | 911 CALLER |
| No caller + no patient visual | HOVER (scene watch + search pattern) |
| Hazard (wires/traffic/storm) | HOVER at safe altitude → abort to RTL if escalating |

**Autonomy doctrine**: flies itself by default (Lattice human-on-the-loop) · every state logged (black box + audit) · any override or failsafe (geofence → RTL → avoidance → parachute → kill-switch) beats autonomy · sim-validated mission profiles first (SITL/Gazebo — never fly unvalidated)

## GROUND CONTROL & TRUCK FLYING (founder 08-02 — control from the truck on a mobile app)
- **QGroundControl (QGC) on the truck tablet** — open-source GCS (Android/iOS), ANY MAVLink drone (PX4/ArduPilot = our stack): live fly view, mission planning, multi-vehicle, video streaming, sensor calibration. Primary truck station: sunlight-readable tablet, RAM mount, dock power
- **MAVSDK** — the custom-app lane: NURA app gains a DRONE PILOT MODE (fly/waypoints/EMD camera view/pod release) via MAVSDK (Kotlin/Java Android client verified); web-GCS pattern (FastAPI + MAVSDK PWA) ties Hermes Mission Control to the drone (mission files from swarm-sim → GCS → MAVSDK → SITL — sim-first path already in the skill)
- **ATAK/CIVTAK plugin (verified: ATAK-CIV SDK 5.5 MAVSDK integration pattern, 30+ published plugins)** — drone telemetry + control on the tactical map: the operator screen ties to the PJ/TAK lane
- **mavlink-router on the truck Jetson** — ONE radio on the drone, MANY clients: QGC + NURA app + TAK + Hermes (UDP fan-out, no port fights)
- **Control links**: mesh (Lattice V2V) → cellular (KORE eSIM) → Starlink; RC fallback controller stays for MANUAL OVERRIDE (safety doctrine — app never replaces the physical override)
- **Mount**: truck tablet (RAM/mil mount, glove-friendly, dock power, sunlight-readable), crew-side second screen optional
- **Lattice mesh OS**: one operating picture — every drone, pod, station, and telemetry feed; human-on-the-loop autonomy; failsafe hierarchy: geofence → RTL → avoidance → parachute/controlled descent → cyber kill-switch (safe-land all)
- **Simulation-first**: Gazebo/SITL validate every mission profile before flight (never fly unvalidated — Verge/Aero discipline)
- **Security**: military-grade hardening (mesh AES, anti-spoof, tamper-evident pods, no PHI in transit without encryption)
- **Fleet ops**: auto-docking, battery logistics, maintenance prognostics, flight log black box

## Regulatory roadmap
Part 107 + waivers (107.29 night · 107.39 over-people · 107.31 BVLOS) → Part 44809 fixed-site → Part 135 (HEMS) · Remote ID + LAANC · UTM integration · military lane = DoD flight clearances per site

## Commercial model
Tier 1+2 fund Tier 3: 911 contracts (municipal EMS) + rural coverage + event medical → HEMS operator partnership. Show revenue (Verge lane) as the seed.
