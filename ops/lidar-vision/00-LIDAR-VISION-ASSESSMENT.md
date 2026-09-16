# NURA — LiDAR VISION: GITHUB ASSESSMENT
Searched 2026-09-12. All star counts, licenses and dates verified live via the GitHub API
(scripts: `lidar_github_scan.py`, `lidar_vlm_scan.py`, `lidar_named_scan.py`).

---

## WHY THIS IS ALREADY A NURA REQUIREMENT

The drone specs already mandate LiDAR — this isn't new scope, it's an unmet line item:

> **`NURA-OS/Aero/EMS-Drone-Spec.md`**
> *"SENSOR SUITE: NAVIGATION: **LiDAR** (SLAM mapping, obstacle field, precision landing)"*
> *"ARRIVAL / SCENE ASSESS — LiDAR + vision + thermal classify the scene … landing
> zone clear/obstructed/water?"*
> *"SAFE LANDING PROTOCOL — **LiDAR-verified** clear landing zone → auto-land"*
> *"TRANSIT — RTK + **LiDAR SLAM** + geofenced corridor + ADS-B deconfliction"*

> **`NURA-OS/Products/RATCHET-Drone-Fleet-Spec.md`** — Scout Drone sensors:
> *"4K optical · thermal · **LiDAR** · night vision · gas · radiation · atmospheric"*

**The hardware constraint that decides everything:** *"small Jetson (Orin-Nano class) per drone —
onboard AI … 7-15W"* with **LOCAL-AI doctrine** (zero cloud dependency for clinical function).
So onboard perception must fit **7–15 W** and work **offline**.

---

## THE ARCHITECTURE THIS IMPLIES (two layers, not one)

"Give you vision using LiDAR" cannot be one model. Safety and semantics have different budgets:

**LAYER 1 — deterministic, onboard, real-time (SAFETY-CRITICAL)**
LiDAR → ground plane → obstacle field → landing-zone clearance. Geometry/classical ML, not an LLM.
Must run on Orin-Nano. This is what the spec means by "LiDAR-verified landing zone".

**LAYER 2 — semantic, LLM-facing (the "vision" Hermes consumes)**
Point cloud → structured spatial description → text. This is what makes it *vision* rather than a
proximity sensor. Runs where there's headroom, or offboard pre/post-mission.

---

## LAYER 1 CANDIDATES — permissive, actively maintained

