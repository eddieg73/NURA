# LD19 — SENSOR ASSESSMENT
LDROBOT LD19 (DToF 2D LiDAR). Specs verified against the manufacturer datasheet
(`LDROBOT_LD19_Datasheet_EN_v2.6`) and distributor listings, 2026-09-12.

---

## VERDICT UP FRONT

**The right *development* sensor. The wrong *flight* sensor.**

Buy it to de-risk the pipeline for ~$135. **Do not fly it as the safety-critical sensor.**

---

## VERIFIED SPECIFICATIONS

| Parameter | Value |
|---|---|
| Technology | **DToF** (direct time-of-flight), 905 nm infrared |
| Ranging | **0.02 – 12 m** (70 % reflectivity target) |
| Ranging frequency | 4,500 Hz |
| Scan frequency | 10 Hz typical (5–13 Hz via PWM) |
| Accuracy | ±45 mm average; 10 mm std deviation; 15 mm resolution |
| Field of view | **360°** |
| Angular resolution | 0.8° @ 10 Hz; angle error ±2° |
| **Ambient light** | **30 Klux** — works outdoors (LD06 does not) |
| **Weight** | **47 g** (without cable) |
| Dimensions | 38.59 × 38.89 × 33.50 mm |
| **Power** | 5 V, 180 mA → **0.9 W** |
| Interface | UART **230400** baud, 3.3 V, **one-way** (streams on rotation; no commands) |
| Connector | ZH1.5T-4P 1.5 mm |
| Motor | Brushless, PWM speed control (or internal 10 Hz) |
| **Operating temp** | **−10 °C to +40 °C** |
| Motor life | 10,000 h |
| Price | ~$135 USD / ~$210 AUD (distributor); cheaper direct |

---

## WHY IT FITS THE BENCH — this is the interesting part

**0.9 W.** The drone spec's compute budget is *"Orin-Nano class, 7–15 W."* The LD19 consumes
**6–13 % of that**. It is genuinely drone-light at **47 g**. On power and mass this sensor is
not the problem.

**30 Klux ambient resistance** means it works **outdoors** — the LD06 explicitly cannot, and that
distinction matters for a Florida EMS programme where the bench work happens outside.

**Permissive software, current stack:**

| Repo | ★ | License | Notes |
|---|---|---|---|
| `Myzhar/ldrobot-lidar-ros2` | 104 | **Apache-2.0** ✅ | Nav2 **Lifecycle** node, ROS 2 **Humble + Jazzy**, publishes `sensor_msgs/LaserScan` on `/ldlidar_node/scan`. Actively maintained (2026-06-11). |
| `TheNoobInventor/lidarbot` | 230 | **BSD-3-Clause** ✅ | **Complete working reference build**: differential-drive robot, ROS 2 **Jazzy** on Raspberry Pi 4. Pushed **2026-09-08**. Copy the pattern. |
| `ldrobotSensorTeam/ldlidar_stl_ros2` | 90 | **MIT** ✅ | Official LDROBOT package — but **stale (2024-02)** and pinned to ROS 2 Foxy. |
| `Myzhar/MyzharBot` | 0 | Apache-2.0 ✅ | Same author's ground robot. |

**Measured performance** (upstream benchmark): ~9.94 fps, **end-to-end latency < 1 ms**, **0 missed
frames**. That is real-time capable.

**The chain it plugs into already exists in our own spec:** PX4/ArduPilot + MAVLink +
mavlink-router on the truck Jetson + **Gazebo/SITL (simulate every mission profile before flight)**.

So the play is clean: **LD19 → ROS 2 Jazzy → `LaserScan` → Layer-1 ground/LZ segmentation → validated
in SITL/Gazebo → real hardware.** For ~$135 and a weekend, Layer 1 stops being theoretical.

---

## WHY IT MUST NOT FLY AS THE SAFETY SENSOR

Five disqualifiers, in order of severity:

1. **It is 2D — one horizontal plane.** It sees a *slice*, not a volume. Our own spec names the
   hazard this cannot handle: *"hazards (**wires**, traffic)"*. A 2D scanner catches a wire **only
   if the wire lies exactly in the scan plane**. At 360° × 0.8° in a single plane, that is luck,
   not detection. This alone disqualifies it for obstacle avoidance on an aircraft.
2. **12 m range is far too short.** The spec calls for a 50–70 mph dash. 12 m at 60 mph is
   **~0.45 seconds of reaction time** — below any usable detect-and-avoid margin.
3. **−10 °C to +40 °C.** Fails Florida summer tarmac, and carries no aviation environmental
   qualification. No DO-160.
4. **Not certified, no redundancy.** No DO-160, no TSO, single-channel. It cannot be a
   safety-critical component on a certified aircraft.
5. **10,000 h motor life** on a continuously spinning brushless motor — a consumable, not a
   flight-critical part.

The spec says *"sense-and-avoid (camera + radar + LiDAR — Amazon-model)"*. Amazon's model uses
**long-range, volumetric** sensing. LD19 is not that, and it should not be pretended to be.

---

## RECOMMENDED USE

**DO — buy one (~$135) and use it for:**
- Standing up the **ROS 2 Jazzy → `LaserScan` → segmentation** pipeline with **real data instead
  of synthetic** — de-risks Layer 1 before any airframe exists
- **Landing-zone / ground-plane detection** prototypes — exactly what "LiDAR-verified clear landing
  zone" requires, at bench scale
- **Indoor SLAM** prototyping and the obstacle-field algorithm (extrude the scan into a costmap)
- Copying `lidarbot` (BSD-3) as the reference integration — it is a working ROS 2 Jazzy build

**DO NOT —**
- Mount it as the drone's sense-and-avoid sensor
- Represent it as satisfying the spec's LiDAR requirement for flight
- Assume 2D ground-plane avoidance generalises to 3D airspace

**Production flight sensor needs:** volumetric (3D), long-range, wider temperature envelope,
and an aviation qualification path. That is a different price bracket and a different decision —
and it is exactly why the **camera-derived-depth lever** (`ros2-depth-anything-v3-trt`, Apache-2.0)
matters: it gives dense 3D from hardware the airframe already carries.

---

## LICENCE GATE

All four LD19 software stacks are **permissive — nothing blocks us.** ✅
Contrast with the Layer-2 findings: SpatialLM (Llama 3.2 Community), VGGT (Meta Research
Materials), PointLLM (no licence). **The sensor ecosystem is the clean part of this stack.**
