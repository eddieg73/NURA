#!/usr/bin/env python3
"""Create the actionable drone-sensing tasks + the Paperclip disposition task on the board."""
import json
import sys
import time

import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

H = headers()
BASE = "https://api.notion.com/v1"
ids = json.load(open("/opt/data/workforce_ids.json"))
TASKS, REG = ids["tasks_db"], ids["registry_db"]

# resolve agent page ids so Assignee can be a relation later if needed
rows, cur = [], None
while True:
    b = {"page_size": 100}
    if cur:
        b["start_cursor"] = cur
    r = requests.post(f"{BASE}/databases/{REG}/query", headers=H, json=b, timeout=60)
    d = r.json()
    rows += d.get("results", [])
    if not d.get("has_more"):
        break
    cur = d.get("next_cursor")
print(f"registry rows: {len(rows)}")

T = [
    # (identifier, title, assignee, priority, status, founder_gate, description)
    ("DRN-001", "DECISION: add one downward rangefinder per drone (~$25-40)",
     "Orion", "P0 Critical", "Backlog", True,
     "SENSING AUDIT C2/H3/M5. The spec says 'LiDAR-verified clear landing zone' and "
     "'descend toward patient (LiDAR-verified)', but a 2D horizontal LD19 plane physically cannot "
     "observe BELOW the airframe. It gives an obstacle ring at current height, not clearance beneath. "
     "No downward range exists anywhere in the plan, so cm-precision touchdown is unevidenced.\n\n"
     "ONE PURCHASE COVERS THREE SPEC FUNCTIONS: (1) landing, (2) descent-to-patient, (3) winch/pod "
     "ground clearance. Do not buy three times.\n\n"
     "Benewake TF-Luna ~$25 (0.2-8 m) is sufficient for the final 8 m at spec auto-land speeds; "
     "TFmini-S ~$40 (0.1-12 m) if clearance must match the LD19's own 12 m. Feed as a standard "
     "MAVLink DISTANCE_SENSOR altitude source on the existing PX4/ArduPilot stack so the airframe's "
     "own landing logic and the spec language both become true.\n\n"
     "Cost per drone: ~$25-40. This is the entire cost of making 'LiDAR-verified' true."),

    ("DRN-002", "Re-map 'wire' hazard detection OFF the LiDAR (documentation only)",
     "Orion", "P0 Critical", "Blocked", True,
     "SENSING AUDIT C1. A conductor above or below the scan plane CANNOT be intersected by a "
     "horizontal plane at all. Even in-plane, 0.8 deg beam spacing is 16.8 cm at 12 m "
     "(2*12*tan 0.4 deg), so 5-10 mm conductors and thin branches fall between beams.\n\n"
     "Also: the spec hovers at 300-400 ft = 91-122 m, but the LD19 returns nothing beyond 12 m -- it "
     "covers 9.8-13.1% of the stated hover height. Scene classification at altitude cannot be a LiDAR "
     "job.\n\n"
     "FIX (doc cost only): classify from EO + thermal + monocular depth at the 300-400 ft hold; bring "
     "the LD19 in only below ~12 m AGL during final descent. Formally map wires to camera + mmWave "
     "radar and keep the existing mode-select row as the wire rule, so the LiDAR is NEVER the wire "
     "sensor. Detect water from EO texture plus low thermal contrast, not the LiDAR.\n\n"
     "Blocked on: spec revision sign-off."),

    ("DRN-003", "Re-scope LD19 to terminal/low-speed envelope (SITL profiles)",
     "Orion", "P1 High", "Backlog", False,
     "SENSING AUDIT H2. Max range 12 m = 0.38 s reaction at 70 mph, 0.54 s at 50 mph. The 10 Hz sweep "
     "adds 3.1 m of blind travel per scan at 70 mph. No 15-55 lb airframe closes a sense-and-avoid "
     "loop on 0.38 s with a 100 ms sensor period.\n\n"
     "FIX (no purchase): designate the LD19 for terminal and low-speed phases only (<=12 m, <=5 m/s); "
     "let the already-stated mmWave radar + EO camera carry 50-70 mph transit avoidance. Write the "
     "envelope into the SITL mission profiles so 'Simulation-first' validates the real division of "
     "labour instead of an assumed 3D LiDAR.\n\n"
     "Acceptance: mission profiles encode the speed/range envelope and pass against the LD19-accurate "
     "sensor model (see DRN-006)."),

    ("DRN-004", "LD19 health validator + one spare per dock",
     "Sentinel", "P1 High", "Backlog", False,
     "SENSING AUDIT H5. The LD19 has a finite 10,000 h motor life and a ONE-WAY UART (230400, no "
     "command channel) -- it cannot report its own health. No spin-rate sanity, no temperature, no "
     "fault status. That makes it an UNMONITORED single point of failure for two safety-critical "
     "functions, with no declared failover.\n\n"
     "FIX (zero hardware): companion-side driver validates each sweep (point count vs expected 450, "
     "angle monotonicity, min/max range sanity), publishes health + a MAVLink OBSTACLE_DISTANCE / "
     "DISTANCE_SENSOR stream, writes the result to the spec's own tamper-evident black box.\n\n"
     "HARD RULE: any failed or stale sweep -> HOVER -> RTL.\n"
     "Track cumulative spin hours in the digital twin; schedule swap at ~8,000 h (80% of life). "
     "Carry one $135 spare LD19 per dock."),

    ("DRN-005", "Duty-cycle the depth model to fit the 7-15 W Orin-Nano envelope",
     "Orion", "P1 High", "Backlog", False,
     "SENSING AUDIT H4. The LiDAR's inability to provide 3D geometry offloads SLAM, scene "
     "classification and landing-zone reasoning onto the dense-depth network -- the most expensive "
     "model in the stack. Depth TensorRT + EO/thermal detection + point-cloud segmentation + "
     "sense-and-avoid concurrently inside 7-15 W on Orin-Nano-class silicon is not achievable at "
     "flight rate.\n\n"
     "FIX (config only): ViT-S-class depth at 322-518 px, FP16/INT8 TensorRT, duty-cycled to "
     "ARRIVAL/descend states at 5-10 Hz, while the LD19 obstacle ring runs always-on at 10 Hz as the "
     "cheap safety layer. Keep the deterministic EMD/clinical path on the MCU/companion, never on the "
     "depth model (per 'deterministic safety underneath' + 'ZERO cloud dependency for clinical "
     "function').\n\n"
     "UNVERIFIED: exact achievable FPS on Orin Nano at 15 W is INFERRED, not measured. Bench-confirm "
     "before quoting any number. Validate the frame budget in SITL before flight."),

    ("DRN-006", "Author an LD19-accurate Gazebo sensor model (SITL currently validates the wrong model)",
     "Orion", "P2 Medium", "Backlog", False,
     "SENSING AUDIT M1. A 2D 450-sample / 10 Hz plane plus monocular depth presents COMPLETELY "
     "DIFFERENT avoidance geometry from the 3D LiDAR plugin a default SITL world assumes -- and the "
     "geometry that matters (planar blind spots, beam spacing at range, absent below-vehicle data) is "
     "exactly what a generic 3D plugin papers over.\n\n"
     "CONSEQUENCE: any mission profile already 'validated' in simulation validated the wrong sensor "
     "model.\n\n"
     "FIX: author a Gazebo ray sensor matching the LD19 exactly (12 m max, 450 samples, 0.8 deg "
     "angular, 10 Hz, single plane, range/ambient masks for the 30 Klux limit) plus a camera-depth "
     "node wired to the same TensorRT model as the flight stack. Re-run existing profiles. GATE FLIGHT "
     "RELEASE on those re-runs."),

    ("DRN-007", "Publish the sensor-degradation ladder with explicit ambient thresholds",
     "Sentinel", "P2 Medium", "Backlog", False,
     "SENSING AUDIT M2. The spec names rain/fog/dust as the LiDAR killer but not the daytime one. A "
     "clear-day sunlit scene is ~100,000 lux -- about 3.3x the LD19's 30 Klux rating -- so LiDAR "
     "degrades in exactly the high-ambient conditions when EO/depth are also degraded by glare. When "
     "the radar limb is itself rain-attenuated and optics are glare-limited, the plan states NO "
     "complementary sensing for the combined case.\n\n"
     "FIX: publish a ladder in the spec -- RTK + dual IMU dead-reckoning -> mmWave proximity -> HOVER "
     "-> RTL -- with explicit ambient/visibility thresholds tied to the 30 Klux rating. Add a "
     "hydrophobic/anti-glare lens cover (single-digit dollars) to the EO/thermal apertures.\n\n"
     "The spec's own failsafe hierarchy already terminates correctly; it just is not tied to "
     "sensor-envelope numbers."),

    ("DRN-008", "HazMat + weather pod sensors on the existing pod bus",
     "Orion", "P2 Medium", "Backlog", False,
     "SENSING AUDIT M3. UNADDRESSED ENTIRELY and unaddressable by the sensing under audit: CO, LEL, "
     "H2S and radiation are non-optical quantities, so neither the 2D LiDAR nor the camera-depth stack "
     "contributes anything. Likewise no optical sensor measures wind. The weather probe is NOT marked "
     "optional. No implementation, no pod-bus allocation, no cost stated.\n\n"
     "FIX: use the already-specified pod bus ('BLE (payload pods, ground links)') -- one low-cost "
     "CO/LEL/H2S module on the pod connector for HazMat scenes. Keep radiation as a genuinely optional "
     "pod. DERIVE WIND WITH ZERO HARDWARE from the existing IMU plus ESC thrust-versus-attitude "
     "estimate. Add a $10-20 temp/humidity sensor for the spec's cold-chain ambient and landing-weather "
     "duties.\n\n"
     "UNVERIFIED: 3-gas module cost range is INFERRED -- verify against an off-the-shelf part."),

    ("DRN-009", "Correct the rPPG claim in RATCHET-Drone-Fleet-Spec.md",
     "Clinical Trends Analyst", "P3 Low", "Backlog", True,
     "SENSING AUDIT L1. The RATCHET spec cites 'camera-based photoplethysmography pulse estimation "
     "(where conditions permit)'. Measurement conditions are NOT specified, and rPPG is incompatible "
     "with the platform as described: a 10 Hz-planar-LiDAR + moving-airframe camera stack has no "
     "stated frame rate, gimbal or stabilisation requirement, against a 50-70 mph dash motion envelope "
     "and 10-15 min loiter. The parenthetical 'where conditions permit' means this is NOT a satisfied "
     "requirement.\n\n"
     "FIX -- scope discipline first: reroute the claim to 'visual casualty detection plus "
     "movement/breathing motion analysis' from the existing EO/thermal (LEO / G2VLM on the Orin Nano), "
     "computed ONLY in stable hover, processed on the truck console. DELETE or explicitly gate the "
     "rPPG claim.\n\n"
     "If rPPG is retained, add a hover-stabilised gimbal and a stated minimum frame rate as HARD "
     "requirements -- that is the only path to making the existing sentence true.\n\n"
     "Founder gate: this is a clinical-claim change; needs your sign-off before the spec is amended."),

    ("WF-001", "DECISION: final disposition of Paperclip (restore is rehearsed and available)",
     "Atlas", "P1 High", "Blocked", True,
     "The 2026-08-03 snapshot IS restorable -- rehearsed end-to-end, ~6 seconds, atomic, with a "
     "verified rollback. PG 18 both sides, 157 tables, migrations 182/182, no schema skew. The "
     "rehearsal produced 2 companies / 72 agents / 148 issues -- exactly matching the direct dump "
     "parse (two independent methods agree).\n\n"
     "See ops/workforce/01-PAPERCLIP-RESTORE-CONTINGENCY.md for the full procedure.\n\n"
     "THE ACTUAL QUESTION FOR THE FOUNDER: restoring buys back a FIVE-WEEK-OLD copy of a system that "
     "stalled -- 145 of 148 issues blocked, one agent holding 91% of the board, 22 agents in error. "
     "The data already lives on the Notion board where it can be worked.\n\n"
     "OPTIONS: (a) retire Paperclip permanently, keep the contingency documented (recommended); "
     "(b) restore into the live instance for a side-by-side reference; (c) retrieve anything else "
     "from the snapshot to Notion first, then retire.\n\n"
     "NOTE: company 58ddc931 (the newer one, ~207 issues / 54 agents) exists in NO local backup and "
     "its host paperclip.nuratech.ai returns HTTP 000. If that host can be recovered it holds data "
     "newer than anything local -- that is a separate recovery question."),
]

