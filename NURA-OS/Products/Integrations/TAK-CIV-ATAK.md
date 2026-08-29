# Integration One-Pager — CIV-TAK / ATAK (Team Awareness Kit)

**Date:** 2026-08-19 · **Public sources only** · Feasibility verdict at bottom.

## What it is
The **Team Awareness Kit (TAK)** — US Government-owned situational-awareness software, born at AFRL. **ATAK** (Android) is the flagship client; the civil-use release **ATAK-CIV / CivTAK** is free on Google Play and **open source** (github.com/deptofdefense/AndroidTacticalAssaultKit-CIV, EAR99). Companion products from tak.gov: **iTAK** (iOS), **TAKX** (Windows C2), **WebTAK** (browser COP), **TAK Server** (data broker, encryption, federation), **Tracker** (lightweight position reporter).

## What it does out of the box (free)
Offline + online maps and high-res imagery · collaborative points/drawings/overlays (KML/GPX) · blue-force tracking / position location info (PLI) · chat + file/photo/video sharing · team **emergency beacons** · geofences with triggers · **casualty evacuation (CASEVAC/9-line) tools** · photo-to-map ("rubber sheeting") · range/bearing/viewshed/heat maps · radio control integration · first-responder icon sets. Proven in disaster response: deployed during Hurricane Harvey (2017) and Irma across multi-jurisdictional responders; DHS S&T white paper recommends TAK for public safety.

## Developer ecosystem
- **Plugin SDK** from tak.gov (free **ATAK-CIV SDK 5.5+**, requires a tak.gov account — the SDK is no longer on GitHub; Jetpack Compose support, `civDebug` build variant, Android Studio + specific Gradle versions).
- **Third-Party Pipeline:** signing for third-party plugins now open on tak.gov — plugins can load on all ATAK variants (a recent, significant change); distribution via Google Play / TAK Server mission packages.
- Community ecosystem: UAS/drone control plugins (MAVSDK/MAVLink), sensor integrations, wearable-vitals plugins (e.g., HAIL: watch heart-rate/SpO₂ → ATAK + digital CASEVAC + DD1380 auto-fill), 30+ published CIV plugins.
- **TAK Server** is free GOTS software but self-hosted and needs IT ownership; tak.gov portal itself is US-IP-restricted and .gov/.mil accounts unlock more resources.

## NURA fit — the natural home lane
- **EMS agency + disaster-response-mass-casualty lanes:** MCI field coordination, responder PLI, CASEVAC/9-line, geofenced staging, offline operation (dead-zone capable — matches the EMH offline doctrine).
- **Aero drones:** MAVSDK plugin pattern (documented in the community SDK guides) feeds drone telemetry/feeds into the same COP — Aero's air assets become TAK-tracked assets.
- **EMH at the edge:** ATAK on the provider's Android device = the field situational layer beside the EMH voice layer; a NURA **MCI-triage plugin** (START triage counts, casualty markers → Chatwoot/Twilio bridge) is the first build.
- **Meshtastic/LoRa synergy:** EMS folder already plans Meshtastic; TAK data-over-Meshtastic integrations exist in the community — a comms-degraded MCI COP.

## Risks / constraints
- Steep learning curve + battery drain (community consensus); training required for field crews.
- TAK Server = real infrastructure to stand up and secure (encryption, federation, MDM for devices).
- EAR99 + USG terms: ATO paperwork guidance applies for government use; plugins must be signed; no embargoed-country distribution.
- PHI: casualty markers/9-lines are PHI-adjacent — keep patient-identifying data in NURA lanes (encrypted), not in shared TAK servers; use unit-level data on the COP.

## Feasibility verdict
**HIGH — adopt for the EMS/disaster lane.** Free, open source, battle-and-storm-proven, with a live plugin ecosystem and a documented SDK path for a NURA MCI plugin. Plan: (1) ATAK-CIV on field devices + TAK Server self-hosted on NURA infra; (2) crew training; (3) NURA MCI-triage plugin (START counters, CASEVAC → Chatwoot bridge); (4) Aero drone telemetry via MAVSDK plugin; (5) Meshtastic comms bridge. This is the situational-awareness backbone the disaster lane was waiting for — and it costs $0 in licenses.
