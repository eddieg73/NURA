# RATCHET MEDICAL DRONE FLEET (RMDF) — the core subsystem (2026-08-04, founder canonical)

**A fleet of specialized autonomous medical drones coordinated by Hermes and supervised by Ratchet — drones reach patients long before human teams, on Mars, the Moon, Antarctica, disaster zones, and rural Earth.** Architecture: Hermes Mission Kernel → Ratchet Medical AI → {Medical UAV · Ground UGV · Micro Indoor Drone} → the Shared Medical Cloud.

## THE 11 SPECIALIZED PLATFORMS
1. **Scout Drone** — find casualties · assess hazards · 3D maps · heat signatures · comms relay. Sensors: 4K optical · thermal · LiDAR · night vision · gas · radiation · atmospheric · GPS/RTK (Earth) · Visual SLAM (Moon/Mars). Medical: count casualties · detect movement/breathing · camera-based photoplethysmography pulse estimation (where conditions permit) · identify severe bleeding/burns · unconscious detection.
2. **Medical Supply Drone** — tourniquets · blood products (where feasible) · IV fluids · antibiotics · oxygen · AED · airway kit · trauma dressings · burn kits · meds · ultrasound · lab cartridges. **Earth example: MI 8 miles away → Ratchet dispatches AED + aspirin + O2 + ECG + video link BEFORE EMS arrives.**
3. **Telemedicine Drone** — two-way video · digital stethoscope · US probe · ECG · pulse ox · BP · mic array · speakers · AI translator — **the physician examines the patient remotely.**
4. **Trauma Drone** — massive hemorrhage: tourniquets · hemostatic gauze · pressure dressings · chest seals · junctional tourniquets · pelvic binder · TXA · IO kit — Ratchet walks bystanders through treatment.
5. **Airway Drone** — BVM · oxygen · suction · laryngoscope + video laryngoscope · cricothyrotomy kit · ETCO2 — Ratchet guides a qualified responder step-by-step; advanced airway stays under trained human supervision unless robotic systems are separately validated.
6. **Ultrasound Drone** — lands, deploys portable US; Ratchet: "Place the probe exactly where shown" → CV confirms placement → AI interprets: FAST · pneumothorax · pericardial effusion · pregnancy · cardiac function.
7. **Pharmacy Drone** — mission-specific meds; Ratchet knows allergies/weight/renal function/interactions; dispenses ONLY after verification + authorization policies are satisfied.
8. **Blood Drone** (future) — whole blood · plasma · platelets · cryoprecipitate; maintains temperature · shock detection · chain of custody (health systems have already demonstrated drone blood delivery).
9. **Laboratory Drone** — portable diagnostics: CBC · chemistry · lactate · troponin · blood gases · INR · CRP · glucose · pregnancy · urinalysis — results auto-populate Ratchet.
10. **Surgical Support Drone** — NOT autonomous surgery: sterile instruments · suction · lighting · cameras · retractors · sutures — the circulating assistant.
11. **Swarm Drone** — multi-casualty: ten drones launch (map · find · blood · AED · comms · hazards · telemetry) — Hermes coordinates.

## MARS
Dust storm · rover crash · habitat 12 km away → Ratchet launches: D1 thermal · D2 oxygen · D3 ultrasound · D4 comms relay · D5 medical supplies — while Hermes calculates oxygen remaining · radiation · weather · safe route · rescue ETA.

## ANTARCTICA (the proving ground)
Snowmobile rollover → scout drone finds the victim → drops: heated blanket · satellite communicator · oxygen · trauma kit → begins the video consult with the station physician.

## EARTH (commercially valuable immediately)
EMS · fire departments · rural hospitals · search and rescue · military medicine · offshore platforms · cruise ships · national parks · disaster response · large industrial sites · remote clinics.

## INTEGRATION (NURA/Hermes)
911 Call → Hermes Mission Kernel → Ratchet Clinical AI → {OpenEMR · NURA EMR · PACS · Pharmacy · Inventory · Weather · FAA/UTM (Earth) · Mission Control} → the Medical Drone Fleet → Patient Encounter.

## FUTURE CONCEPTS
**Drone Docking Network** — autonomous charging/resupply docks at every fire station, hospital, Antarctic station, lunar habitat, Mars base. **Medical Drone Ambulance** — larger VTOL with advanced monitoring + eventually a patient (a much larger engineering/regulatory challenge). **Drone-to-Robot Collaboration** — the drone locates, the ground robot arrives with heavier equipment, Ratchet coordinates. **Drone Manufacturing** — Mars: a damaged propeller → Ratchet identifies the failed component → the local fabrication system prints a validated replacement → back to service. **Digital Twin Fleet** — per drone: battery health · motor status · flight hours · maintenance history · payload inventory · sterilization status · sensor calibration · predicted failures — Ratchet predicts maintenance BEFORE mission-critical failure.

## THE RECOMMENDATION
**Build the Ratchet Autonomous Medical Fleet with specialized roles — not one medical drone.** A failure of one platform doesn't eliminate the capability; each drone optimizes for its mission; it scales from terrestrial EMS/disaster → Antarctic stations → lunar bases → Mars settlements.
