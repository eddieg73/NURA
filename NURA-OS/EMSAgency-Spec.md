# ORANGE STAR 🍊 — NURA EMS Agency · Mobile Integrated Health (spec 2026-08-02)

## BRAND (founder 08-02 — mockup approved) 🧡
- **Agency legal/operating name:** ORANGE STAR 🍊
- **Vehicle + consumer-facing brand:** **NURA HEALTH** (founder: "I like Nura Health") — MIH unit livery
- **Livery (verified mockup, vault Brand/nura-health-mih-unit-livery.jpg):** SAFETY ORANGE primary · NAVY BLUE accent bands · WHITE lettering · chrome/diamond-plate trim · Star-of-Life logo ("NURA HEALTH" + "MOBILE INTEGRATED HEALTH UNIT") · "PARAMEDIC + NURSE PRACTITIONER" · "IN PARTNERSHIP WITH YOUR LOCAL FIRE DEPARTMENT" · "BRINGING CARE HOME. STRENGTHENING COMMUNITIES."
- **Fleet color family:** matches Aero drones (orange + white reflective "EMS DRONE") — one visual identity across ground + air


NEW COMPANY (founder). Mobile Integrated Health (MIH) units: NP or PA + ambulance or fly car, PARTNERED with local EMS agencies / fire depts / hospitals. First unit: LAUDERHILL (Broward). Partner clinic: Medisun Health Group. Revenue lane: REVA Air Ambulance ground-portion partnership.

## Business model (founder clarified 2026-08-02 — PARTNERSHIP-FIRST)
NURA EMS does NOT displace local EMS/fire — it AUGMENTS them under partnership:
- **Provide**: NP or PA + the ambulance OR "fly car" (ALS quick-response vehicle — SUV-based, paramedic-level, scene-first)
- **Partners**: local EMS agencies · fire depts · hospitals — MOU-based augmentation (staffing relief, 911 alternative response, MIH, inter-facility, event standby)
- **Founder = the PA provider**: Eddie Garrido, PA-C/EMT-P (FL Paramedic PMD13383) is the company's clinical operator — the MIH unit's NP/PA seat is founder-filled; the org builds around him (he does not build around the org)
- **Fly car spec**: SUV platform (Tahoe/Explorer-class), ALS kit, BLE telemetry + Jetson edge (truck stack applies), lights/siren, scene camera, Med 8 radio
- **Revenue**: partnership fees/contracts · MIH service contracts (911 call reduction) · interfacility (REVA ground) · event medical · grant-funded mobile stroke/cardiac outreach
- **Texas 911 outbid lane**: SEPARATE track — the partnership model builds the license + record; 911 RFP bidding is the later growth lane (AMR/PP study already filed)

## The model (references)
- **The Villages + UF Health Mobile Stroke Unit**: CT-on-wheels, telemedicine stroke neurologist, fire-dept partnership — stroke outcomes via earlier treatment
- **LA Fire NP1**: NP-led mobile integrated health ambulance — 911 alternative response, chronic/behavioral/post-discharge care, 911 call reduction
- **NURA MIH unit**: NP or PA + paramedic + driver; telemedicine + the NURA CDS lane (telemetry, NEWS2, provider gate); Medisun clinic = medical home for follow-up

## FLORIDA LICENSURE PACKAGE (verified 2026-08-02 — DOH Bureau of EMS)
1. **DH Form 631** — Ground Ambulance Service Provider License (ALS/BLS) — submit ≥30 days before start
2. **COPCN** — Certificate of Public Convenience & Necessity from the BROWARD COUNTY COMMISSION (each county served)
3. **Medical Director** — FL-licensed physician + DEA cert (ALS); contract/LOA + license copy (401.265 F.S.)
4. **DH Form 1510** — vehicle permit applications (per ambulance)
5. **Insurance** — vehicle liability (sums per DOH) or self-insurance w/ OIR approval
6. **Trauma transport protocols** — signed by medical director
7. **Radio comms** — approved system via DMS (Med 8 to hospitals required)
8. **Management plan** — training program, dispatch protocols, complaint system, accident handling, QA program (401.25(2)(h))
9. **Staffing** — ALS: paramedic + EMT/driver (401.25(8)); interfacility 401.252 exception
10. **Fees** — per 401.34 F.S. · random inspections after license

## Truck tech stack (founder 2026-08-02 — every unit)
- **Edge compute PER UNIT: Jetson ONE (NVIDIA Orin-class) or other small computer (NUC/Orin-Nano class — interchangeable spec, founder 08-02)** — onboard inference: vision (scene/camera), telemetry CDS (NEWS2 offline), BLE device ingestion; works in dead zones; THREE REQUIRED RADIOS on every unit: **Bluetooth + WiFi + Cellular**
- **LOCAL AI ON THE TRUCK (founder 08-02 — doctrine)**: the unit runs the FULL clinical AI stack LOCALLY — whisper.cpp STT (hearing), on-device LLM (llama.cpp GGUF / hummingbird-class lane) + deterministic NEWS2 (scoring), vision ONNX models (scene/patient assist), EMH voice (local TTS) — **ZERO cloud dependency for clinical function**; PHI never leaves the truck except store-and-forward sync (E2EE, on-reconnect); offline-ai-agent doctrine applies (claims 12-13 embodiment)
- **Starlink** — sat backhaul (rural/911 coverage), roam profile; fallback: cellular + mesh
- **WiFi** — truck AP (scene hotspot, clinic docking, crew tablets) + WiFi-calling path
- **Bluetooth** — BLE patient monitors/devices (medical-device-connectivity lane: IHE PCD/11073), stethoscope/otoscope pods
- **Mesh phone** — Lattice-style mesh node (vehicle-to-vehicle/phone mesh, no carrier needed; drone-swarm relay tie)
- **Cellular eSIM — KORE Super SIM** (acquired Twilio IoT, 2023; eSIM profiles via SM-DP+, 400+ networks/180+ countries, multi-IMSI failover, fleet APIs). NOTE: "Twilio partner" = KORE now OWNS the Twilio IoT lane (Twilio holds ~11.5% KORE). Issued per device: Jetson modem, mesh phone, telemetry pods
- **Twilio = the MESSAGING/VOICE app lane (NOT IoT)**: SMS/voice/WhatsApp via Twilio API — 727-477-3636 (system number); dispatch alerts, crew comms, provider notifications, patient follow-up texts. KORE = data connectivity · Twilio = messaging/voice — complementary, both in every unit's software stack
- **Link hierarchy**: Starlink → cellular (KORE eSIM) → mesh → BLE local. All AES-encrypted (military-grade doctrine)
- Power: inverter + battery pack; antennas roof-mounted; EMI-screened (MIL-STD-461 mindset)

## Company structure
- Legal: FL corporation (for-profit) — officers/shareholders listed on Form 631
- Fire dept MOU: Lauderhill FD (or Broward Sheriff Fire Rescue) — dispatch integration, scene access, mutual aid
- REVA partnership: NURA EMS provides ground ambulance for REVA Air's ground portion (interfacility transports) — recurring revenue

## Revenue lanes
1. MIH 911 alternative response (contracts: city/county, payers, ACOs — readmission reduction)
2. Interfacility transport (incl. REVA ground partnership)
3. Mobile stroke/cardiac outreach (grant + payer funded)
4. Medisun patient logistics (clinic-to-home, post-discharge)
