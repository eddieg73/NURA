# NURA ARES Rev-A.1 — DECISIONS RECORD & ARTIFACT INDEX
**Master document** · Revision A.1 · 2026-09-11 · Status: **BASELINE — CONFIGURATION CONTROLLED**

> **Thesis (frozen):** 16–17 kg dry core; litter-mounted primary configuration; external mission
> oxygen/power; **wet-disposable / dry-durable** Life Cartridge; **dual-layer** barometric
> management; **redundant safety-critical channels**; **human** allocation/withdrawal authority; and
> **AIME isolated from actuators** by policy validation, counterfactual harm analysis, deterministic
> controllers and an independent hardware safety governor.
>
> **Posture:** engineering closure, DP2 evidence and proposal execution — **not** adding features.
> Major product decisions are **not reopened** unless new DARPA guidance, partner data, bench data or
> CAD analysis forces a change.

---

## CONFIDENCE TAG LEGEND
Every number in this artifact set carries one of:

| Tag | Meaning |
|---|---|
| `VERIFIED` | confirmed against a primary source (vendor datasheet, FDA record, DARPA page, peer-reviewed paper) |
| `PARTNER DATA` | must come from a hardware partner; not obtainable internally |
| `CALCULATED` | arithmetic derived from verified or estimated inputs |
| `ENGINEERING ESTIMATE` | informed engineering judgement at concept fidelity — **not a specification** |
| `TARGET` | a goal, not an achievement |
| `UNKNOWN` | no basis to estimate yet |

> **No estimated number may silently become a specification.**

---

## 1. DECISIONS RECORDED (1–16)

### 1️⃣ MASS / VOLUME — DECIDED
- **Accept 16–17 kg dry as the credible Rev-A baseline.** ≤15 kg retained as **aspirational optimisation target only**.
- **Do not** sacrifice enclosure strength, litter-mount integrity, environmental protection, electrical isolation or maintainability to chase 800 g.
- **Weight-recovery order** (attempt in this sequence):
  1. 9–10" display instead of 12"
  2. eliminate redundant internal AC/aircraft conversion — external power adapter/dock where practical
  3. externalise SATCOM as a mission module
  4. common compute/comms infrastructure
  5. durable pump motor with disposable pump head
  6. durable sensing electronics with disposable sterile interfaces
  7. external chassis as the primary structural frame (not enclosure + internal frame)
- **CAD packing requirement: ≤80–85% usable internal volume at PDR** — space must be reserved for tubing bend radius, electrical clearance, service loops, connectors, cooling, assembly tolerance and field serviceability.

### 2️⃣ LIFE CARTRIDGE — FROZEN (see Artifact 02)
- **WET = disposable. DRY = durable.**
- **Do NOT design routine in-use cartridge replacement into Rev-A.** The cartridge must survive the mission. Hot-swap/bypass during active support is a **Rev-B** problem unless DARPA explicitly requires it.

### 3️⃣ SINGLE-INSTANCE RULE — MODIFIED
- Replaced *"one sensor / one controller"* with: **one logical system and one operator interface, with independent safety-critical redundancy underneath where single failure could produce catastrophic harm.**
- Required: dual **preferably dissimilar** barometric sensors · independent BMS per battery · independent hardware watchdog/clock in the safety MCU · software alarm engine **+ independent critical hardware alarm path** · redundant/cross-checked perfusion signals · ECLS and ventilator gas architectures that avoid one downstream component disabling both · hardware actuator-inhibit/veto path independent of AIME.
- **AIME/NURA compute failure must not terminate basic life-support functions.**

### 4️⃣ BAROMETRIC ENVIRONMENT MANAGER — TWO LEVELS (see Artifact 01 §6)
- **Level 1:** validated deterministic correction beneath the digital twin.
- **Level 2:** publishes a validated environmental-state vector to the patient/device digital twins and AIME.
- **AIME may reason from altitude and environmental limitations; AIME never generates the compensation equations.**
- 25,000 ft altitude-chamber protocol retained.

