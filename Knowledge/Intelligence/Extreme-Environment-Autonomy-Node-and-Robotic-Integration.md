# Extreme-Environment Autonomy Node + Robotic/Executor Integration (Mars/Antarctica-grade)

**Directive:** "get to the moon / function in Antarctica within 6–9 months." Grounded framing: NURA's offline-first + sovereignty + Mars-grade doctrine, scaled to a **no-cloud, unattended, autonomy-first node** and a **unified executor-control layer**. This is the real, buildable version of that ambition.

## Part A — The autonomy node (deployable enclosure)
Real Antarctic autonomous systems (PLATO observatory, KAREX rover, BAS Halley VI, Dourbes magnetic observatory) set the engineering envelope:

### A1. Power (the #1 constraint; winter = polar night, no grid)
- Solar ONLY works in the austral summer; winter needs a **fuel/battery generator**. Halley VI uses a **Capstone C30 micro-turbine** (30kW, runs unattended ~265 days, -55°C, ~9.5kW avg, ~150 autonomous fuelling events). PLATO uses **Hatz 350cc diesel** micro-engines (~1kW average for 2 years, 6,000L fuel). KAREX uses **swappable batteries + thermal insulation** for -50°C.
- → Our design: **solar (summer) + diesel/battery gen (winter) + redundancy + thermal**. Target average continuous load while preserving the clinical compute.
- Note: solar panels produce ~25% MORE than nominal in Antarctic conditions (high flux + snow reflection + negative temp coefficient) — size accordingly.

### A2. Thermal (-50 to -80°C)
- Thermal management is "one of the easiest to solve" IF done correctly: heated/insulated enclosures, foam-sandwich radome for RF, rugged SBCs (**BeagleBone Black rugged, -40..80°C** or equivalent), instrument-specific localized heating (e.g. a sensor that only needs heat below -20°C).
- → Sized, insulated, internally-heated enclosure; RF hardware in a foam box (self-heating often sufficient).

### A3. Comms (no geostationary reachable south of ~-75°; MUST use polar-orbiting)
- Iridium satellite network (66 polar sats, global coverage). Iridium OpenPort ~128kbps; PLATO ~30MB/day; Princess Elisabeth station caps 56kbps.
- Real-time IPC: **MQTT over the satlink** (as used by the Dourbes observatory) — QoS1, keepalive ~10s, publish to a broker at HQ, ~300ms latency. Store-and-forward + local file copy is mandatory.
- → Latency-tolerant, store-and-forward, offline-first messaging; MQTT to a back-home broker; never rely on low-latency round-trips.

### A4. Autonomy & failover
- Unattended 6–11 months; automated recovery after N retries; **remote-control priority over autonomous mode**; multi-robot task scheduling; health/status continuously monitored; fuel/data/thermal all monitored telemetrically.
- → NURA's existing watchdog/self-heal/autonomy-audit cron stack maps directly (bounded retries, graceful degrade, human-override-absolute).

### A5. Clinical AI on-device (the NURA-specific differentiator)
- Run the **LOM / Needle-2 / on-device models** for offline inference (no cloud). Offline-first clinician sync; decision + safety scores computed locally, provider-gated. This is what makes a *clinical* autonomy node distinct from a generic observatory.

## Part B — Executor integration (Hermes=brain, executors=hands)
- **Unified actuator-control abstraction** (per doctrine: Home Assistant for house/drones, OBD for vehicles, Garmin/Onyx for aircraft). Bind ANY executor to the same control plane: openpilot, drones, robots, medical devices.
- **Vendor-API pattern (the Tesla Fleet API model):** OAuth2 (client id/secret → user access token) + scopes + a **public key hosted at the app's domain** (`/.well-known/appspecific/<vendor>.public-key.pem`) + Fleet Telemetry streaming. Onboard per region (register endpoint per region). This is the sanctioned integration template for ANY vendor device API.
- **Tesla Optimus** — currently NO public SDK/API (not exposed). It will follow the same pattern when/if opened. We build the abstraction NOW so a future Optimus/robot binds cleanly.
- **Open humanoid/robot SDK** alternatives (for real integration today): platforms exposing control SDKs (e.g. Unitree, ROS2-based bots) — same abstraction, different vendor connector. Route through the existing control-lane router.

## Part C — 6–9 month phased plan
1. **M0 (mo 1–2):** Autonomy-node physical design: power/thermal/comms sizing; select rugged SBC + enclosure; design power budget around the offline clinical AI load.
2. **M1 (mo 3–4):** Offline clinical-inference + offline-first sync on the node; MQTT broker + store-and-forward back to HQ; watchdog/failover hardening.
3. **M2 (mo 5–6):** Executor-control abstraction live (Home Assistant/drone/OBD connectors + OAuth2/public-key vendor pattern); an open-SDK robot test bench; Fleet-API-style connector template.
4. **M3 (mo 7–9):** Full unattended cold-chamber + simulated-Antarctic test (power soak, -50°C thermal, satlink store/forward, failover drill); field-deploy checklist; remote ops console.

## Verification before we claim "it works"
- Power: sustained load through a simulated polar-night battery/solar budget.
- Thermal: electronics stable at -50°C for 48h+; recovery from cold-soak fault.
- Comms: store-and-forward survives a satlink blackout; no data loss (QoS1 + local copy).
- Autonomy: unattended for a defined window with zero-touch, auto-recovery, human-override-absolute preserved.
- Clinical: offline inference + safety-gate + provider-gated decisions, audit trace intact.

## Honest constraints
- **Tesla Optimus has no public integration API** → integration is architectural (abstraction + vendor pattern), not a live link, until Tesla exposes it.
- **NURA Link** must be identified before we can spec its integration (see follow-up).
- "Moon" literal = not feasible in 6–9 mo; "Antarctica/Mars-analog autonomy node" = feasible with the above.
