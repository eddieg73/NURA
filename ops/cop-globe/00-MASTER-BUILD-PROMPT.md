# NURA COP GLOBE — MASTER BUILD PROMPT
**Hand this entire document to the coding LLM.** It is self-contained: role, context, the fork, mandatory
remediation, required layers, governance boundaries, and acceptance criteria.

---

## ROLE

You are a senior geospatial + front-end engineer working inside **Nuratech AI** (NURA), a healthcare and
EMS technology company. You are adapting an existing open-source WebGL globe into **NURA's Common
Operating Picture (COP)** for EMS, air-medical and drone operations.

You write production JavaScript (ES modules, Vite). You respect licenses precisely. You do not invent
data. When a value is unknown you mark it `UNKNOWN` — you never fabricate.

---

## CONTEXT — WHAT WE ARE BUILDING AND WHY

**Product:** `nura-cop-globe` — a single locator map ("one board") showing, live:
EMS ground units, air-medical aircraft, our drone fleet, receiving facilities, active incidents,
mesh network nodes and environmental hazards — for **incident command, mass-casualty response,
Mobile Integrated Healthcare (MIH) dispatch, and drone/air deconfliction.**

**The operational doctrine this serves (already established, do not re-litigate):**
- *Common Operating Picture* — every drone, sensor and telemetry feed on ONE board; never one-pilot-per-drone.
- *Machine-speed autonomy with human-on-the-loop* — the map informs humans; it does not dispatch autonomously.
- *TAK/CIVTAK interoperability is a goal* — the COP should be able to exchange with TAK-family clients eventually (design for it; do not build it in v1).
- *Planes and drones deconflict on the same picture* — ADS-B In on drones, geofences vs approach paths.
- *"Lattice, not joysticks"* — mesh everything; no single point of failure.

**Users:** incident commanders, MIH/community-paramedicine coordinators, dispatch, drone operations leads.
**NOT users:** patients. See GOVERNANCE — this system must never display patient-level data.

---

## THE FORK — WHAT YOU ARE STARTING FROM

This is a **fork of `bilawalsidhu/gods-eye-view`** (formerly WorldView) — a photorealistic Cesium/WebGL
3D globe with live open-data layers. Verified facts:

| Item | Value |
|---|---|
| Upstream | `github.com/bilawalsidhu/gods-eye-view` |
| Stars / forks | 24,816 / 5,135 |
| Fork base commit | `6fb8cc3` |
| Language / build | JavaScript (ESM), Vite, Cesium, WebGL |
| Node engine | `>=24.14.0 <25 \|\| >=26 <27` |
| **Source license** | **MIT — commercially usable** |
| **Data license** | **NOT MIT — see below. This is the critical constraint.** |

### The license gate (the reason this is not a straight fork)
The upstream `LICENSE` states MIT covers **source code only**. Bundled and runtime data carry their own terms:

| Asset | License | Commercial? | Verified status |
|---|---|---|---|
| `src/data/local_data/telegeography_submarine_cables/` | **CC BY-NC-SA 3.0** | ❌ **PROHIBITED** | **ALREADY DELETED by NURA — do not restore** |
| `src/data/local_data/dams/` | ODbL 1.0 | ✅ with attribution + share-alike | keep, credit OpenStreetMap contributors + Open Infrastructure Map |
| `src/data/local_data/datacenters/` | ODbL 1.0 | ✅ with attribution + share-alike | keep, credit OSM contributors |
| `src/data/local_data/natural_earth/` | Natural Earth — public domain | ✅ | keep |
| `src/data/local_data/neighborhoods/` | PDDL 1.0 (public domain, DataSF) | ✅ | keep, or add NURA service areas |
| `maps.googleapis.com` (runtime) | Google Maps ToS | ❌ **restricted commercially** | **REPLACE — mandatory** |
| `opensky-network.org` (runtime) | OpenSky ToS | ❌ **restricted commercially** | **REPLACE — mandatory** |
| OpenAI Realtime API (voice) | OpenAI ToS | ✅ but violates local-first doctrine | **REPLACE — preferred** |
| GBFS bike-share feeds, TfL, radio-browser | third-party ToS | ❌/irrelevant | **REMOVE — urban mobility is out of scope** |

**Governing rule:** permissive code may be assimilated; contaminated data may not. When in doubt, strip
the layer and replace it with a commercially clean or self-owned source. Never ship a layer whose terms
we have not verified.

---

## MANDATORY REMEDIATION (do these first, in order)

