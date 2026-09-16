# NURA ARES Rev-A.1 — OXYGEN FLOW METROLOGY & ALTITUDE VALIDATION NOTE
**Artifact 05a** · Revision A.1 · 2026-09-11 · Status: **CORRECTION ACCEPTED — REQUIRES VALIDATION**
Supersedes the altitude treatment in Artifact 05 and ICD §3.2.

> **Correction accepted.** The **2.69× altitude oxygen-consumption penalty must NOT be frozen as an
> established physical requirement.** It was derived for a gas-delivery architecture that Rev-A.1
> does not specify. Retagged **`CALCULATED / REQUIRES VALIDATION`**. The pressure-regulated sweep
> subsystem remains strategically attractive but its benefit **must be proven, not asserted.**

---

## 1. WHY THE CORRECTION IS RIGHT

The 2.69× ratio is the **ambient-pressure ratio** at 25,000 ft (760 / 282 ≈ 2.69). It is a
*volumetric* ratio. Whether **oxygen inventory consumption** scales that way depends entirely on
**how the gas-delivery system is constrained** — and on **how flow is defined and measured**.

I applied a volumetric ratio to a design whose flow is (or should be) **mass/molar referenced**.
That is a category error. It is corrected below.

---

## 2. THE THREE FLOW DEFINITIONS (mandatory register)

| Unit | Definition | Physical meaning |
|---|---|---|
| **SLPM** | Standard Litres Per Minute — volumetric flow referred to a **standard** condition (typically 0 °C / 1 atm) | Molar volume at standard conditions is fixed (22.414 L/mol), so **SLPM ∝ molar/mass flow. It is a mass-referenced unit.** |
| **ALPM** | Actual Litres Per Minute — volumetric flow at **local** T and P | `ALPM = SLPM × (P_std/P_act) × (T_act/T_std)` |
| **g/min or mol/min** | **Mass flow** | The physically conserved quantity — **what a cylinder actually loses** |

### 2.1 SLPM → ALPM conversion (actual volumetric requirement for a given mass flow)

| Altitude | P (mmHg) | P/P₀ | SLPM → ALPM |
|---|---|---|---|
| 0 ft | 760.0 | 1.000 | 1.000 |
| 8,000 ft | 564.5 | 0.743 | 1.346 |
| 16,000 ft | 411.9 | 0.542 | 1.845 |
| 22,000 ft | 321.0 | 0.422 | 2.368 |
| **25,000 ft** | **282.1** | **0.371** | **2.695** |

> This 2.695 is **the SLPM↔ALPM conversion factor**, i.e. an *actual-volume* requirement.
> It is **not** an O₂ inventory multiplier unless the architecture is volumetric-constrained.

---

## 3. WHERE THE 2.69× APPLIES — AND WHERE IT DOES NOT

### CASE 1 — Ambient volumetric blower / fan (ALPM-constrained)
A blower moves a fixed **ALPM** at local density. At altitude the gas is thinner, so the **mass**
flow delivered falls as P/P₀. To hold molar flow you must raise ALPM by P₀/P.
→ **the 2.69× penalty IS physical for this architecture.**

### CASE 2 — Cylinder + regulator + mass-flow control (SLPM / g·min⁻¹ constrained)
A mass flow controller holds **molar flow constant** regardless of ambient pressure. O₂ drawn from
the cylinder = molar flow × time. **Ambient pressure does not enter.**
→ **the 2.69× penalty DOES NOT APPLY.** Consumption is altitude-independent in SLPM terms.

### CASE 3 — Cylinder + regulator + fixed orifice (downstream-pressure sensitive)
Flow through a fixed orifice depends on the upstream/downstream pressure ratio. Downstream
(ambient) pressure drops at altitude, so the ratio changes — delivered flow **rises** for a choked
orifice, **falls** for a subsonic one.
→ **architecture-dependent. MUST BE MEASURED.**

> ### ✅ **Rev-A.1 specifies an O₂ cylinder + regulator + gas blender/controller.**
> That is **CASE 2 or CASE 3 — not CASE 1.** The 2.69× figure was derived for CASE 1 and applied to
> a CASE 2/3 design. **Correction accepted.**

---

## 4. THE SUBTLER EFFECT — PARTIAL-PRESSURE BOOKKEEPING ON THE CO₂ SIDE

`CO₂ removal = sweep MOLAR flow × (X_CO₂,out − X_CO₂,in)`

The membrane transfer is driven by **partial pressure**, not mole fraction. The sweep outlet
approaches equilibrium with blood pCO₂ (~45 mmHg).