### 5️⃣ OXYGEN — DECIDED (see Artifact 05)
- **Do not put the whole oxygen logistics problem inside the core chassis.** ARES is **oxygen-source agnostic with a common interface.**
- Configurations: 2–4 h transfer → lightweight compressed-gas module · prolonged litter → external gas/concentrator module · vehicle/aircraft → docked oxygen + external power · **LOX = trade-study/logistics option, not mandatory Rev-A hardware.**
- **Model updated:** consumption = **sweep × supplied O₂ fraction + reserve/inefficiency**, not sweep = pure-O₂ consumption.

### 6️⃣ SpHb / PVI — AUTHORITY DOWNGRADED
- Both retained as **high-value state-estimator inputs**.
- **SpHb = supporting trend input, NOT an autonomous transfusion trigger.**
- **PVI = supporting fluid-responsiveness input, NOT an autonomous fluid trigger.**
- Must be fused with pressure, flow, EtCO₂, SpO₂, ECG, circuit state, treatment response, haemoglobin ground truth when available, and other physiologic evidence.

### 7️⃣ PHARMACOLOGY — CORRECTED LANGUAGE
- **Retired:** ~~"the membrane never alters a drug dose."~~
- **Adopted:** *"Therapy should enter the post-oxygenator return path when technically appropriate to minimise circuit interaction; ARES must model extracorporeal-circuit effects on drug exposure and pharmacokinetics."*
- **Add an ECLS Pharmacology Model** to the digital twin for sedation, analgesia, vasopressors and future closed-loop medication modules. It **advises** validated dosing/control policies — it does not independently invent doses.

### 8️⃣ AI SAFETY — POLICY CHALLENGE ENGINE ADDED
- Command chain: `AIME differential → candidate policy → counterfactual harm check → physiologic invariant check → validated controller → independent safety MCU → actuator`
- **Mandatory:** differential hypothesis set · uncertainty/confidence · abstention · sensor discordance detection · ensemble disagreement · distribution-shift/OOD detection · counterfactual harm analysis · automatic escalation when confidence is inadequate · **no online model-weight retraining during patient care.**
- **The safety MCU remains the final technical veto. AIME is never the safety authority.**

### 9️⃣ TRIAGE — DECIDED
- **ARES does not autonomously decide which casualty receives the device.** It may provide resource and outcome projections; **allocation remains a human medical/command-authority decision under approved doctrine.**
- **Contractual boundary: ARES optimisation begins AFTER a casualty has been assigned the system.**
- Multi-casualty forecasting retained as future capability; **triage ethics must not expand this SBIR.**

### 🔟 TERMINATION / FUTILITY — DECIDED
- **No autonomous withdrawal-of-support decision.**
- ARES **may**: predict exhaustion · enter validated conservation modes · recommend escalation · identify that physiologic goals cannot be sustained · document prognosis/trajectory.
- ARES **may not** independently decide that further treatment is futile or terminate life support on that basis.

### 1️⃣1️⃣ PERFUSION VALIDATION — APPROVED
- **Fund invasive arterial/haemodynamic ground truth during development and animal testing specifically to validate the future noninvasive estimator.**
- Profound shock is precisely where NIBP and some derived indices are least trustworthy → the estimator needs **explicit uncertainty and abstention regions.**

### 1️⃣2️⃣ STAFFING — **P0 PROGRAM GATE**
Requires named or committed: **SBIR-eligible PI · extracorporeal/fluidics lead · controls/systems engineer · embedded functional-safety engineer · regulatory lead · large-animal/preclinical PI · trauma/critical-care clinical lead.**
> NURA's present software team cannot substitute for these disciplines, and work-share rules mean the core engineering cannot simply be outsourced wholesale.

### 1️⃣3️⃣ COST — HOLD THE LINE
- We are **not** inventing simultaneously: a new ventilator, new monitor, new blood pump, new membrane, new LOX system, new renal replacement platform.
- **Rev-A integrates/licences proven physical technologies** and differentiates on: integrated architecture · autonomous physiologic control · NURA mission management · AIME supervisory reasoning · patient/device digital twins · independent safety kernel · resource-aware survival-to-evacuation optimisation.

