# NURA ARES Rev-A.1 — FINAL CORRECTIONS & EXECUTION ORDER
**Handoff: Hermes (CTO) → ChatGPT** · 2026-09-11 · Rev-A.1 **FROZEN**

> Eddie's final engineering note accepted in full. **Three corrections applied. No feature
> additions.** Direction: evidence, partner integration, compliance, PDR preparation.
> **The next milestone is not Rev-A.2 — it is DP2 EVIDENCE READY.**

---

## 1. THE THREE CORRECTIONS — APPLIED

### 1.1 ✅ Oxygen altitude penalty — **retracted as a requirement**
**What I got wrong:** I derived **2.69×** as the ambient-pressure ratio at 25,000 ft and applied it
to **O₂ inventory consumption**. That was a **category error** — a *volumetric* ratio applied to a
design whose flow is (or should be) **mass/molar referenced**.

**The three flow definitions now mandatory:**

| Unit | Meaning |
|---|---|
| **SLPM** | Standard L/min at a reference condition (0 °C/1 atm). **SLPM ∝ molar/mass flow — it is mass-referenced.** |
| **ALPM** | Actual L/min at local T and P. `ALPM = SLPM × (P_std/P_act) × (T_act/T_std)` |
| **g/min, mol/min** | Mass flow — **what a cylinder actually loses** |

**Where 2.69× applies, and where it does not:**

| Case | Architecture | 2.69× penalty? |
|---|---|---|
| **1** | Ambient volumetric **blower/fan** (ALPM-constrained) | **YES — physical** |
| **2** | Cylinder + regulator + **mass-flow control** (molar-constrained) | **NO — consumption altitude-independent in SLPM** |
| **3** | Cylinder + regulator + **fixed orifice** (downstream-pressure sensitive) | **ARCHITECTURE-DEPENDENT — must be measured** |

**Rev-A.1 specifies cylinder + regulator + gas blender/controller = CASE 2 or 3, not CASE 1.**

**And the CO₂ side pushes the OPPOSITE direction.** The membrane is driven by **partial pressure**.
Equilibrium CO₂ mole fraction in the sweep rises with altitude:

| Altitude | P (mmHg) | Equilibrium X_CO₂ | Molar sweep for 80 mL/min CO₂ @80% approach |
|---|---|---|---|
| 0 ft | 760.0 | 0.0592 | 1.689 SLPM |
| 8,000 ft | 564.5 | 0.0797 | 1.255 SLPM |
| 16,000 ft | 411.9 | 0.1092 | 0.915 SLPM |
| 22,000 ft | 321.0 | 0.1402 | 0.713 SLPM |
| **25,000 ft** | **282.1** | **0.1595** | **0.627 SLPM** |

**At altitude the sweep can carry MORE CO₂ before equilibrium — so the same removal might need LESS
molar sweep.** The two effects partially offset. **Neither direction may be assumed.**

**Measured spread across candidate architectures — 24 h @80 mL/min CO₂:**

| Architecture | O₂ / 24 h | LOX + dewar |
|---|---|---|
| CASE 1 ambient blower | 6,576 L | 9.9 kg |
| CASE 2 mass-flow control | 2,441 L | 4.4 kg |
| CASE 3 fixed orifice (subsonic) | 1,487 L | 3.2 kg |

> **A 4.4× spread. The gas-delivery design choice decides the logistics.**
> **Retagged `CALCULATED / REQUIRES VALIDATION`.** Pressure-regulated sweep remains strategically
> attractive but **its benefit must be PROVEN (test M4), not asserted** — until then it is a
> *hypothesis to be tested in Phase II*, not an ICD requirement.

**Metrology register now mandatory** (ICD §3.4): flow reference condition for every number · sweep
upstream pressure + control mode (MFC/orifice/blower) · membrane inlet/outlet absolute pressures ·
**exhaust pressure-regulated or ambient-referenced (the deciding parameter)** · FiO₂ at blender
outlet and membrane inlet · **mass-flow measurement on the O₂ supply** (the only trustworthy
inventory measurement) · temperature at each point · blood-side Hb/saturation/Q/temperature.

**Six tests added** to the bench-rig spec (Artifact 08): **M1** SLPM↔ALPM verification per altitude ·
**M2** O₂ consumption vs altitude per architecture · **M3** control-mode characterisation ·
**M4** pressure-regulated vs ambient-referenced A/B (**the decisive test**) · **M5** CO₂ removal vs
molar sweep per altitude · **M6** FiO₂ accuracy through the full gas path at altitude.

### 1.2 ✅ Accounting-system language — no false universal gate
**Retired:** ~~"DCMA accounting-system approval required"~~
**Adopted:** *"Cost-reimbursement accounting-system adequacy determination / pre-award review **as
required by the contracting officer**."*

There is **no universal gate**. If cost-reimbursement is contemplated the accounting system must be
adequate for that contract type — but the **exact review/approval route must be confirmed from the
current solicitation and the cognizant contracting office**, not assumed. Compliance-matrix row
rewritten.

### 1.3 ✅ Mount interface — now a defined requirement
**Retired:** ~~"2× NATO litter-rail QD clamps"~~. **A mechanical interface cannot become a
specification merely because we call it NATO-compatible.**

**Adopted:** **`MOUNT-01` — TARGET/UNKNOWN**, added to the ICD (§4a) and the compliance matrix, with
**10 unidentified inputs**: exact litter model(s) + rail geometry · restraint/attachment standard ·
**aircraft** interface standard · **ambulance** interface standard (EN 1789) · load cases
(static/dynamic/crash) · **crash loads** · **vibration environment** (rotary + fixed wing) ·
retention incl. secondary · approved transport-interfaces register · compliant mounting hardware.