ok = fail = 0
for ident, title, assignee, prio, status, gate, desc in T:
    props = {
        "Task": {"title": [{"type": "text", "text": {"content": title}}]},
        "Identifier": {"rich_text": [{"type": "text", "text": {"content": ident}}]},
        "Assignee": {"rich_text": [{"type": "text", "text": {"content": assignee}}]},
        "Priority": {"select": {"name": prio}},
        "Status": {"select": {"name": status}},
        "Source": {"select": {"name": "Engineering audit"}},
        "Founder Gate": {"checkbox": gate},
        "Description": {"rich_text": [{"type": "text", "text": {"content": desc[:2000]}}]},
    }
    r = requests.post(f"{BASE}/pages", headers=H,
                      json={"parent": {"database_id": TASKS}, "properties": props}, timeout=45)
    if r.status_code < 300:
        ok += 1
        print(f"  + {ident:<8} {prio:<12} gate={str(gate):<5} {title[:52]}")
    else:
        fail += 1
        print(f"  FAIL {ident}: HTTP {r.status_code} {r.text[:130]}")
    time.sleep(0.35)

print(f"\ncreated: {ok}   failed: {fail}")

# verify
rows, cur = [], None
while True:
    b = {"page_size": 100}
    if cur:
        b["start_cursor"] = cur
    r = requests.post(f"{BASE}/databases/{TASKS}/query", headers=H, json=b, timeout=60)
    d = r.json()
    rows += d.get("results", [])
    if not d.get("has_more"):
        break
    cur = d.get("next_cursor")
print(f"board total after: {len(rows)} tasks (verified by re-read)")
