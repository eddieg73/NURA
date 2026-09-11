# NURA ARES Rev-A.1 — DP2 OPTION-A BENCH RIG SPECIFICATION
**Artifact 08 of 10** · Revision A.1 · 2026-09-11 · Status: **SPECIFICATION DRAFT**
Every value tagged: `VERIFIED` `PARTNER DATA` `CALCULATED` `ENGINEERING ESTIMATE` `TARGET` `UNKNOWN`

> **Purpose.** Produce the DP2 entry evidence for **DP2-G06 / DP2-G07 Option A** —
> *"an algorithm that maintains oxygenation and ventilation within specified ranges for SpO₂ and
> EtCO₂ by adjusting combinations of blood flow, sweep gas and FiO₂."*
>
> **Why Option A.** It is the **only** one of the three DP2 autonomy options that is
> bench-demonstrable **without blood products, vasopressors, animals or an animal protocol**.
> Options B (MAP/vasopressor+fluid) and C (extracorporeal potassium) both require blood, drugs or
> animal work — slower, costlier, and gated on IACUC/ACURO.

---

## 1. THE GATE THIS CLOSES

| ID | Requirement | Demonstrated by |
|---|---|---|
| DP2-G06 | ≥1 qualifying autonomy capability | closed-loop logs + results |
| DP2-G07 | Option A: maintain SpO₂/EtCO₂ via blood flow, sweep gas, FiO₂ | this rig |
| DP2-G03 | ≥2 L/min blood flow | rig hydraulic characterisation *(supports)* |
| DP2-G04 | ≥75 mL/min O₂ transfer | rig gas-transfer measurement *(supports)* |
| DP2-G05 | ≥40 mL/min CO₂ removal | rig gas-transfer measurement *(supports)* |

> **Honest scope statement:** a bench rig can demonstrate the **control law and its perturbation
> response**, and can produce **first-order gas-transfer numbers on a blood analogue**. It **cannot**
> produce clinical-grade gas-transfer or hemocompatibility evidence. That requires real blood and
> ultimately large-animal work. This rig buys the **autonomy gate**, not the whole DP2 package.

---

## 2. RIG ARCHITECTURE

```
                        ┌──────────────── RIG CONTROLLER (ARES autonomy stack) ────────────────┐
                        │  estimator → AIME differential → policy challenge → validated ctrl    │
                        │  → independent safety MCU (hardware)                                  │
                        └───────────────────────────┬───────────────────────────────────────────┘
                                                    │
   ┌──────────────┐   ┌───────────┐   ┌─────────────────┐   ┌──────────────┐   ┌────────────┐
   │ RESERVOIR    │──▶│  PUMP     │──▶│  OXYGENATOR     │──▶│ SENSORS      │──▶│ RETURN to  │
   │ blood ana-   │   │ 2.5–3.5   │   │  (real, PMP     │   │ flow·pO2·pCO2│   │ reservoir  │
   │ logue, deoxy │   │ L/min     │   │   hollow-fibre) │   │ temp·ΔP      │   │ (closed    │
   │ + gas-       │◀──┴───────────┘   └────────┬────────┘   └──────────────┘   │  loop)     │
   │ equilibration│                            │                               └────────────┘
   └──────────────┘                    ┌───────┴────────┐
                                       │ GAS BLENDER    │  sweep flow + FiO₂
                                       │ pressure-regu- │  ← PRESSURE-REGULATED
                                       │ lated exhaust  │
                                       └───────┬────────┘
                                               │
                                       ┌───────┴────────┐
                                       │ O₂ SOURCE      │  cylinder + mass-flow meter
                                       └────────────────┘
```

### 2.1 Required rig elements
| # | Element | Spec / requirement | Tag |
|---|---|---|---|
| 1 | **Real oxygenator** | clinical-grade PMP hollow-fibre, with partner-provided performance curve | PARTNER DATA |
| 2 | **Pump** | capable of 2.5–3.5 L/min against the real circuit ΔP | ENGINEERING ESTIMATE |
| 3 | **Blood analogue** | deoxygenated, gas-equilibrated; haemoglobin or an O₂-carrying substitute | TARGET |
| 4 | **Gas blender** | independent control of sweep flow and FiO₂ (0.21–1.00) | TARGET |
| 5 | **Pressure-regulated sweep exhaust** | holds the sweep channel near 1 atm — **measures the altitude penalty** | TARGET |
| 6 | **Inline gas analysers** | pre- and post-membrane O₂ and CO₂, plus sweep in/out | TARGET |
| 7 | **Blood-side sensors** | flow, pre/post pressure, temperature, pO₂/pCO₂/SO₂ | TARGET |
| 8 | **Mass-flow meter on O₂ supply** | the only trustworthy O₂ consumption measurement | TARGET |
| 9 | **Programmable disturbance source** | scripted desaturation / CO₂ loading steps | TARGET |
| 10 | **Altitude simulation** | barometric chamber **or** a pressure-regulated sweep channel emulating 8k/16k/22k/25k ft | TARGET |
| 11 | **ARES autonomy stack** | the actual estimator + AIME policy layer + validated controller + safety MCU | TARGET |
| 12 | **Logger** | time-synchronised, raw, immutable; every channel + every command | TARGET |

---

## 3. TEST MATRIX

