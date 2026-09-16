# NURA ARES Rev-A.1 — INTERFACE CONTROL DOCUMENT (ICD)
**Artifact 01 of 10** · Revision A.1 · 2026-09-11 · Status: **DRAFT FOR ENGINEERING CLOSURE**
Every value tagged: `VERIFIED` `PARTNER DATA` `CALCULATED` `ENGINEERING ESTIMATE` `TARGET` `UNKNOWN`

> This ICD defines the frozen interfaces of the Rev-A.1 baseline. Nothing here may change without a
> recorded configuration-control decision. Values tagged `ENGINEERING ESTIMATE` or `TARGET` are
> **not specifications** and must not be quoted to a partner or a reviewer as achieved.

---

## 1. SYSTEM IDENTIFICATION

| Field | Value | Tag |
|---|---|---|
| Product | NURA ARES powered by AIME | TARGET |
| Program | DARPA DPA26BZ06-DV029, ICU-in-a-Box, Direct-to-Phase-II, Release 6 | VERIFIED |
| Revision | Rev-A.1 | TARGET |
| Core envelope | 400 × 300 × 220 mm (~26.4 L core chassis) | ENGINEERING ESTIMATE |
| Dry durable core mass | 12.42 kg bottom-up (band 9.74–15.80) | ENGINEERING ESTIMATE |
| Frozen baseline mass | 16–17 kg dry (includes margin + unallocated items) | TARGET |
| CAD packing requirement | **≤80–85% usable internal volume at PDR** | TARGET |
| Mounting | `MOUNT-01` — transport mounting interface — **TARGET / UNKNOWN** (see §4a: litter, rail, restraint, aircraft, ambulance standards not yet identified) | TARGET/UNKNOWN |
| Environment target | 25,000 ft / 7,620 m · MIL-STD-810H · MIL-STD-461G · IP55 | TARGET |

**Positioning (frozen — decision 15):** one medical system with one sensor architecture, one mission
model, one therapeutic-control hierarchy and one safety architecture. **Never describe as three
devices in one enclosure.**

---

## 2. ELECTRICAL INTERFACES

### 2.1 Power input
| Parameter | Spec | Tag |
|---|---|---|
| AC input | 100–240 VAC, 50/60 Hz | TARGET |
| Aircraft AC | 100–115 VAC, 400 Hz | TARGET |
| DC input | 12–28 VDC (range 10.2–30.3 VDC, T1-class) | VERIFIED (T1) |
| **External conversion** | **Heavy AC/aircraft conversion externalised to power adapter/dock where practical** | TARGET |
| Battery bays | 2 (hot-swap) + mission modules | TARGET |
| Battery chemistry | Li-ion, 250 Wh/kg pack, 85% usable | ENGINEERING ESTIMATE |
| **BMS** | **independent BMS per battery pack** | TARGET |
| Battery module target | 4 h per module at full-nominal (161 W) → ~0.7 kWh usable (~2.9 kg) | CALCULATED |
| Peak system draw | 302 W | ENGINEERING ESTIMATE |
| Full-nominal draw | 161 W | ENGINEERING ESTIMATE |

### 2.2 Compute / safety power domains
| Domain | Isolation requirement | Tag |
|---|---|---|
| AIME host compute | Separate rail; failure must not terminate life support | TARGET |
| Validated controllers | Separate rail from AIME host | TARGET |
| **Safety MCU** | **Independent supply + independent hardware watchdog + independent clock** | TARGET |
| Display / HMI | Sheddable (first load dropped in conservation) | TARGET |
| Comms (internal) | Sheddable | TARGET |
| ECLS pump + gas | Highest priority; never shed while supporting | TARGET |

---

## 3. GAS INTERFACES

### 3.1 Oxygen source — **source-agnostic common interface (decision 5)**
| Mission configuration | Source | Tag |
|---|---|---|
| 2–4 h transfer | lightweight compressed-gas module | TARGET |
| Prolonged litter (12–24 h) | external gas/concentrator module | TARGET |
| Vehicle / aircraft | docked oxygen + external power | TARGET |
| LOX | trade-study/logistics option — **not mandatory Rev-A hardware** | TARGET |