| Altitude | P (mmHg) | Equilibrium X_CO₂ | Molar sweep for 80 mL/min CO₂ @ 80% approach |
|---|---|---|---|
| 0 ft | 760.0 | 0.0592 | 1.689 SLPM |
| 8,000 ft | 564.5 | 0.0797 | 1.255 SLPM |
| 16,000 ft | 411.9 | 0.1092 | 0.915 SLPM |
| 22,000 ft | 321.0 | 0.1402 | 0.713 SLPM |
| **25,000 ft** | **282.1** | **0.1595** | **0.627 SLPM** |

**At altitude the sweep can carry a HIGHER CO₂ mole fraction before reaching equilibrium.** For the
same molar sweep flow, attainable CO₂ removal could be **HIGHER** — or the same removal might need
**LESS** molar sweep.

> **The two effects point in OPPOSITE directions and partially offset.** Neither direction may be
> assumed. This is precisely why the metrology must be defined and the consumption **measured**.

*(Caveat: this assumes partial-pressure-driven transfer with the outlet near equilibrium. Kinetics,
membrane area, blood-side flow and sweep residence time all bound the real result. It is a
first-order argument for direction only — not a performance prediction.)*

---

## 5. INVENTORY CONSUMPTION BY ARCHITECTURE — 24 h, 80 mL/min CO₂

| Architecture | SLPM-equiv | O₂ / 24 h | LOX + dewar | Composite @300 bar |
|---|---|---|---|---|
| CASE 1 ambient blower (ALPM-constrained) | 4.567 | **6,576 L** | 9.9 kg | 31.8 kg |
| CASE 2 mass-flow control (molar) | 1.695 | **2,441 L** | 4.4 kg | 11.8 kg |
| CASE 3 fixed orifice (subsonic) | 1.033 | **1,487 L** | 3.2 kg | 7.2 kg |
| CASE 3′ fixed orifice (choked) | 1.695 | **2,441 L** | 4.4 kg | 11.8 kg |

> **The spread across architectures is a 4.4× difference in oxygen inventory (1,487–6,576 L).**
> **The gas-delivery design choice decides the logistics.** Nothing here may be frozen into the ICD
> as a requirement until the architecture is selected and the consumption measured.

---

## 6. METROLOGY REGISTER — what the design must now specify explicitly

| # | Item | Status |
|---|---|---|
| 1 | **Flow reference condition** stated for EVERY flow number (SLPM @ 0 °C/1 atm, or g/min) | REQUIRED |
| 2 | Sweep supply: **regulated upstream pressure (bar)** + **control mode** (MFC \| orifice \| blower) | OPEN |
| 3 | Membrane gas **inlet** pressure (absolute) and **outlet/exhaust** pressure (absolute) | OPEN |
| 4 | **Whether the exhaust is pressure-regulated or ambient-referenced** ← **THE DECIDING PARAMETER** | OPEN |
| 5 | FiO₂ at blender outlet, and O₂ fraction entering the membrane | OPEN |
| 6 | **Mass-flow measurement on the O₂ supply** — the only trustworthy inventory measurement | REQUIRED |
| 7 | Temperature at each measurement point (SLPM↔ALPM conversion requires T) | REQUIRED |
| 8 | Blood side: Hb, pre/post saturation, Q, temperature (transfer side of the balance) | REQUIRED |

---

## 7. TEST MATRIX ADDITIONS (altitude chamber / HIL)

Added to **Artifact 08** (DP2 Option-A bench rig) and the V&V matrix:

| ID | Test | Instrumentation | Acceptance |
|---|---|---|---|
| M1 | SLPM↔ALPM verification at each of sea level / 8k / 16k / 22k / 25k ft | calibrated mass-flow meter + pressure + temperature at every node | measured conversion matches ISA prediction within stated tolerance |
| M2 | **O₂ inventory consumption vs altitude, per architecture** | mass-flow meter on the O₂ supply (gravimetric cross-check where possible) | establishes the REAL altitude multiplier — replaces the 2.69× assumption |
| M3 | Sweep control-mode characterisation (MFC vs orifice vs blower) | flow + upstream/downstream pressure | identifies which case applies and quantifies sensitivity |
| M4 | **Pressure-regulated vs ambient-referenced exhaust, A/B** | both configurations, same CO₂ load | **proves or refutes the pressure-regulation benefit** |
| M5 | CO₂ removal vs sweep molar flow at each altitude | pre/post gas analysis, blood-side pCO₂ | tests the partial-pressure argument in §4 — direction and magnitude |
| M6 | FiO₂ accuracy at altitude through the full gas path | gas analyser at blender outlet and membrane inlet | FiO₂ error budget defined |

