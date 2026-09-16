# EMS DRONE — SENSING GAP AUDIT
Engineering review of the airborne sensing requirements against what the specified hardware can
actually deliver. Findings are graded CRITICAL / HIGH / MEDIUM / LOW.

**Verdict up front:** the spec's sensing language is written as though **one LiDAR delivers a 3D
obstacle field, 3D SLAM, scene classification and a verifiable landing zone.** The specified device
class — LD19-class 2D DToF, 12 m, one horizontal plane — delivers **a single-plane obstacle ring
inside 12 m, and nothing else.**

**No architecture change is required to fix this.** The remediation is one $25–40 downward
rangefinder per drone, one spare LD19 per dock, a documented degradation ladder, and an
LD19-accurate SITL sensor model.

---

## 1. THE THREE LAYERS — TWO ARE PROVISIONED

| Layer | Status | What it is |
|---|---|---|
| **1. Primary nav/safety** | Stated | LDROBOT **LD19** 2D DToF — 0.02–12 m, 4500 Hz ranging, 10 Hz scan, 360°, **single horizontal plane**, 0.8° angular, ±45 mm, 30 Klux, −10…+40 °C, 47 g, 0.9 W, UART 230400 one-way, 10,000 h motor life, ~$135 |
| **2. Passive optical** | Stated | EO forward/down cameras, thermal/IR, IR illuminator + spotlight, plus the compute-side depth stack (Depth-Anything-3 / `ros2-depth-anything-v3-trt`, Pointcept, CSF, patchwork, depth_clustering, pyRANSAC-3D, LEO, G2VLM) — **all permissive (Apache-2.0 / MIT / BSD)** |
| **3. Nadir range/clearance** | **MISSING** | Nothing in the plan looks below the airframe |

Mass and power are the one clean pass: **47 g and 0.9 W** against a 15 lb payload pod and an
Orin-Nano-class 7–15 W budget is **~6% of the power envelope, <1% of payload mass.**

---

## 2. THE HEADLINE FINDING

The spec assigns the LiDAR six duties. **It satisfies none of them outright.**

> SLAM mapping · obstacle field · precision landing · LiDAR-verified landing zone ·
> LiDAR + vision + thermal scene classification · LiDAR-verified descent to patient

It *partially* serves lateral clearance and short-range obstacle detection.

**The single highest-value purchase in this entire audit is one downward rangefinder per drone
(~$25–40), and it serves three separate spec functions at once:**

1. `LiDAR-verified clear landing zone → auto-land`
2. `descend toward patient (LiDAR-verified)`
3. `precision drop + winch (no free-drop of fragile/medical pods)`

All three are **nadir blind volume** — a horizontal plane physically cannot observe below the
airframe. **Do not buy three times.**

---

## 3. CRITICAL GAPS

### C1 — `LiDAR + vision + thermal classify the scene` (ARRIVAL / SCENE ASSESS)
**Two independent failures:**
- **Hover altitude.** The spec holds at `300–400 ft default` = 91–122 m. The LD19 returns nothing
  beyond **12 m — it covers 9.8–13.1% of the stated hover height.**
- **Wires.** A conductor above or below the scan plane **cannot be intersected by a horizontal plane
  at all.** Even in-plane, 0.8° beam spacing is **16.8 cm at 12 m** (2·12·tan 0.4°), so 5–10 mm
  conductors and thin branches fall between beams. Water is also not an LD19 job — specular grazing
  returns at altitude are unreliable.

**Fix (documentation cost):** classify from **EO + thermal + monocular depth at the 300–400 ft hold**
(Depth-Anything-3 relative height field; G2VLM / LEO for scene reasoning on the Orin Nano), and bring
the LD19 in only **below ~12 m AGL during final descent.** Detect water from EO texture plus low
thermal contrast, not the LiDAR. Formally map `wires` to **camera + mmWave radar**, and keep the
existing mode-select row `Hazard (wires/traffic/storm) → HOVER → RTL if escalating` as the wire rule,
so **the LiDAR is never the wire sensor.**

### C2 — `LiDAR-verified clear landing zone → auto-land` / `RTL to truck roof dock`
A single horizontal plane at landing altitude gives an **obstacle ring at the vehicle's current
height, not a clearance measurement below it.** No terrain height map, no slope estimate, no altitude
above ground. ±45 mm ranging error plus 16.8 cm beam spacing at 12 m **undersamples small obstructions
(curb, rock, limb, cable) inside the landing disc.** "LiDAR-verified clear" as written cannot be
evidenced by a nadir-blind plane, and cm-precision touchdown needs a downward range that **no sensor
in the plan provides.**

**Fix:** add **one downward-looking rangefinder per drone**, fed as a standard
`DISTANCE_SENSOR`/MAVLink altitude source on the existing PX4/ArduPilot stack, so the airframe's own
landing logic and the spec's "LiDAR-verified" language both become true. **Benewake TF-Luna ~$25
(0.2–8 m)** is sufficient for the final 8 m at spec auto-land speeds; **TFmini-S ~$40 (0.1–12 m)** if
clearance must match the LD19's own 12 m. Use the truck RTK base for dock-relative XY, as already stated.