### 3.2 Sweep gas
| Parameter | Value | Tag |
|---|---|---|
| CO₂ target (Phase II) | ≥80 mL/min | VERIFIED |
| CO₂ target (DP2 floor) | ≥40 mL/min | VERIFIED |
| Exhaust CO₂ fraction (planning) | 6% | ENGINEERING ESTIMATE |
| Reserve/inefficiency factor | 1.18 | ENGINEERING ESTIMATE |
| **Sweep requirement @80 mL/min** | **1.573 L/min (STP)** | CALCULATED |
| **Sweep exhaust** | **pressure-regulated candidate — TO BE PROVEN (test M4)** | TARGET |
| SLPM→ALPM conversion at 25,000 ft | ×2.695 (actual-volume requirement) | CALCULATED |
| **O₂ inventory multiplier at altitude** | **ARCHITECTURE-DEPENDENT — 1.0× to 2.69×** | **REQUIRES VALIDATION** |

> ⚠️ **CORRECTED — see Artifact 05a.** The 2.69× figure is the **SLPM→ALPM conversion factor**, i.e.
> an *actual-volume* requirement. It is **not** an O₂ inventory multiplier unless the gas-delivery
> architecture is **volumetric-constrained**. Rev-A.1 specifies a **cylinder + regulator + gas
> blender/controller** — a mass/molar-referenced architecture in which the penalty may be **1.0×**,
> and in which partial-pressure bookkeeping on the CO₂ side pushes the *opposite* direction.
>
> Measured spread across candidate architectures for 24 h at 80 mL/min CO₂:
> **1,487 L – 6,576 L (4.4×)**. **The gas-delivery design choice decides the logistics.**
>
> **The pressure-regulated sweep is strategically attractive but its benefit must be PROVEN on the
> bench (test M4), not asserted.** Until then it is a *hypothesis to be tested in Phase II*, not an
> ICD requirement. All oxygen figures retagged `CALCULATED / REQUIRES VALIDATION`.
>
> A **metrology register** is now mandatory (§3.4) defining SLPM, ALPM, mass flow, upstream/downstream
> pressures, FiO₂ and mass-flow measurement for every quoted number.

### 3.3 Ventilation gas
| Parameter | Spec | Tag |
|---|---|---|
| Air supply | **integrated turbine — no external compressed air** | VERIFIED (T1-class) |
| O₂ connector | DISS (CGA 1240) or NIST | VERIFIED (T1) |
| **Separation requirement** | **no single downstream component may disable both ventilation and ECLS gas exchange** | TARGET |

### 3.4 METROLOGY REGISTER — mandatory for every flow number (added by Artifact 05a)
| # | Item | Status |
|---|---|---|
| 1 | **Flow reference condition** stated for EVERY quoted flow (SLPM @ 0 °C/1 atm, or g/min) | REQUIRED |
| 2 | Sweep supply: regulated **upstream pressure (bar)** + **control mode** (MFC \| orifice \| blower) | OPEN |
| 3 | Membrane gas **inlet** pressure (absolute) and **outlet/exhaust** pressure (absolute) | OPEN |
| 4 | **Exhaust pressure-regulated or ambient-referenced** ← **THE DECIDING PARAMETER** | OPEN |
| 5 | FiO₂ at blender outlet and O₂ fraction entering the membrane | OPEN |
| 6 | **Mass-flow measurement on the O₂ supply** — the only trustworthy inventory measurement | REQUIRED |
| 7 | Temperature at each measurement point (SLPM↔ALPM conversion requires T) | REQUIRED |
| 8 | Blood side: Hb, pre/post saturation, Q, temperature | REQUIRED |

---

## 4. FLUID INTERFACES

### 4.1 Vascular
| Parameter | Spec | Tag |
|---|---|---|
| Access | ONE central venous cannula (internal jugular or femoral) | VERIFIED (topic) |
| Preferred size | ≤15 Fr (5 mm) — design objective, **no silent relaxation** | TARGET |
| Cannulation | Out of scope (casualty assumed cannulated) | VERIFIED (topic) |