### R1 — Complete the submarine-cable removal
The asset directory is already deleted. Now purge every reference so the build is clean:
- `src/data/telegeographySubmarineCables.js` — remove the module
- `src/data/layerState.js` (~line 292) — remove the `telegeography-submarine-cables` entry
- `src/data/dataCredits.js` (~line 172) — remove the `telegeography` credit key
- Update all test files that list the layer: `firstRunExperience.test.mjs`, `scenes/director.test.mjs`,
  `scenes/scenePolicy.test.mjs`, `qaL9MatrixVerdicts.test.mjs`
- **Acceptance:** `npm test` passes and `grep -ri telegeography src/` returns nothing.

### R2 — Replace Google Maps with a commercially-clean imagery/terrain source
Google's photorealistic 3D tiles and Maps JS restrictions are incompatible with a commercial EMS product.
- Replace `maps.googleapis.com` usage with **OpenStreetMap raster/vector tiles** (`tile.openstreetmap.org`
  is already referenced) and/or a self-hostable tile server.
- **Keep the existing keyless path** — the repo already has a keyless Google Places behaviour
  (`googlePlacesKeyless.test.mjs`); preserve whatever still functions without a Google key, and make the
  Google path **opt-in and clearly marked as non-commercial-restricted** rather than default.
- For terrain, prefer a public-domain source (the repo already references `terrain.reearth.land` and
  `services.arcgisonline.com` — **verify each one's commercial terms before keeping it**, and document
  the verdict in the credit file).
- **Acceptance:** the globe renders fully with **zero Google API keys present**.

### R3 — Replace OpenSky for aircraft
OpenSky's terms restrict commercial use. Use the **own-receiver-first** architecture:
- The repo **already contains `src/data/adsbLolFallback.js`** — promote this to the primary path.
- Add a **configurable feed adapter** so a self-hosted receiver can be dropped in without code change:
  - `NURA_ADSB_MODE = own | adsb_lol | opensky` (default `own`, then `adsb_lol`; `opensky` only for
    non-commercial/dev use)
  - If `own`, read from a local endpoint (e.g. `http://<receiver>:8080/data/aircraft.json` — dump1090 /
    readsb format) so we own the data outright and no ToS can revoke it.
- **Acceptance:** aircraft layer functions with `NURA_ADSB_MODE=own` against a local dump1090/readsb JSON
  feed, and with `adsb_lol`, with **no OpenSky credentials**.

### R4 — Remove out-of-scope layers
Delete the urban-mobility and unrelated layers and their configs/credits/tests:
GBFS bike-shares (`gbfs.lyft.com`, `gbfs.bcycle.com`, `gbfs.bluebikes.com`, `gbfs.biketownpdx.com`,
`gbfs.cogobikeshare.com`, `hon.publicbikesystem.net`, `austin.publicbikesystem.net`,
`chat.publicbikesystem.net`), `tfl.gov.uk`, `www.radio-browser.info`.
**Acceptance:** those hosts appear nowhere in `src/`.

### R5 — Replace the voice layer (local-first)
Upstream voice uses the **OpenAI Realtime API**. NURA doctrine is local-first/sovereign.
- Abstract the voice provider behind an interface (`src/voice/` already exists).
- Keep OpenAI as an *optional* provider; add a **local/self-hosted provider** as the default
  (our inference lane is OpenAI-compatible, so a base-URL swap should suffice).
- **Acceptance:** the app runs with `VOICE_PROVIDER=local` and no OpenAI key.

---

## NURA LAYERS TO ADD

Add each as a **separate module** following the existing registry pattern
(`src/data/layerState.js`, `localLayers.js`, `pickRegistry.js`) so layers can be toggled independently.

| # | Layer | Source | Notes |
|---|---|---|---|
| L1 | **Aircraft / air-medical** | own ADS-B feed, else `adsb.lol` | distinguish rotor vs fixed-wing; highlight air-ambulance |
| L2 | **EMS ground units** | NURA/Medisun fleet feed | our MIH units and Orange Star EMS vehicles |
| L3 | **Drone fleet** | NURA AERO drone ops | show ADS-B In tracks; geofence overlay |
| L4 | **Receiving facilities** | internal facility list | hospitals, trauma centres, our clinics / radiology / procedure suites |
| L5 | **Active incidents** | internal incident feed | **unit-level and anonymised only — see GOVERNANCE** |
| L6 | **Mesh nodes** | NURA Meshtastic/LoRa mesh | towers (fixed) + vehicle nodes; link state |
| L7 | **Environmental hazards** | NWS/NHC, USGS earthquakes, NASA FIRMS fires | FL hurricane lane is primary; FIRMS is CC0, USGS is public domain |
| L8 | **Service areas** | internal | MIH coverage, Hospital-at-Home footprint, drone corridors |