---

## 4. HIGH GAPS

| # | Requirement | Why unmet | Cheapest fix |
|---|---|---|---|
| **H1** | `LiDAR (SLAM mapping…)` | 2D = 360° in ONE horizontal plane, 450 pts/rev. Scan-matching one plane yields 2.5D localisation, no vertically observable geometry, no Z correction. Far too sparse for the `3D maps` the RATCHET spec demands | **Zero hardware** — make the camera-depth stack the 3D mapping source; LD19 stays the planar safety layer. `ros2-depth-anything-v3-trt` → Pointcept + pyRANSAC-3D/CSF, fused with the already-stated RTK. Optional ~$135: a second LD19 rotated 90° (nadir) |
| **H2** | `sense-and-avoid (camera + radar + LiDAR)` at `50–70 mph dash` | Max range 12 m = **0.38 s reaction at 70 mph**, 0.54 s at 50. The 10 Hz sweep adds **3.1 m of blind travel per scan at 70 mph.** No 15–55 lb airframe closes a sense-and-avoid loop on 0.38 s with a 100 ms sensor period | **Re-scope by envelope, no purchase** — designate the LD19 for **terminal and low-speed only (≤12 m, ≤5 m/s)**; let the already-stated mmWave radar + EO camera carry 50–70 mph transit. Write the envelope into the SITL profiles so `Simulation-first` validates the real division of labour |
| **H3** | `descend toward patient (LiDAR-verified)` | Descent toward a target **directly beneath** the airframe is outside a horizontal plane, and the under-vehicle region is **occluded by the airframe and landing gear.** Nothing measures patient-relative pose or vertical closure | **Same single rangefinder as C2** (covers vertical closure) + the spec's own nadir EO camera with monocular depth. **One purchase covers this and C2 — do not buy twice** |
| **H4** | `small Jetson (Orin-Nano class) per drone` at `7–15 W` | The LiDAR's inability to give 3D geometry **offloads SLAM, scene classification and landing-zone reasoning onto the dense-depth network** — the most expensive model in the stack. Depth TensorRT + EO/thermal detection + point-cloud segmentation + sense-and-avoid inside 7–15 W is **not achievable at flight rate without model selection and duty-cycling.** *Exact achievable FPS on Orin Nano at 15 W is INFERRED, not measured — bench-confirm before quoting a number* | **Config only** — ViT-S-class depth at 322–518 px, FP16/INT8 TensorRT, **duty-cycled to ARRIVAL/descend at 5–10 Hz**, while the LD19 ring runs always-on at 10 Hz as the cheap safety layer. Keep the deterministic EMD/clinical path on the MCU/companion, never on the depth model |
| **H5** | `maintenance prognostics`, `predicted failures`, `sensor calibration` | The LD19 is a **spinning device with finite 10,000 h life and a one-way UART (230400, no command channel) — it cannot report its own health.** No spin-rate sanity, no temperature, no fault status. That makes it an **unmonitored single point of failure for two safety-critical functions**, with no declared failover | **Zero hardware** — companion-side driver validates each sweep (point count vs expected 450, angle monotonicity, min/max range sanity), publishes health + a MAVLink `OBSTACLE_DISTANCE`/`DISTANCE_SENSOR` stream, writes to the spec's own black box. Hard rule: **any failed or stale sweep → HOVER → RTL.** Track spin hours in the digital twin; swap at ~8,000 h (80%). Carry **one $135 spare LD19 per dock** |

---

## 5. MEDIUM GAPS

- **M1 — SITL validates the wrong sensor model.** A 2D 450-sample / 10 Hz plane plus monocular depth
  presents **completely different avoidance geometry** from the 3D LiDAR plugin a default SITL world
  assumes — and the geometry that matters (planar blind spots, beam spacing at range, absent
  below-vehicle data) is **exactly what a generic 3D plugin papers over.** Any profile already
  "validated" in simulation validated the wrong model.
  **Fix:** author a Gazebo ray sensor matching the LD19 exactly (12 m, 450 samples, 0.8°, 10 Hz,
  single plane, range/ambient masks for the 30 Klux limit) plus a camera-depth node wired to the same
  TensorRT model; re-run existing profiles; **gate flight release on those re-runs.**

- **M2 — No stated all-lighting counterpart to the all-weather case.** The spec names rain/fog/dust
  as the LiDAR killer but not the daytime one. **Clear-day sunlit scene ≈ 100,000 lux — about 3.3× the
  30 Klux rating** — so LiDAR degrades in exactly the high-ambient conditions when EO/depth are also
  degraded by glare. When the radar limb is itself rain-attenuated and optics are glare-limited, the
  plan states **no complementary sensing for the combined case.**
  **Fix:** publish a sensor-degradation ladder in the spec (**RTK + dual IMU dead-reckoning → mmWave
  proximity → HOVER → RTL**) with explicit ambient/visibility thresholds tied to the 30 Klux rating;
  add a hydrophobic/anti-glare lens cover (low single-digit dollars) to the EO/thermal apertures.