### 4.2 Circuit topology
```
PATIENT → dual-lumen ≤15 Fr cannula
   withdrawal → PUMP (2.5–3.5 L/min) → MEMBRANE LUNG → SENSORS → HEAT EXCHANGER
                                                                      ↓
                                          RETURN limb ← THERAPEUTIC MANIFOLD
                                            (vasopressor · sedation/analgesia ·
                                             anticoagulation · blood · crystalloid)
```
**Therapy enters the post-oxygenator return path when technically appropriate to minimise circuit
interaction, and ARES must MODEL extracorporeal-circuit effects on drug exposure and PK** (decision 7).

### 4.3 Fluid port schedule
| Port | Service | Side |
|---|---|---|
| P1 | Cannula withdrawal (drain) | WET (disposable) |
| P2 | Cannula return | WET (disposable) |
| P3 | Sterile sample interface | WET (disposable) |
| P4–P9 | Drug/blood/fluid manifold inlets (4–6) | WET (disposable) |
| P10 | Gas in (sweep) | DRY (durable) |
| P11 | Gas out (exhaust) | DRY (durable) |
| P12 | Thermal fluid in/out (to durable machinery) | boundary |
| P13 | O₂ source inlet | DRY (durable) |

---

## 4a. MOUNT INTERFACE — `MOUNT-01` **TARGET / UNKNOWN** (correction 3 applied)

**Retired:** ~~"2× NATO litter-rail QD clamps"~~. A mechanical interface cannot become a
specification merely because we call it NATO-compatible.

**Required before the ICD may specify this interface:**

| # | Input | Status |
|---|---|---|
| 1 | **Exact litter model(s)** and rail geometry | UNKNOWN |
| 2 | Restraint / attachment standard(s) | UNKNOWN |
| 3 | **Aircraft** interface standard(s) | UNKNOWN |
| 4 | **Ambulance** interface standard(s) (EN 1789 and equivalent) | UNKNOWN |
| 5 | **Load cases**: static, dynamic, crash | UNKNOWN |
| 6 | **Crash loads** and occupant-adjacent equipment criteria | UNKNOWN |
| 7 | **Vibration environment** (rotary + fixed wing) | UNKNOWN |
| 8 | **Retention** requirements incl. secondary retention | UNKNOWN |
| 9 | Approved **transport interfaces** register | UNKNOWN |
| 10 | Compliant **mounting hardware** candidates | UNKNOWN |

**Until resolved, `MOUNT-01` is excluded from any mass or interface commitment.**
Candidate regimes to research: STANAG 2040 (litters) and the aeromedical equipment standards invoked
by **JECETS** / USAF ATL / US Army USAARL.

---

## 5. SENSOR / DATA INTERFACES — **single logical system, redundant where catastrophic (decision 3)**

| Channel | Source | Redundancy requirement | Tag |
|---|---|---|---|
| SpO₂ / PI / PVI | Masimo rainbow SET | cross-checked with perfusion channels | VERIFIED (available) |
| SpHb | Masimo rainbow SET | **supporting trend only — NOT a transfusion trigger** | TARGET |
| EtCO₂ | capnography | altitude-corrected via BEM (Dalton) | VERIFIED (effect) |
| ECG | acquisition front-end | independent of AIME | TARGET |
| NIBP + IBP ×3 | acquisition front-end | redundant/cross-checked perfusion | TARGET |
| Circuit flow | ultrasonic | cross-checked against pump RPM | TARGET |
| Circuit pressures | pre/post oxygenator | behind sterile isolation diaphragms | TARGET |
| Air/bubble | ultrasonic + optical | **hard interlock in safety MCU** | TARGET |
| Temperature ×2 | YSI-compatible | — | VERIFIED (class) |
| **Barometric** | **dual dissimilar sensors** | **divergence alarm → conservative default + escalate** | TARGET |
| Drug delivery | pump telemetry | independent dose accounting | TARGET |
| Battery | per-pack telemetry | independent BMS per pack | TARGET |

---

## 6. BAROMETRIC ENVIRONMENT MANAGER — TWO LEVELS (decision 4)

**Level 1 — validated deterministic correction (beneath the digital twin):**
ventilator volume/flow · EtCO₂/barometric correction · gas-density calculations ·
O₂ partial-pressure interpretation · oxygenator/sweep calculations · concentrator derating ·
thermal/cooling derating · validated altitude alarm thresholds.