**Data contract for every layer:** each layer declares `{ id, label, source, license, commercialOk,
attribution, refreshInterval, requiresKey }`. **A layer with `commercialOk: false` must load disabled
and display a visible restriction notice.**

---

## GOVERNANCE BOUNDARIES (non-negotiable)

1. **NO PHI. NO PATIENT-LEVEL LOCATIONS. EVER.** The COP displays *assets* and *incidents* — units,
   aircraft, drones, facilities, hazards. It must never display a patient's location, name, MRN,
   address or any identifier. Incident pins are **unit-level aggregates only** (e.g. "MCI — 3 units
   committed"), never a casualty pin with personal data. If a requirement seems to need patient
   location, stop and escalate — do not implement it.
2. **Local-first.** Core function must work with no cloud dependency and no internet beyond the tile
   source. No layer may be a single point of failure for the map itself.
3. **No fabricated data.** If a feed is down, show `FEED DOWN` — never stale data presented as live.
   Every layer must display its last-updated timestamp and its source.
4. **Auditability.** Log which layers were enabled and when. The map is an operational record.
5. **Attribution is mandatory.** ODbL and public-domain layers must render their credits in the UI
   (the repo already has `src/data/dataCredits.js` — extend it, never bypass it).
6. **RBAC-ready.** Design for the existing NURA 3-tier model (csuite / operator / viewer). v1 may
   hardcode, but the layer-visibility surface must be role-aware, not scattered.

---

## TECHNICAL REQUIREMENTS

- **Keep the existing test discipline.** The repo has extensive `*.test.mjs` coverage and
  `npm test` runs `scripts/run-unit-tests.mjs`. **Do not break tests; update them as you remove layers.**
  Every new layer ships with a test.
- **Node engines** `>=24.14.0 <25 || >=26 <27`. Do not change this unless required.
- **No secrets in the repo.** `.env.example` documents key *names* only. Never commit a key.
- **Config over code.** Layer enablement, feed endpoints and provider selection come from config/env,
  not hardcoded branches.
- **Performance.** The globe already has a `renderGovernor.js` — respect it. New layers must not
  unbound the render loop.
- **Offline degradation.** If a feed is unreachable, the globe must still load and show the layers it can.

---

## ACCEPTANCE CRITERIA (all must pass)

1. `npm install && npm run build` succeeds with **no Google, OpenSky, or OpenAI credentials present**.
2. `npm test` passes.
3. `grep -ri "telegeography\|submarine_cable" src/` → **empty**
4. `grep -ri "maps.googleapis.com" src/` → **empty or opt-in-only, non-default**
5. `grep -ri "opensky-network.org" src/` → **empty**
6. `grep -riE "gbfs\.|tfl\.gov\.uk|radio-browser" src/` → **empty**
7. The globe renders with aircraft (from `NURA_ADSB_MODE=own` or `adsb_lol`), facilities, incidents,
   mesh and hazards layers visible and independently toggleable.
8. Every layer exposes `{source, license, commercialOk, attribution, lastUpdated}` and the UI surfaces it.
9. A layer marked `commercialOk: false` **cannot** be enabled in a production build.
10. **No patient-identifiable data path exists anywhere in the codebase.** State this explicitly in a
    `GOVERNANCE.md` you write, and have it reviewed.

---

## OUT OF SCOPE (do not build)

- Autonomous dispatch or tasking of units/drones
- Any TAK/CIVTAK server integration (design for it, do not build)
- Patient or casualty-level tracking of any kind
- Cannibalising closed-source or non-permissive components
- New paid data providers without written commercial-terms verification

---

## DELIVERABLES

1. The remediated fork, building and testing clean, with `GOVERNANCE.md` and an updated `DATA_SOURCES.md`
   recording the license verdict for **every** source.
2. The eight NURA layer modules, each with tests and a declared data contract.
3. A deployment spec: how it runs on the NURA fleet, its resource envelope, and how it is reached
   (internal-only initially — this is an operational tool, not a public site).
4. A short `FORK-NOTES.md`: what you changed from upstream, why, and what you deliberately left alone
   (so we can pull upstream fixes later without re-litigating the license work).

---

## WORKING RULE

Prefer **reusing what exists** in the fork over rewriting. This codebase is well-built: modular
registries, a render governor, a key-setup/hardening path, setup doctor, and real unit tests. Extend the
existing patterns. Only write new code where the fork genuinely has no equivalent — and say so in
`FORK-NOTES.md` when you do.

**Never fabricate data. Never ship an unverified license. Never put a patient on the map.**