> **M4 is the decisive test for the pressure-regulated sweep subsystem.** Until it runs, that
> subsystem's value proposition is **unproven** and must be presented to DARPA as a *hypothesis to
> be tested in Phase II*, not as a design requirement.

---

## 8. DOCUMENTS CORRECTED

| Document | Change |
|---|---|
| Artifact 05 (Oxygen Budget CSV) | altitude rows retagged `CALCULATED / REQUIRES VALIDATION`; metrology columns added |
| Artifact 01 (ICD) §3.2 | 2.69× no longer stated as a requirement; now "hypothesis under test"; metrology register added |
| Artifact 01 (ICD) §6 mount | "NATO litter-rail QD" replaced with a defined-interface requirement (see §9 below) |
| Artifact 10 (Compliance matrix) | ADMIN-DCMA row rewritten — no false universal gate |
| Artifact 08 (Bench rig) | tests M1–M6 added |

---

## 9. MOUNT INTERFACE — CORRECTION APPLIED (correction 3)

**Retired language:** ~~"2× NATO litter-rail QD clamps"~~ — a mechanical interface cannot become a
specification merely because we call it NATO-compatible.

**Adopted:** `MOUNT-01 — Transport mounting interface — **TARGET / UNKNOWN**`

The ICD must not specify this until the actual standards are identified. Required inputs:

| # | Input | Status |
|---|---|---|
| 1 | **Exact litter model(s)** and rail geometry | UNKNOWN |
| 2 | Restraint/attachment standard(s) | UNKNOWN |
| 3 | **Aircraft** interface standard(s) | UNKNOWN |
| 4 | **Ambulance** interface standard(s) (EN 1789 and equivalent) | UNKNOWN |
| 5 | **Load cases**: static, dynamic, crash | UNKNOWN |
| 6 | **Crash loads** and occupant-adjacent equipment criteria | UNKNOWN |
| 7 | **Vibration environment** (rotary + fixed wing) | UNKNOWN |
| 8 | **Retention** requirements (incl. secondary retention) | UNKNOWN |
| 9 | Approved **transport interfaces** register | UNKNOWN |
| 10 | Compliant **mounting hardware** candidates | UNKNOWN |

**Until these are resolved, the mount is tagged `TARGET/UNKNOWN` in the ICD and excluded from any
mass or interface commitment.** Candidate regimes to research: STANAG 2040 (litters) and the
aeromedical equipment standards invoked by **JECETS** / USAF ATL / US Army USAARL.

---

## 10. ACCOUNTING-SYSTEM LANGUAGE — CORRECTION APPLIED (correction 2)

**Retired:** ~~"DCMA accounting-system approval required"~~

**Adopted:** *"Cost-reimbursement accounting-system adequacy determination / pre-award review **as
required by the contracting officer**."*

There is **no universal gate**. If the contemplated award type is cost-reimbursement, the accounting
system must be adequate for that contract type — but the **exact review/approval route must be
confirmed from the current solicitation and the cognizant contracting office**, not assumed.

---

## 11. WHAT THIS MEANS FOR THE CAPTURE

| Before | After |
|---|---|
| 2.69× altitude penalty stated as a requirement | **hypothesis under test — retagged REQUIRES VALIDATION** |
| Pressure-regulated sweep presented as a decided architecture | **strategically attractive; benefit must be PROVEN (test M4)** |
| Oxygen inventory implied by one number | **4.4× spread by architecture — design choice decides it** |
| Oxygen mass story used as an argument | **may only be used once the architecture is selected and measured** |
| "NATO litter-rail QD" as an ICD spec | **TARGET/UNKNOWN defined-interface requirement (10 inputs)** |
| DCMA approval as a universal gate | **contract-type-conditional; route to be confirmed** |

> **Net effect on the DP2 case:** the oxygen-logistics argument — previously one of the strongest
> points — must now be **earned on the bench** rather than asserted. That is the correct position,
> and it is also an **opportunity**: a measured, architecture-aware oxygen model with a validated
> pressure-regulated sweep is a defensible technical contribution that most competitors will not
> have. It belongs in the Phase II SOW.

---

*Artifact 05a · NURA ARES Rev-A.1 · Hermes CTO · 2026-09-11*
*Correction accepted from Eddie's final engineering note. All figures CALCULATED / REQUIRES VALIDATION.*