| Repo | ★ | License | Last push | Fit |
|---|---|---|---|---|
| **`Pointcept/Pointcept`** | 3,215 | **MIT** ✅ | **2026-09-11** | Modern point-cloud perception codebase (semantic/instance segmentation). **Best maintained, cleanest license.** |
| `jianboqi/CSF` | 647 | **Apache-2.0** ✅ | **2026-09-11** | Cloth-simulation ground filtering / bare-earth extraction → **landing-zone ground detection**. Actively maintained. |
| `LimHyungTae/patchwork` | 590 | **MIT** ✅ | 2026-05-21 | SOTA fast robust ground segmentation (RA-L'21). Published, proven, MIT. |
| `lorenwel/linefit_ground_segmentation` | 811 | BSD-3 ✅ | 2024-07-26 | Ground segmentation, ROS-native. Proven, but less recently touched. |
| `PRBonn/depth_clustering` | 1,313 | MIT ✅ | **2021-11-11** | Fast point-cloud clustering for obstacle detection. ⚠️ **Stale 5 years** — reference only. |
| `leomariga/pyRANSAC-3D` | 666 | Apache-2.0 ✅ | 2026-08-28 | Plane/sphere/cylinder fitting on point clouds. Useful for runway/LZ plane fits. |
| `autowarefoundation/autoware` | 12,057 | Apache-2.0 ✅ | 2026-09-09 | Full autonomous-driving stack — proven perception, but **far heavier than a drone needs**. Harvest modules, don't adopt the stack. |

## LAYER 2 CANDIDATES — the "LLM sees the scene" part

Licenses below are **read from the actual LICENSE file**, not from the GitHub API's summary
(which reports `NOASSERTION` for anything non-SPDX and would have misled us).

| Repo | ★ | License (verified) | Verdict |
|---|---|---|---|
| **`ByteDance-Seed/Depth-Anything-3`** | 6,329 | **Apache-2.0** ✅ *confirmed* | Monocular **metric depth → point cloud from a plain camera**. Fully clear. |
| **`ika-rwth-aachen/ros2-depth-anything-v3-trt`** | 556 | **Apache-2.0** ✅ | **ROS2 + TensorRT node** producing point clouds from camera images. Pushed 2026-08-21. **Turnkey for a Jetson.** |
| **`embodied-generalist/embodied-generalist`** (LEO) | 489 | **MIT** ✅ *confirmed* | Embodied generalist agent in 3D world (ICML 2024). Clean, directly on-theme. |
| **`manycore-research/SpatialLM`** | 4,733 | **Llama 3.2 Community License** ⚠️ | Closest to the ask — LLM does structured 3D modelling from point clouds (NeurIPS 2025). **Meta proprietary, NOT open source.** See gate below. |
| `facebookresearch/vggt` | 14,377 | **VGGT License v1 — Meta "Research Materials"** ⚠️ | CVPR'25 Best Paper. Carries an Acceptable Use Policy and is framed as *Research Materials*. **Not a standard OSS licence — counsel first.** |
| `OpenRobotLab/PointLLM` | 1,054 | **NO LICENSE FILE** ❌ | **All rights reserved by default.** Legally unusable. Do not build on it. |
| `naver/mast3r` | 3,101 | Non-commercial research ⚠️ | **Blocked for product use.** |
| `isl-org/Open3D` | 13,955 | NOASSERTION ⚠️ | Reports NOASSERTION (LICENSE-file format); MIT in practice — confirm before shipping. |

### ⚠️ The licence distinction that matters most

`NOASSERTION` from the GitHub API does **not** mean "unknown" — it means **not a recognised SPDX
open-source licence**. Reading the files showed two very different cases hiding behind that one label:

- **SpatialLM → Llama 3.2 Community License.** This is *usable* commercially — NURA is far under the
  700M-MAU threshold — but it is **not open source**. It carries an acceptable-use policy, a
  "Built with Llama" attribution duty, and requires derivatives to be redistributed under the same
  terms. **Permissible, conditional, and it must be a deliberate decision — not an accident.**
- **VGGT → Meta "Research Materials" licence.** Framed as research with an acceptable-use policy.
  **Not cleared for a commercial clinical product** without counsel.

Neither is "free code". Both were one API field away from being treated as such.

---

## THE COST LEVER WORTH SERIOUS CONSIDERATION

**`ros2-depth-anything-v3-trt` + Depth Anything 3** gives **metric depth and point clouds from a
camera**, on ROS2, TensorRT-accelerated, Apache-2.0.

Why that matters concretely:
- A real LiDAR on a 15–55 lb drone costs **mass, power and money**. A camera costs almost none.
- The spec already carries **EO cameras** ("EO forward/down") for Layer-2 scene assessment.
- So: **cameras give the dense point cloud; LiDAR (where fitted) gives the metrically-trusted
  safety layer.** They are complementary, and the cheap one already exists on the airframe.

This is the single highest-leverage finding. It lets the Scout/EMS tiers field *3D spatial vision*
before any LiDAR unit is bought — and it validates the pipeline in SITL/Gazebo first, which the
doctrine already requires (*"Sim-validated first (SITL/Gazebo)"*).

---

## LICENCE GATE — the thing that decides what we may ship

Applying our own rule (permissive code may be assimilated; contaminated code may not):

- **Safe to build on:** Pointcept (MIT) · CSF (Apache-2.0) · patchwork (MIT) · Depth Anything 3
  (Apache-2.0) · ros2-depth-anything-v3-trt (Apache-2.0) · LEO (MIT) · pyRANSAC-3D (Apache-2.0)
- **Blocked pending counsel:** SpatialLM (NOASSERTION) · VGGT (NOASSERTION) · MASt3R (non-commercial)
- **Cannot use at all:** PointLLM (no licence)

⚠️ **SpatialLM is the most tempting and the most restricted.** It does exactly what "give you
vision using LiDAR" describes — but NOASSERTION means we do not know our rights. It is a
**reference architecture to study**, not a dependency, until counsel clears it.

---

## RECOMMENDED PATH (sim-first, per doctrine)

1. **Spike on the sim** — SITL/Gazebo + a synthetic LiDAR, no hardware spend. Prove the pipeline
   end-to-end before anything flies.
2. **Layer 1**: `patchwork` or `CSF` for ground/LZ segmentation (both welcome MIT/Apache, both
   actively maintained).
3. **Layer 2 (cheap)**: `ros2-depth-anything-v3-trt` — camera → point cloud → semantic summary.
   Apache-2.0, TensorRT, built for exactly this.
4. **Layer 2 (rich)**: study SpatialLM's *architecture in the open*; implement the concept on a
   permissive base rather than depending on its weights.
5. **Read-only first.** Nothing onboard actuates. Human-on-the-loop and the failsafe ladder always
   outrank autonomy — the spec is explicit, and it stays that way.

---

## OPEN QUESTIONS FOR THE FOUNDER

1. **Which tier first** — SMALL (<55 lb, Orin-Nano 7–15 W) or LARGE? The compute budget changes
   what is even possible.
2. **Is a physical LiDAR unit budgeted**, or do we lead with camera-derived depth and add LiDAR
   later?
3. **Do you want the SITL/Gazebo spike built** so there is a working pipeline before hardware?