**Until resolved, `MOUNT-01` is excluded from any mass or interface commitment.**
Candidate regimes to research: **STANAG 2040** and the aeromedical standards invoked by
**JECETS / USAF ATL / US Army USAARL**.

> **Everything else in Rev-A.1 stays frozen.**

---

## 2. DP2 READINESS — the top-level metric

**States (four only):** `NO EVIDENCE → PARTNER CLAIM → VERIFIED DATA → PROPOSAL-READY EVIDENCE`

| Gate | Requirement | State | Basis |
|---|---|---|---|
| **G02** | Portable battery-operated prototype | **NO EVIDENCE** | no prototype reviewed; partner required |
| **G03** | ≥2 L/min blood flow | **NO EVIDENCE** | PAS 2 L/min × 10 d ovine is a *claim* until raw data supplied |
| **G04** | ≥75 mL/min O₂ transfer | **NO EVIDENCE** | PAS ~117→90–92 mL/min — public summary only |
| **G05** | ≥40 mL/min CO₂ removal | **NO EVIDENCE** | **no public qualifying figure found for ANY candidate** |
| **G06/G07** | Qualifying autonomy (Option A) | **NO EVIDENCE** | no candidate has public qualifying evidence — **NURA'S WEDGE** |

> ### 🟥 **GREEN: 0 of 5**
> **Until all five are PROPOSAL-READY EVIDENCE, proposal writing is SECONDARY.**

**Classification discipline:** literature claims not supplied as raw data by the partner are
**PARTNER CLAIM**, never **VERIFIED DATA**. That is the difference between *"the paper says"* and
*"we can submit it."*

*Live board: `00-DP2-READINESS-BOARD.png` · machine-readable: `00-DP2-READINESS-SCOREBOARD.csv`*

---

## 3. EXECUTION PRIORITY (in order — each unblocks the next)

1. Confirm **Wyoming proposing entity, UEI and SAM status**
2. Submit the **DARPA interpretation questions** while direct clarification remains available
3. Lock the **SBIR-eligible PI and the seven missing technical/regulatory roles**
4. Contact the **A/A+ extracorporeal partners** — NDA + bench access (Artifact 09)
5. Determine whether **newly generated pre-submission bench evidence can satisfy DP2**; if yes,
   execute **Option-A qualification immediately**
6. Complete the real **NIST 800-171 / SPRS** gap assessment and POA&M
7. Resolve the **topic cost ceiling, contract type and accounting-system** requirements
8. Run **PDR** with the ICD, Life Cartridge architecture, mass/volume reconciliation, FMEA,
   traceability matrix and **verified partner hardware data**

> ⚠️ **Sequencing dependency:** item **5 gates item 4's value.** If DARPA says bench-generated data
> cannot satisfy DP2, the Option-A rig is not an eligibility pathway and the partner strategy must
> carry the whole gate. **This question should go to `SBIR_BAA@darpa.mil` before the rig is funded.**

---

## 4. FREEZE RULE (in force)

Any architecture change from this point requires **one of four triggers**:
1. **New DARPA requirement**
2. **Verified partner constraint**
3. **Bench / test result**
4. **CAD / PDR finding**

**Every change gets a configuration-control record** showing its impact on
**mass · power · safety · schedule · regulatory · DP2**.

No undocumented drift. **No feature additions.**

---

## 5. WHERE THIS LEAVES THE CAPTURE

**Before this round:** the oxygen-logistics argument was one of our strongest points — *asserted*.

**After:** it must be **earned on the bench**. That is the correct position — and it is also an
**opportunity**: a measured, architecture-aware oxygen model with a validated pressure-regulated
sweep is a defensible technical contribution most competitors will not have. **It belongs in the
Phase II SOW, not the ICD.**

**The honest state of the program:**
- Architecture: **frozen and credible**
- Evidence: **0 of 5 gates**
- Staffing: **7 roles missing**
- Federal registration: **unconfirmed**
- Partners: **uncontacted**

> **The main risk is no longer a weak idea. The main risk is failing to convert the design into
> admissible DP2 evidence before the submission window closes.**

---

## 6. ARTIFACT SET (updated)

`ops/ares/revA1/` — every numeric cell tagged
`VERIFIED | PARTNER DATA | CALCULATED | ENGINEERING ESTIMATE | TARGET | UNKNOWN`

| # | Artifact | Change this round |
|---|---|---|
| 00 | Decisions & index | + DP2 readiness, freeze rule, execution order |
| **00b** | **DP2 READINESS BOARD + scoreboard** | **NEW** |
| 01 | Interface Control Document | §3.2 retagged · §3.4 metrology register **NEW** · §4a `MOUNT-01` **NEW** |
| 02 | Life Cartridge wet/dry | unchanged |
| 03 / 03b | Mass + volume roll-up | unchanged |
| 04 | Power budget | unchanged |
| 05 | Oxygen budget | altitude rows **retagged REQUIRES VALIDATION** |
| **05a** | **Oxygen metrology & altitude validation note** | **NEW** |
| 06 | FMEA / single-fault | unchanged |
| 07 | Traceability matrix | unchanged |
| 08 | DP2 Option-A bench rig spec | **+ tests M1–M6** |
| 09 | Partner data-request package | unchanged (+ item 18: exhaust architecture) |
| 10 | DARPA compliance matrix | DCMA rewritten · `MOUNT-01` added · PERF-04 retagged |

**Not done, by design:** no partner contacted · no email sent · no DARPA question submitted ·
no prototype · SAM registration unconfirmed · no cost volume · no CAD.

---

*Hermes CTO · 2026-09-11 · Rev-A.1 FROZEN · next milestone: **DP2 EVIDENCE READY***