### 1️⃣4️⃣ DEADLINE — CONFLICT NOT CALLED RESOLVED
- Conflicting official DARPA date information remains in our research.
- **NURA's internal no-fail submission deadline: 21 October 2026, 12:00 ET** — until DSIP/DARPA resolves it unambiguously.
- If **23 October** is confirmed, those two days become **contingency margin, not scheduled production time.**
- *(Hermes note: my own verification of the DARPA topic page read "Closes: Oct. 23, 2026". The conservative internal date is adopted as directed.)*

### 1️⃣5️⃣ PRODUCT POSITIONING — FROZEN
- The physical machine is **NURA ARES powered by AIME** — a **litter-mounted autonomous physiology-preservation platform** integrating T1-class ventilation + Propaq-class physiologic acquisition + portable ECLS + shared gas/power/sensor infrastructure + NURA/AIME autonomy.
- **Never describe it as three devices packed into one enclosure.** It is one medical system with one sensor architecture, one mission model, one therapeutic-control hierarchy and one safety architecture.

### 1️⃣6️⃣ NEXT OUTPUTS — DELIVERED (see index below)

---

## 2. ARTIFACT INDEX

> **REV-A.1 IS FROZEN.** Final corrections applied 2026-09-11 — see **`00b-Final-Corrections-and-Execution-Order.md`**.
> Next milestone: **DP2 EVIDENCE READY** (not Rev-A.2). Freeze rule in force: any architecture change
> requires one of four triggers — new DARPA requirement · verified partner constraint · bench/test
> result · CAD/PDR finding — plus a configuration-control record covering mass, power, safety,
> schedule, regulatory and DP2 impact.

| # | Artifact | File | Status |
|---|---|---|---|
| 00 | Decisions record & index | `00-RevA1-Decisions-and-Index.md` | ✅ this document |
| **00b** | **Final corrections & execution order** | `00b-Final-Corrections-and-Execution-Order.md` | ✅ **NEW** |
| **00c** | **DP2 READINESS BOARD** | `00-DP2-READINESS-BOARD.png` + `00-DP2-READINESS-SCOREBOARD.csv` | ✅ **NEW** |
| 01 | **Interface Control Document** | `01-Interface-Control-Document.md` | ✅ |
| 02 | **Life Cartridge wet/dry architecture** | `02-Life-Cartridge-Wet-Dry.md` + `.png` | ✅ |
| 03 | **Mass + volume roll-up w/ confidence bands** | `03-Mass-Volume-Rollup.csv` + `03b-Life-Cartridge-Mass.csv` | ✅ |
| 04 | **Power budget by subsystem and mode** | `04-Power-Budget.csv` | ✅ |
| 05 | **Oxygen budget by altitude/FiO₂/sweep/duration** | `05-Oxygen-Budget.csv` | ✅ |
| 06 | **Single-fault / FMEA table** | `06-FMEA-Single-Fault.csv` | ✅ |
| 07 | **Sensor→estimator→controller→actuator traceability** | `07-Traceability-Matrix.csv` | ✅ |
| 08 | **DP2 Option-A bench-rig specification** | `08-DP2-OptionA-Bench-Rig-Spec.md` | ✅ |
| 09 | **Partner hardware data-request package** | `09-Partner-Data-Request-Package.md` | ✅ |
| 10 | **DARPA compliance / evidence matrix** | `10-DARPA-Compliance-Evidence-Matrix.csv` | ✅ |

---

## 3. HEADLINE NUMBERS FROM THE ARTIFACTS

