# NURA COP GLOBE — REMEDIATION LOG
Fork base: `bilawalsidhu/gods-eye-view` @ `6fb8cc3` · Worked tree: `/opt/data/cop-globe`
Date: 2026-09-11 · All figures below are from real tool output, not estimates.

---

## Baseline (before any change)

| Check | Result |
|---|---|
| `npm install` | 201 packages, clean |
| `npm test` | **2,717 pass / 0 fail / 1 skipped** |
| `npm run build` | success, 3.96 s, 157 modules |
| Node | v26.5.1 (engines allow `>=26 <27`) |

---

## R1 — Remove the NonCommercial submarine-cable dataset ✅ COMPLETE

**Why:** the bundled TeleGeography submarine-cable data is **CC BY-NC-SA 3.0 (NonCommercial)**.
Incompatible with a commercial EMS product.

The upstream `LICENSE` had already excised the ~1.1 MB data directory but left the **code still wired in**.
An approximate **1,177-line module** plus its own test suite, imported by `localLayers.js`, the overlay
allocation worker, and the voice-action map.

### What was changed
1. **Deleted** `src/data/telegeographySubmarineCables.js` and `src/data/telegeographySubmarineCables.test.mjs`.
2. **Created** `src/overlays/overlayLabelBudgets.js` — the three constants the overlay worker actually
   needed, decoupled from any dataset, renamed neutrally.
3. **`src/overlays/worldOverlayAllocation.worker.mjs`** — repointed the import; renamed the synthetic
   benchmark cohort `submarine-cables` → `reference-cohort`. **Note:** this cohort is *generated
   benchmark load* (`Cable System ${i}` labels), not the TeleGeography dataset — so the performance
   calibration is preserved untouched. This is why the removal did not disturb the allocation budget.
4. **`src/overlays/worldOverlayAllocation.test.mjs`** — repointed import + profile name.
5. **`src/data/localLayers.js`** — dropped the layer import and export.
6. **`src/data/layerState.js`** — removed the registry entry.
7. **`src/data/dataCredits.js`** — removed the credit block.
8. **`src/voice/gevActions.js`** — removed **4 dead voice command mappings** (`'submarine cables'`,
   `'cables'`, `'telegeography'`, and the `'Submarine Cable'` label). These would have been live
   voice commands referencing a layer that no longer exists.
9. **`src/data/layerState.test.mjs`** — layer-count assertion **16 → 15** (correct consequence of removal).
10. Four listing tests updated: `firstRunExperience.test.mjs`, `scenes/director.test.mjs`,
    `scenes/scenePolicy.test.mjs`, `qaL9MatrixVerdicts.test.mjs`.

