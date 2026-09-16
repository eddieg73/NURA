# NURA ARES Rev-A.1 — LIFE CARTRIDGE WET/DRY ARCHITECTURE
**Artifact 02 of 10** · Revision A.1 · 2026-09-11 · Status: **FROZEN INTERFACE**
Every value tagged: `VERIFIED` `PARTNER DATA` `CALCULATED` `ENGINEERING ESTIMATE` `TARGET` `UNKNOWN`

> **Governing rule (decision 2):** **WET = disposable. DRY = durable.**
> The blood-contacting boundary defines the split. Anything that touches blood, or forms the sterile
> boundary, is disposable. Anything that drives, senses through, or powers it is durable.

---

## 1. THE SPLIT

### 1.1 WET — Disposable ARES Life Cartridge
| Item | Mass (kg) | Tag |
|---|---|---|
| Complete blood-contacting circuit | 0.62 | ENGINEERING ESTIMATE |
| Pump head / impeller | 0.11 | ENGINEERING ESTIMATE |
| Membrane oxygenator | 0.74 | ENGINEERING ESTIMATE |
| Blood tubing or molded blood channels | *(in circuit above)* | ENGINEERING ESTIMATE |
| Blood-facing side of the heat exchanger | 0.19 | ENGINEERING ESTIMATE |
| Bubble / air-management chamber | 0.16 | ENGINEERING ESTIMATE |
| Sterile sample interface | *(in chamber above)* | ENGINEERING ESTIMATE |
| Return-limb blood/fluid/drug manifold | 0.33 | ENGINEERING ESTIMATE |
| Disposable pressure-isolation diaphragms | 0.07 | ENGINEERING ESTIMATE |
| Optional future renal cartridge/filter | — | UNKNOWN |
| **TOTAL WET (disposable)** | **2.22 kg** (band 1.74–2.83) | ENGINEERING ESTIMATE |

### 1.2 DRY — Durable chassis (subsystems that interface with the cartridge)
| Item | Mass (kg) | Tag |
|---|---|---|
| Pump motor / magnetic drive | 0.52 | ENGINEERING ESTIMATE |
| Valve actuators | 0.34 | ENGINEERING ESTIMATE |
| Ultrasonic flow sensing electronics | *(in sensing group)* | ENGINEERING ESTIMATE |
| Optical air/bubble sensing | *(in sensing group)* | ENGINEERING ESTIMATE |
| Flow sensing electronics + air/bubble optics (combined) | 0.28 | ENGINEERING ESTIMATE |
| Pressure transducers behind sterile isolation interfaces | 0.16 | ENGINEERING ESTIMATE |
| Gas controls | 0.55 | ENGINEERING ESTIMATE |
| Heater/cooler and thermal-fluid machinery | 0.48 | ENGINEERING ESTIMATE |
| Compute | 0.45 | ENGINEERING ESTIMATE |
| Safety processor | 0.18 | ENGINEERING ESTIMATE |
| Power electronics | 0.75 | ENGINEERING ESTIMATE |
| Communications | 0.16 | ENGINEERING ESTIMATE |
| Cartridge dock / retention + fluidic quick-connects | 0.34 | ENGINEERING ESTIMATE |

---

## 2. THE TWO GOVERNING PRINCIPLES

| Principle | Implementation | Tag |
|---|---|---|
| **Pinch-valve tubing is disposable; actuator stays durable** | the tube is compressed, never contacted | TARGET |
| **Blood-contacting heat-exchange surface is disposable; thermal machinery is durable** | blood-side HX in cartridge; heater/cooler + fluid loop durable | TARGET |

**Corollary — magnetic drive:** the impeller is WET, the motor and magnetic coupling are DRY.
There is no shaft seal crossing the boundary, which also removes a known thrombus nucleation site
and a sterility failure mode.

---

## 3. WHY THIS SPLIT