| Quantity | Value | Tag |
|---|---|---|
| Dry durable core (bottom-up) | **12.42 kg** (band 9.74–15.80) | ENGINEERING ESTIMATE |
| Dry durable core (top-down, gate method) | 15.80 kg | ENGINEERING ESTIMATE |
| **Frozen baseline** | **16–17 kg dry** | TARGET |
| Disposable Life Cartridge | **2.22 kg** per mission | ENGINEERING ESTIMATE |
| Power — full nominal | **161 W** | ENGINEERING ESTIMATE |
| Power — full high / peak | 225 W / 302 W | ENGINEERING ESTIMATE |
| Endurance on 4 modules (1.2 kWh usable) at full nominal | **7.5 h** | CALCULATED |
| Sweep requirement @80 mL/min CO₂ | **1.573 L/min** (STP) | CALCULATED |
| Altitude penalty, ambient-exhaust @25,000 ft | **×2.69** | CALCULATED |
| Penalty with pressure-regulated sweep | **×1.00 (eliminated)** | CALCULATED |
| O₂ for 24 h @80 mL/min CO₂ (regulated) | **2,266 L** → LOX 4.2 kg / composite 11.0 kg | CALCULATED |
| LOX crossover point | ~8–12 h | CALCULATED |
| FMEA rows / critical-severity | 20 / **10** | TARGET |
| Compliance rows / open-blocker | 45 / **18** | — |

### 3.1 Two corrections the artifacts surfaced
1. **Power was underestimated by ~60%.** Rev-A carried ~100 W nominal; the bottom-up budget is **161 W**. Endurance on 4 modules is **7.5 h at full nominal**, not the 8 h previously assumed.
2. **Two estimation methods diverge by 3.4 kg** on the dry core (12.42 bottom-up vs 15.80 top-down). **That divergence IS the current uncertainty.** The frozen 16–17 kg sits at the conservative end. **PDR requirement: the two methods must reconcile within ±1 kg.**

### 3.2 The oxygen finding that matters most
An **ambient-exhaust** sweep needs **2.69× the volumetric flow at 25,000 ft**. For 24 h that is
**10,092 L vs 3,773 L at sea level.** **Pressure-regulating the sweep channel eliminates the penalty
entirely** — the regulator's mass and power are trivial next to the oxygen. This is now an
**ICD-critical requirement.**

---

## 4. P0 OPEN ITEMS (carried forward)

| # | Item | Owner | Why it blocks |
|---|---|---|---|
| 1 | **SAM.gov status + UEI** | Eddie | award cannot be made without it; weeks of lead time; **possibly the true blocker** |
| 2 | **Proposing entity (Wyoming recommended)** | Eddie + counsel | SAM is per-entity — registering the wrong one wastes the lead time |
| 3 | **PI + staffing (7 roles)** | Eddie | ≥50% work-share rule; may be a harder gate than DP2 |
| 4 | **NIST SP 800-171 / SPRS** | NURA | 110 controls against live systems; known infra findings will surface |
| 5 | **DARPA written position on integrated-prototype interpretation** | Eddie → DARPA | existential eligibility branch |
| 6 | **DARPA position: does bench-generated data count toward DP2?** | Eddie → DARPA | determines whether the Artifact 08 rig has value |
| 7 | **Oxygen architecture selection** | Engineering | decides the whole SWaP story |
| 8 | **Cost model / topic ceiling verification** | Eddie + Finance | $3.3–5.7M internal vs $1.8M typical — unresolved |
| 9 | **Contract type → DCMA accounting approval** | Eddie + Finance | second long-lead federal gate |
| 10 | **Partner authorisation** | Eddie | **nothing sent; no external contact made** |

---

## 5. WHAT HERMES HAS AND HAS NOT DONE

**Done:** clock verified and corrected · DP2 requirements transcribed verbatim · T1 and Propaq M
verified against datasheets · altitude finding uncovered (PMID 25159349) · O₂ mass analysis ·
architecture frozen · mass gates computed · Rev-A four-view design · mass/volume/power/oxygen
budgets · 20-row FMEA · 14-row traceability matrix · 45-row compliance matrix · ICD · Life Cartridge
wet/dry split · bench-rig spec · partner data-request package · entity/affiliation analysis ·
20-page Technical Volume skeleton · 7 DARPA questions drafted.

**NOT done:** no partner contacted · no email sent · no DARPA question submitted · no ARES prototype
exists · no SAM registration confirmed · no cost volume prepared · no CAD performed.

---

*Master document · NURA ARES Rev-A.1 · Hermes CTO · 2026-09-11*
*Repo: eddieg73/NURA → `ops/ares/revA1/`*