### 3.1 Characterisation (no closed loop)
| Test | Objective | Acceptance | Tag |
|---|---|---|---|
| C1 Hydraulics | flow vs RPM vs ΔP across 1.0–3.5 L/min | characterisation curve, no cavitation | TARGET |
| C2 Gas transfer — O₂ | O₂ transfer vs blood flow at fixed Hb and sweep | ≥75 mL/min at ≥2 L/min *(supporting)* | TARGET |
| C3 Gas transfer — CO₂ | CO₂ removal vs sweep at fixed blood flow | ≥40 mL/min *(supporting)* | TARGET |
| C4 Altitude | repeat C2/C3 at simulated 8k/16k/22k/25k ft | quantify penalty; **prove pressure regulation removes it** | TARGET |
| C5 Gas-consumption truth | O₂ consumed vs the 1.573 L/min sweep model × reserve | model validated or corrected | TARGET |

### 3.2 Closed-loop Option A (the actual gate)
| Test | Objective | Acceptance | Tag |
|---|---|---|---|
| A1 | Maintain SpO₂ in range by modulating blood flow alone | time-in-target ≥ stated %; no excursion beyond limits | TARGET |
| A2 | Maintain SpO₂ by modulating FiO₂ alone | as above | TARGET |
| A3 | Maintain SpO₂ by modulating sweep alone | as above | TARGET |
| A4 | **Combined** flow + sweep + FiO₂ co-optimisation | as above, with lower actuator effort than single-variable | TARGET |
| A5 | Maintain EtCO₂ in range by modulating sweep | time-in-target ≥ stated % | TARGET |
| A6 | **Simultaneous** SpO₂ + EtCO₂ control | both in range concurrently | TARGET |
| A7 | Step disturbance rejection | recover to target within stated time | TARGET |
| A8 | Ramp/physiologic drift | tracking error within stated bound | TARGET |
| A9 | Sensor freeze / drift / dropout injection | detector fires; controller enters safe mode | TARGET |
| A10 | Contradictory sensors | discordance detected; abstention + escalate | TARGET |
| A11 | Actuator saturation | graceful degradation, no windup, alarm | TARGET |
| A12 | **Safety MCU veto** | injected unsafe command is blocked at hardware | TARGET |
| A13 | **AIME host failure** | life support continues on controllers + MCU | TARGET |
| A14 | Altitude combined control | closed loop holds targets at simulated 25k ft | TARGET |

**Every closed-loop test must record:** hypothesis · configuration · inputs/perturbations ·
endpoints · acceptance criteria · instrumentation · raw-data capture · failure criteria ·
next-stage gate. *(Per the DARPA-aligned V&V ladder.)*

---

## 4. METRICS — WHAT "SUCCESS" MEANS (not "AIME gave a good recommendation")

| Domain | Metric | Tag |
|---|---|---|
| Autonomy | **% time in physiologic target** | TARGET |
| Autonomy | number and duration of out-of-envelope events | TARGET |
| Autonomy | manual override frequency | TARGET |
| Autonomy | controller transition count / chattering | TARGET |
| Safety | detected vs undetected injected faults | TARGET |
| Safety | false alarm rate | TARGET |
| Safety | safe-state latency | TARGET |
| Safety | hazardous-command veto rate | TARGET |
| Resource | O₂ consumed per hour vs model | TARGET |
| Resource | W·h consumed per hour vs Artifact 04 budget | TARGET |
| Gas | O₂ transfer, CO₂ removal vs flow/sweep | TARGET |

---

## 5. EVIDENCE PACKAGE PRODUCED (feeds DP2-G13 and Volume 5)

- Time-synchronised raw logs for every run
- Characterisation curves (hydraulics, gas transfer, altitude)
- Closed-loop perturbation results and time-in-target statistics
- Fault-injection results including safety-MCU veto demonstration
- O₂-consumption validation against the Artifact 05 model
- Photographs and a configuration record of the rig
- A signed statement of test conditions, instrumentation and calibration

---

## 6. HARD CONSTRAINTS

| Constraint | Tag |
|---|---|
| **No animal work in this rig** (that is a separate, separately-approved protocol) | TARGET |
| **No clinical claims** from bench data | TARGET |
| **The rig must contain the REAL safety MCU**, not a simulation — the veto demonstration is worthless otherwise | TARGET |
| **The AIME stack under test must be the same build intended for the proposal** | TARGET |
| Blood analogue results must be **labelled as analogue** in every figure | TARGET |
| **Nothing generated at bench may be described to DARPA as prior device achievement** | TARGET |

> ⚠️ **Programme-eligibility caveat (must be cleared in writing with DARPA).** DP2 requires evidence
> of what has **already been achieved**. Newly generated pre-submission bench data may or may not
> satisfy DARPA's intended DP2 feasibility standard. **This must be one of the questions sent to
> SBIR_BAA@darpa.mil** before the rig is funded, not after.

---

## 7. OPEN ITEMS

| ID | Item | Owner |
|---|---|---|
| BR-O1 | DARPA written position: does bench-generated data count toward DP2 feasibility? | Eddie → DARPA |
| BR-O2 | Oxygenator and partner bench-access agreement under NDA | Eddie → partner |
| BR-O3 | Blood analogue selection (Hb-based vs substitute) and its validity limits | Engineering |
| BR-O4 | Altitude: real chamber access vs pressure-regulated sweep emulation (and its defensibility) | Engineering |
| BR-O5 | Rig funding decision | Eddie |
| BR-O6 | Whether the partner's hardware can be driven by the NURA controller on their bench | Partner |

---

*Artifact 08 of 10 · NURA ARES Rev-A.1 · Hermes CTO · 2026-09-11*