| Benefit | Effect | Tag |
|---|---|---|
| Sterile boundary is entirely disposable | no reprocessing of blood-contact surfaces; no cross-contamination path | TARGET |
| Durable side holds the cost | motor, actuators, sensing electronics, thermal machinery, compute amortised over many missions | TARGET |
| Per-mission cost concentrated in the cartridge | 2.22 kg consumable per mission | ENGINEERING ESTIMATE |
| Field replacement is a single assembly | one part number, one shelf-life, one replace step | TARGET |
| Sensor electronics never contact blood | reusable, calibratable, verifiable | TARGET |
| Fewer sterility-critical interfaces | keyed connectors, single orientation | TARGET |

---

## 4. **DO NOT DESIGN ROUTINE IN-USE CARTRIDGE REPLACEMENT INTO Rev-A** (decision 2)

> The primary cartridge must survive the intended mission.
> **Circuit hot-swap or bypass while actively supporting a patient is a Rev-B problem** unless DARPA
> explicitly requires it.

| Consideration | Rev-A.1 position | Tag |
|---|---|---|
| In-mission cartridge replacement | **NOT REQUIRED** | TARGET |
| Cartridge life | must meet the intended mission duration | TARGET |
| Hot-swap / bypass during active support | Rev-B, gated on explicit DARPA requirement | TARGET |
| On-cartridge condition monitoring | yes — DP across oxygenator, gas-transfer trend, dead-space index | TARGET |
| Replacement DECISION support | trend prediction + recommend escalation; **not autonomous** | TARGET |

**Consequence for the FMEA:** cartridge failure (FMEA-005/006) is mitigated by **detection +
conservation mode + escalate**, not by field replacement. This must be stated explicitly in the
proposal so a reviewer does not assume an unqualified hot-swap capability.

---

## 5. CARTRIDGE INTERFACE (mechanical / fluidic)

| Interface | Requirement | Tag |
|---|---|---|
| Retention | positive-lock dock; single orientation; mis-install must be mechanically prevented | TARGET |
| Fluidic quick-connects | keyed, non-interchangeable, drip-free on disconnect | TARGET |
| Pressure isolation | disposable diaphragms coupling to durable transducers | TARGET |
| Thermal | blood-side HX mates to durable thermal loop via sealed coupling | TARGET |
| Drive | magnetic coupling, no shaft seal | TARGET |
| Optical/ultrasonic windows | blood-side optics on cartridge; emitters/detectors durable | TARGET |
| Prime/self-test | cartridge install triggers prime + pressure-decay self-test which BLOCKS start on failure | TARGET |
| Shelf life | to be established by partner data | UNKNOWN |
| Sterilisation method | to be established (EtO / gamma / other) | UNKNOWN |

---

## 6. OPEN ITEMS (feeding the partner data request — Artifact 09)

| ID | Item | Needed from |
|---|---|---|
| LC-O1 | Which elements the partner places inside vs outside their disposable boundary | PARTNER DATA |
| LC-O2 | Achievable per-cartridge mass at the stated gas-transfer performance | PARTNER DATA |
| LC-O3 | Shelf life and sterilisation method | PARTNER DATA |
| LC-O4 | Membrane chemistry and coating (hemocompatibility basis) | PARTNER DATA |
| LC-O5 | Achievable cartridge life under continuous support | PARTNER DATA |
| LC-O6 | Cost per cartridge at volume | PARTNER DATA |
| LC-O7 | Whether a renal cartridge can share the dock without re-architecture | UNKNOWN |

---

## 7. MASS SUMMARY

`WET (disposable, per mission)  2.22 kg   ← consumable, NOT device mass`
`DRY (durable, in core)          —        ← counted in Artifact 03 core roll-up`
`MISSION LOAD ON TOP            cartridge 2.22 kg + O₂ + batteries + blood + drugs`

---

*Artifact 02 of 10 · NURA ARES Rev-A.1 · Hermes CTO · 2026-09-11*
*Companion drawing: `02-Life-Cartridge-WetDry.png`*