### Evidence
```
grep -ri "telegeography\|submarine_cable" src/   →  (empty)
npm test                                          →  2,693 pass / 0 fail / 1 skipped
npm run build                                     →  success
```
(2,717 → 2,693 because the deleted module's own test suite went with it.)

---

## R3 — Replace OpenSky for aircraft ✅ COMPLETE (live-verified)

**Why:** OpenSky's terms restrict commercial use. Also the strategic point: owning the receiver means
**no third party can revoke our live air picture.**

### Key discovery
The fork **already contained `src/data/adsbLolFallback.js`**, which normalises adsb.lol records into the
**OpenSky state-vector shape** the existing renderer consumes. And **adsb.lol uses the same record schema
as dump1090/readsb** — they differ only in the envelope key (`ac` vs `aircraft`). So one normaliser
serves both, and **the renderer needed no changes**.

### What was changed
1. **Created `src/data/aircraftSource.js`** — single place that resolves the source:
   `NURA_ADSB_MODE = own | adsb_lol | opensky`, default **`adsb_lol`**. Unrecognised values fail safe to
   the default — **never** to OpenSky. `NURA_ADSB_OWN_URL` validated to http(s) only.
2. **`vite.config.js`** — added `aircraftSourceProxy()`, a source-agnostic middleware at `/api/aircraft`
   with 5 s caching, stale-serve on upstream failure, and single-flight coalescing. **OpenSky mode is
   refused with HTTP 409** rather than silently served.
3. **`src/data/flights.js`** — `API_URL` changed from `/api/opensky` → `AIRCRAFT_ENDPOINT` (`/api/aircraft`).
   Stale header comment updated.
4. **Three test fixtures** repointed from `/api/opensky` → `/api/aircraft`
   (`tr3bRegistry.test.mjs` ×2, `flights.test.mjs` ×1).
5. **Created `src/data/aircraftSource.test.mjs`** — 7 tests incl. the regression guard
   "an unrecognised mode fails safe to the default, never to OpenSky".

### Evidence — all three modes exercised live

**`NURA_ADSB_MODE=adsb_lol`** — real aircraft over Florida:
```
HTTP 200 · X-Flight-Source: adsb.lol · X-Flight-Count: 90
feed age: 5 seconds   (2026-09-11 04:58:48 UTC vs now 04:58:53 UTC)
33 aircraft inside the Florida bounding box
adcca6 AAL1679 27.8620,-86.1984 alt=10371m spd=235m/s
a03b91 FDX41   30.8196,-84.6141 alt=10371m spd=239m/s
abc201 GTI537  30.2464,-83.7873 alt=12192m spd=246m/s
a4380f FFT1334 28.1210,-82.7795 alt=1692m  spd=130m/s
```

**`NURA_ADSB_MODE=opensky`** — must refuse:
```
HTTP 409
{"error":"opensky_not_commercially_cleared","hint":"Set NURA_ADSB_MODE=own or adsb_lol."}
```

**`NURA_ADSB_MODE=own`** — against a mock dump1090 feed (4 aircraft, one with no callsign):
```
HTTP 200 · X-Flight-Source: own-receiver · X-Flight-Count: 4
a1b2c3 N911FL  27.9506,-82.4572 alt= 366m spd=61m/s trk=212.4 squawk=1200 cat=3
a4d5e6 LIFEGRD 27.8650,-82.5100 alt= 259m spd=49m/s trk=88.1  squawk=4401 cat=3
c0ffee MIH01   25.7617,-80.1918 alt=ground spd=0m/s  trk=0     squawk=1200 cat=0
dead01 (none)  28.1234,-81.5678 alt= 975m spd=73m/s trk=305   squawk=1200 cat=0
```
Unit conversions verified correct: 1200 ft → 366 m (×0.3048); 118 kt → 61 m/s (×0.514444);
`alt_baro:"ground"` → `on_ground: true`; category `A2` → `3`; callsign trimmed; positionless
contact retained. **The self-owned path works end to end.**

### Post-R3 suite
```
npm test        →  2,700 pass / 0 fail / 1 skipped   (2,693 + 7 new)
npm run build   →  success, 5.00 s
```

### Bug found and fixed during verification
`coalesceProxyRequest(map, key, fn)` returns **`{ promise, shared }`**, not the promise. First
implementation awaited the wrapper and crashed with `Cannot read properties of undefined (reading
'length')` → HTTP 502. Caught by the live probe, not by unit tests. Fixed to await `.promise`.

---

## REMAINING — not yet done

| Ref | Task | Status |
|---|---|---|
| **R2** | Replace Google Maps imagery/terrain | ⬜ open — deepest integration; `vite.config.js` `define` still exposes `GOOGLE_MAPS_API_KEY`; needs a commercial-terms verdict on `terrain.reearth.land` and `services.arcgisonline.com` |
| **R4** | Remove out-of-scope layers (GBFS bike-shares, TfL, radio-browser) | ⬜ open — hosts present in `src/data/bikeshare.js`, `dataCredits.js`, `radioProxy.test.mjs` |
| **R5** | Voice provider abstraction (local-first, OpenAI optional) | ⬜ open |
| **L1–L8** | The eight NURA layers (EMS units, drones, facilities, incidents, mesh, hazards, service areas) | ⬜ open — needs founder-supplied fleet/facility data |
| **—** | `/api/opensky-track` (historical track feature) still calls OpenSky | ⚠️ known remaining touchpoint — see `flights.js:3046`. adsb.lol has no equivalent history API; needs a decision (drop the feature, or source history elsewhere) |
| **—** | `traffic` layer is **simulated** data presented as a live-looking layer | ⚠️ conflicts with the "no fabricated data" rule in the prompt — needs a "SIMULATED" badge or removal |

---

## Standing caution

The upstream repo also ships `militaryRegistry.js`, `tr3bRegistry.js` and a **live CCTV layer**. The
CCTV layer in particular needs a privacy review before any NURA deployment: public camera feeds
aggregated into one view is a surveillance capability, and NURA is a healthcare/EMS company. Recommend
it stay off by default and out of scope for v1.

---

## Reproduce

```bash
cd /opt/data/cop-globe
npm install
npm test                                   # 2,700 pass / 0 fail
npm run build                              # success
NURA_ADSB_MODE=adsb_lol npx vite --port 5199 --host 127.0.0.1   # live aircraft, no keys
NURA_ADSB_MODE=own NURA_ADSB_OWN_URL=http://127.0.0.1:8081/data/aircraft.json npx vite --port 5202
NURA_ADSB_MODE=opensky npx vite --port 5200                      # 409 by design
```