- **M3 — HazMat / weather requirements entirely unaddressed.** `CO/LEL/H2S + radiation probe` and
  `onboard weather probe (wind/temp)` are **non-optical quantities — neither the LiDAR nor the
  camera-depth stack contributes anything**, and no optical sensor measures wind. The weather probe is
  **not marked optional.** No implementation, no pod-bus allocation, no cost stated.
  **Fix:** use the **already-specified pod bus** (`BLE (payload pods, ground links)`) — one low-cost
  CO/LEL/H2S module on the pod connector (verify against an off-the-shelf 3-gas module; cost range
  INFERRED). Radiation stays genuinely optional. **Derive wind with zero hardware** from the existing
  IMU plus ESC thrust-versus-attitude estimate. Add a $10–20 temp/humidity sensor for cold-chain
  ambient and landing weather.

- **M4 — Overwatch has the sensor but no geometry.** Thermal is stated and available, so **the gap is
  not the sensor** — it is that nothing converts a thermal detection into a **located** casualty or a
  covered approach. A planar scan gives no elevation model, and 12 m reach is far inside the overwatch
  standoff. Nothing produces the elevation data that `route/cover analysis` and `landing coordinates
  for CASEVAC` imply.
  **Fix:** build cover/approach geometry from the **camera-depth point cloud, not the LiDAR** —
  depth → Pointcept/CSF ground separation → coarse elevation + obstacle map to the truck console and
  the TAK pin, refreshed **only in stable hover.** Zero hardware. Where standoff exceeds useful
  monocular-depth range, **mark the map relative, not survey-grade** — do not claim 3D mapping accuracy.

- **M5 — Winch/drop cannot be enforced by sensing as planned.** The winch sits in the same **nadir
  blind volume**, and **nothing in the sensor list measures tether payout or ground contact**, so
  "no free-drop" is not enforceable. Monocular depth alone cannot resolve the centimetre-scale
  clearance needed at pod release, and carries scale ambiguity without an absolute reference.
  **Fix:** the **same rangefinder as C2** supplies ground clearance, plus winch encoder/tension
  feedback on the pod bus (mechanical, low-cost). Use RTK/IMU for absolute scale.

---

## 6. LOW GAP

- **L1 — rPPG claim is not currently satisfiable.** The RATCHET spec cites
  `camera-based photoplethysmography pulse estimation (where conditions permit)`. **Measurement
  conditions are not specified, and rPPG is incompatible with the platform as described** — a
  10 Hz-planar-LiDAR + moving-airframe camera stack has **no stated frame rate, gimbal or
  stabilisation requirement**, against a `50–70 mph dash` motion envelope and `10–15 min loiter`. The
  parenthetical "where conditions permit" means **this is not a satisfied requirement**, and the plan
  does not state what would satisfy it.
  **Fix — scope discipline first:** reroute the claim to **"visual casualty detection plus
  movement/breathing motion analysis"** from the existing EO/thermal (LEO / G2VLM on the Orin Nano),
  computed **only in stable hover**, processed on the truck console. **Delete or explicitly gate the
  rPPG claim.** If retained, add a hover-stabilised gimbal and a stated minimum frame rate as **hard
  requirements** — that is the only path to making the existing sentence true.

---

## 7. REMEDIATION SUMMARY — WHAT TO ACTUALLY BUY

| Item | Cost | Serves |
|---|---|---|
| **Downward rangefinder** (TF-Luna ~$25 / TFmini-S ~$40) **×1 per drone** | ~$25–40 | **C2 landing · H3 descent-to-patient · M5 winch clearance — three spec functions** |
| **Spare LD19 per dock** | ~$135 | H5 fault tolerance |
| Hydrophobic/anti-glare lens covers | single-digit $ | M2 |
| Temp/humidity sensor on pod bus | $10–20 | M3 cold-chain / landing weather |
| CO/LEL/H2S module on pod bus | INFERRED | M3 HazMat |
| Second LD19 rotated 90° *(optional)* | ~$135 | H1 crossing plane |

**Everything else is configuration or documentation** — depth-model duty-cycling, the degradation
ladder, the SITL sensor model, the companion-side health validator, the wire-rule re-mapping, and the
rPPG scope correction.

**Total new hardware per drone: ~$25–40.** That is the entire cost of making the spec's
"LiDAR-verified" language true.

---

## 8. VERIFICATION STATUS

- Sensor specifications and licences verified against vendor/repo sources.
- **Monocular-depth FPS on Orin Nano at 15 W is INFERRED, not measured — bench-confirm before
  quoting.** Do not treat any single number here as validated.
- Mounting geometry for the LD19 (occlusion of the under-vehicle volume) is **INFERRED** from a 360°
  horizontal disc; confirm against the actual airframe.
- 3-gas module cost is **INFERRED** — verify against an off-the-shelf part.