**Level 2 — publishes a validated environmental-state vector** to the patient and device digital
twins and to AIME.

> **AIME may reason FROM altitude and environmental limitations. AIME never generates the
> compensation equations.**

**Required qualification:** 25,000 ft altitude-chamber protocol — VT delivery accuracy at sea level /
8k / 16k / 22k / 25k ft; adult + paediatric; PEEP 0 and 20 cmH₂O; FiO₂ 0.21 and 1.0; acceptance
criteria stated before test.

---

## 7. CONTROL / SAFETY INTERFACES

### 7.1 Command chain (frozen)
```
sensor → estimator → AIME differential → candidate policy → Policy Challenge Engine
   → counterfactual harm check → physiologic invariant check → validated controller
   → independent safety MCU → actuator
```

### 7.2 Hard rules
| Rule | Tag |
|---|---|
| **AIME never actuates** — no RPM, sweep, FiO₂, blood/fluid, vasopressor, sedation, ultrafiltration | TARGET |
| **Safety MCU holds the final technical veto** — AIME is never the safety authority | TARGET |
| **No online model-weight retraining during patient care** | TARGET |
| Mandatory: differential set · uncertainty · abstention · sensor discordance · ensemble disagreement · OOD/distribution-shift detection · counterfactual harm analysis · automatic escalation on inadequate confidence | TARGET |
| **AIME/NURA compute failure must not terminate basic life support** | TARGET |
| ARES does **not** autonomously decide casualty allocation | TARGET |
| ARES does **not** autonomously withdraw support | TARGET |

---

## 8. HUMAN INTERFACES

| Item | Spec | Tag |
|---|---|---|
| Display | 9–10" ruggedised sunlight-readable (down from 12" — mass recovery item 1) | TARGET |
| Controls | 5 physical glove-operable keys + dedicated SAFE STATE | TARGET |
| Operator | field medic, basic medical training | VERIFIED (topic) |
| Setup time to autonomy | ~2 minutes | TARGET |
| Displayed state | patient state + current/past treatments (explainable audit timeline) | VERIFIED (topic) |
| Remote | authenticated augmentation; **local autonomy survives total network loss** | VERIFIED (topic) |

---

## 9. ENVIRONMENTAL / QUALIFICATION INTERFACES

| Standard | Application | Tag |
|---|---|---|
| MIL-STD-810H | temperature, shock, drop, vibration | TARGET |
| MIL-STD-461G | EMI/EMC | TARGET |
| RTCA/DO-160G | airborne equipment | TARGET |
| **JECETS** | enroute-care airworthiness (USAF ATL / US Army USAARL regime) | TARGET |
| EN 1789 | ambulance | TARGET |
| ISO 10651-3 / EN 794-3 | transport ventilators | TARGET |
| IEC 60601-1 (+ collateral) | basic safety / essential performance | TARGET |
| IP55 | ingress (T1 floor is IP54) | TARGET |
| Operating temp | −15 → +50 °C | VERIFIED (T1) |

> **Qualification language is frozen:** *"leverage prior qualification evidence"* — never
> "inherit airworthiness". OEM data supports similarity arguments; **the integrated ARES device must
> be qualified as a system** for vibration, EMC, altitude, thermal, power quality, mounting, gas flow
> and aeromedical use.

---

## 10. OPEN INTERFACE ITEMS

| ID | Item | Blocking | Tag |
|---|---|---|---|
| ICD-O1 | Oxygen architecture selection (cylinder / LOX / concentrator) | SWaP closure | UNKNOWN |
| ICD-O2 | Life Cartridge wet/dry split confirmation (Artifact 02) | partner quoting | UNKNOWN |
| ICD-O3 | Sweep pressure-regulation implementation (regulator vs back-pressure) | mass/power | UNKNOWN |
| ICD-O4 | Compute/safety MCU part selection | FMEA verification | UNKNOWN |
| ICD-O5 | Contract type → DCMA accounting approval requirement | federal gate | UNKNOWN |
| ICD-O6 | Proposing legal entity (Wyoming recommended) | SAM/UEI | UNKNOWN |

---

*Artifact 01 of 10 · NURA ARES Rev-A.1 · Hermes CTO · 2026-09-11*
