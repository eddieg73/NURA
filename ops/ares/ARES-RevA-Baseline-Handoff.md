# NURA ARES — Rev-A Architecture Baseline
### DARPA DPA26BZ06-DV029 "ICU-in-a-Box" · Direct-to-Phase-II
**Handoff document — Hermes (CTO) → ChatGPT · 2026-09-11**
Status: **Rev-A baseline FROZEN** · Not built · Masses are engineering estimates

---

## 0. How to use this document

This is the consolidated technical state of the NURA ARES capture. It supersedes all earlier
ARES notes. Everything here is either **(a) verified against a primary source and cited**, or
**(b) explicitly labelled an engineering estimate/target**. Nothing is presented as achieved.

If you (ChatGPT) are continuing the design work, the two things I need from you are in
**§12 Open Decisions** — specifically the mass/volume closure strategy and the Life Cartridge
architecture. Everything else is decided and frozen.

---

## 1. THE CLOCK (corrected, verified)

| Milestone | Date | Status |
|---|---|---|
| Publication | Sept 2, 2026 | past |
| **Opening** | **Sept 23, 2026** | **12 days out** |
| **CLOSE** | **Oct 23, 2026** | **42 days out** |
| Proposal window | 30 days | — |
| Submission time | **12:00 pm ET** on close date | hard stop |

> ⚠️ **CORRECTION ON RECORD.** The original internal blueprint stated the close as
> **October 21, 2026** in at least four places. DARPA's live topic page states
> **Closes: Oct. 23, 2026**. The blueprint understated the window by two days.
> All internal deadlines, Gantt bars and the compliance matrix were rebuilt on Oct 23.

**Topic ID:** DPA26BZ06-DV029 · DoW SBIR 2026 BAA · **Release 6** · Direct-to-Phase-II only
**Source:** https://www.darpa.mil/research/programs/icu-in-a-box

---

## 2. THE EXISTENTIAL GATE (DP2 entry)

DARPA requires a **single** portable, battery-operated extracorporeal prototype demonstrating:

| ID | Requirement | Level |
|---|---|---|
| DP2-G02 | Portable, battery-operated extracorporeal prototype | MUST |
| DP2-G03 | Blood flow **≥2 L/min** with lung support | MUST |
| DP2-G04 | O₂ transfer **≥75 mL/min** | MUST |
| DP2-G05 | CO₂ removal **≥40 mL/min** | MUST |
| DP2-G06 | **≥1 of 3** qualifying autonomy algorithms | MUST |
| DP2-G07 | ↳ A: maintain SpO₂/EtCO₂ via blood flow + sweep + FiO₂ | one of three |
| DP2-G08 | ↳ B: maintain MAP via vasopressor + fluid/blood | one of three |
| DP2-G09 | ↳ C: control ultrafiltration for potassium removal | one of three |
| DP2-G12 | Max support duration, ideally **>72 h** | PROPOSE/preferred |

**Interpretation (agreed position):** the singular "**A** prototype … that can: 1) … 2) … 3) …
**and** 4) …" reads as **one integrated prototype** satisfying all four. This must be put to
DARPA in writing — it determines whether NURA can prime.

Phase II targets: **≥125 mL/min O₂** (casualty may be assumed intubated) with **~250 mL/min**
preferred; **≥80 mL/min CO₂**; ≥24 h perfusion pressure; ≥50% estimated blood volume
haemorrhage over 6 h; mechanical-ventilator integration **preferred**.

---

## 3. VERIFIED REFERENCE DEVICES (primary sources only)

### HAMILTON-T1 — ventilation reference
| Parameter | Value |
|---|---|
| Envelope | **320 × 220 × 270 mm (19.0 L)** |
| Mass | **6.5 kg** |
| Power | **50 W typical / 150 W max** |
| Battery | 72 Wh each · ~4 h one / ~8 h two · hot-swap |
| Display | 8.4" TFT (NVG option) |
| Air supply | **Integrated turbine — no compressed air** |
| Noise | 43 dB(A) sound pressure / 51 dB(A) power |
| Environment | **MIL-STD-810G + MIL-STD-461F** · IP54 · −15 → +50 °C |
| **Max altitude** | **7,620 m / 25,000 ft** |
| Airworthiness | RTCA/DO-160G · EN 1789 · ISO 10651-3 / EN 794-3 |
| **FDA** | **510(k) K120670** |
| Alarm of note | **"Performance limited by high altitude"** |

### ZOLL Propaq M — monitoring reference (adopted over X Series)
| Parameter | Value |
|---|---|
| Envelope | **226 × 264 × 178 mm (10.6 L)** |
| Mass | **3.9 kg** with battery (4.5 kg with printer) |
| Battery | 73 Wh · **7.5 h** monitoring |
| Display | 640×480 · **NVG-friendly mode** |
| Environment | MIL-STD-810G (75 G shock, 1 m drop) · **IP5X / IPX5** |
| **Operating altitude** | **15,000 ft** |
| **Airworthiness** | **USAF ATL + US Army USAARL (JECETS)** — ACM rotary wing, Safe-to-fly fixed wing |
| Parameters | ECG 3/5/12 · NIBP · IBP ×3 · temp ×2 · SpO₂ · EtCO₂ · respiration |
| **Masimo rainbow SET** | SpO₂ · SpCO · SpMet · **SpHb** · SpOC · PI · **PVI** |

**Propaq M adopted over X Series because:** 1.4 kg lighter, 1.4 L smaller, 1.5 h more runtime,
and it carries **military airworthiness certification** the X Series does not.

**Reference pair total carried separately: 29.6 L / 10.4 kg — before any ECLS hardware.**

---

## 4. VERIFICATION FINDINGS THAT CHANGE THE DESIGN

### 4.1 🔴 The altitude finding (peer-reviewed)
Study **PMID 25159349**, "Performance of portable ventilators at altitude" — altitude chamber,
sea level / 8,000 / 16,000 / 22,000 ft (barometric 760 / 564 / 412 / 321 mmHg).
Devices: Impact 731, **Hamilton T1**, CareFusion Revel.

- T1 delivered set VT within 10% **only at 8,000 ft**
- Above that, **delivered VT exceeded set VT** (same for the Revel)
- *"Only the 731 actively accounts for changes in barometric pressure to maintain the set VT
  at all tested altitudes."*
- *"Altitude compensation is an active **software algorithm**."*

**Consequence:** the T1's 25,000 ft figure is an **environmental/operating rating**
(survives and runs). It is **not** a guarantee of volume accuracy. Hamilton's own alarm table
confirms this with *"Performance limited by high altitude."* The FDA record (K120670) cites
automatic barometric compensation and RTCA/DO-160F environmental testing — but environmental
testing ≠ delivery-accuracy validation.

**Therefore → one BAROMETRIC ENVIRONMENT MANAGER (§5.2), with its own validation protocol.**

### 4.2 EtCO₂ reads low at altitude
Per Dalton's law (stated in ZOLL's own Propaq M manual), EtCO₂ values are lower at altitude.
Altitude compensation must be designed into **both** the ventilation and acquisition paths.

### 4.3 Oxygen mass dominates — the blueprint budgeted volumes, never kilograms
| Sweep 2 L/min | 24 h | 72 h |
|---|---|---|
| Steel cylinder @200 bar | 14.4 kg | 43.2 kg |
| Composite @300 bar | 13.9 kg | 41.8 kg |
| **LOX + dewar** | **5.0 kg** | **12.7 kg** |

A 24-hour mission totals **~35 kg carried** vs a 12 kg target — **2.9× over**.
**Gas + power = 25.7 kg = 73% of all mass.** Not the pump. Not the AI. **Consumables.**

**→ ARES is not a backpack. It is a litter-mounted device with a resupply tail.**
The M9 pathway is achievable only for ~2–4 hour hops.

### 4.4 Battery/endurance (250 Wh/kg pack, 85% usable)
| Load | 4 h | 8 h | 24 h |
|---|---|---|---|
| 100 W (ECLS + monitor + ventilation typical) | 1.9 kg | 3.8 kg | 11.3 kg |
| 230 W (+ ventilation max + 2× O₂ concentrator) | 4.3 kg | 8.7 kg | 26.0 kg |

**→ A "72-hour battery in a backpack" is the wrong architecture.** Hot-swap + vehicle/aircraft
power is the only coherent answer.

---

## 5. Rev-A ARCHITECTURE BASELINE — **FROZEN**

### 5.1 Core architecture — one machine, not three in a case
```
                       NURA ARES CORE
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
  Ventilation          Monitoring             ECLS
    engine            acquisition            engine
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
              BAROMETRIC ENVIRONMENT MANAGER
                             │
                    SHARED SENSOR BUS
        SpO₂ · EtCO₂ · ECG · SpHb · PVI · pressure · flow · temp
                             │
                PHYSIOLOGIC DIGITAL TWIN
                             │
                           AIME                (supervisory reasoning — NO actuation)
                             │
              VALIDATED CLOSED-LOOP CONTROLLERS
                             │
                    SAFETY GOVERNOR            (independent veto, segregable)
```

**The single-instance rule (this is where the mass saving actually comes from):**
one barometric sensor · one SpO₂ channel · one EtCO₂ channel · one temperature system ·
one clock · one comms modem · one battery controller · one display · one alarm engine ·
one audit log — all feeding ventilation, monitoring, ECLS, AIME and the safety kernel.

**Hard safety rule:** no generative model directly actuates pump RPM, sweep gas, FiO₂,
blood/fluid flow, vasopressor dose, sedation, ultrafiltration or any life-sustaining actuator.
AIME selects only validated therapeutic policies and bounded objectives. The governor may veto.

### 5.2 BAROMETRIC ENVIRONMENT MANAGER (new, first-class subsystem)
One ambient-pressure source driving **every** correction:
ventilator flow & volume · capnography (Dalton) · O₂ partial-pressure interpretation ·
gas density · membrane-lung sweep calculations · concentrator performance · cooling capacity ·
alarm thresholds.

**Required test protocol (goes in the V&V matrix and SOW):**
altitude chamber; VT delivery accuracy at **sea level / 8k / 16k / 22k / 25k ft**;
adult and paediatric; PEEP 0 and 20 cmH₂O; FiO₂ 0.21 and 1.0; **acceptance criteria stated
before test**. This is a proposal-strengthening glide path competitors will likely lack.

### 5.3 Environmental target
**25,000 ft / 7,620 m — system-level**, matching the T1. NOT 15,000 ft just because the
reference monitor stops there. Target standards: MIL-STD-810H, MIL-STD-461G, **RTCA/DO-160G**,
**JECETS** (the regime USAF ATL / US Army USAARL actually certify against), EN 1789,
ISO 10651-3. Ingress target **IP55** (T1 floor is IP54).

### 5.4 Qualification language — corrected
> **Retired phrase:** ~~"inherit airworthiness"~~
> **Correct phrase:** **"leverage prior qualification evidence"**

OEM subassembly qualification data can reduce risk and support similarity/qualification
arguments, but the **integrated ARES device must still be qualified as a system** —
vibration, EMC, altitude, thermal behaviour, power quality, mechanical mounting, gas flow,
and aeromedical use.

---

## 6. MASS GATES — **BASELINE FROZEN AT 16–17 kg**

### Gate 1 — core electronics + monitor + ventilator · target ≤9 kg
| Item | kg |
|---|---|
| T1 reference + Propaq M reference (whole units) | 10.40 |
| less duplicated display / battery / enclosure / PSU / cabling | −2.60 |
| plus Barometric Environment Manager + shared sensor bus | +0.35 |
| plus shared compute backbone (AIME host + logging) | +0.45 |
| **GATE 1 TOTAL** | **8.60 ✅ PASS (+0.40)** |

### Gate 2 — ECLS pump + dry cartridge hardware · target ≤5 kg
| Item | kg |
|---|---|
| pump + drive electronics | 1.20 |
| membrane lung / oxygenator core | 0.90 |
| Life Cartridge housing + blood-contacting shell | 0.80 |
| heat exchanger | 0.40 |
| valves, flow/ΔP/air sensors, dry circuit | 1.00 |
| cartridge retention + fluidic quick-connects | 0.30 |
| **GATE 2 TOTAL** | **4.60 ✅ PASS (+0.40)** |

### Gate 3 — complete dry operational chassis
| Item | kg |
|---|---|
| sealed IP55 enclosure, impact + vibration | 1.35 |
| NATO litter-rail QD clamps + mounting structure | 0.55 |
| sealed thermal path / heat exchanger | 0.40 |
| fasteners, gaskets, connectors, labels | 0.30 |
| **structure allowance** | **2.60** |
| **GATE 3 = 8.60 + 4.60 + 2.60** | **15.80 ❌ vs ≤15 kg stretch** |

### ✅ FREEZE DECISION (2026-09-11)
> **The Rev-A dry operational chassis baseline is 16–17 kg.**
> The ≤15 kg figure is carried **as an aspiration only**, contingent on Gate 1 landing low.

**Rationale:** Gates 1+2 total **13.20 kg** — already 0.80 kg past the 14 kg implicit budget
inside a 15 kg chassis, *before any structure*. A 2.60 kg structural allowance is **not
optional** for a MIL-SPEC sealed, litter-clamped device. Stating 15 kg as a committed
specification invites a reviewer to price a device that cannot be built.

**Consumables are explicitly OUTSIDE these gates** (never hidden in device mass):
**O₂ / LOX · blood products · drugs · mission batteries.**

---

## 7. Rev-A PHYSICAL DESIGN

**Core chassis:** 400 × 300 × 220 mm (**~26.4 L**), excluding bulk O₂ and blood.
**Mounting:** 2× NATO litter-rail QD clamps — **the device rides with the casualty.**
**Why litter-mounted, not backpack:** a combat medic already carries ~30 kg; and during
evacuation the medic is not present, so the device must travel with the patient. Litter
mounting turns every stretcher into a rolling ICU at zero extra manpower.
**Medic setup time:** ~2 minutes, then autonomous.

### Four views (produced as Rev-A sheet)
- **FRONT** — 10–12" unified display (physiology | perfusion | resources | governor state |
  AIME rationale + audit | remote link); 5 glove-operable physical keys (no touchscreen
  dependency); dedicated **SAFE STATE** control; venous/arterial cannula ports + sample port.
- **REAR** — O₂/LOX bay (cylinder DISS/NIST, LOX dewar, concentrator input, blended sweep);
  power in (100–240 VAC / 12–28 VDC vehicle-aircraft / 400 Hz); comms (WiFi, cellular, SATCOM,
  Ethernet); **sealed thermal path (IP55, no open vents)**; **NATO litter-rail QD ×2**;
  **defib DOCK interface only**.
- **SIDE** — battery A + B hot-swap bays; ventilator circuit port (insp/exp limb + flow sensor);
  **Life Cartridge slot**; service/data/calibration port; carry handle.
- **CUTAWAY** — ventilation module + acquisition module converging on one feed; Life Cartridge;
  segregated safety governor; power + compute.

### 7.1 THE ARES LIFE CARTRIDGE (single field-replaceable disposable)
```
PUMP → MEMBRANE LUNG → SENSORS → HEAT EXCHANGER → MANIFOLD
2.5–3.5 L/min  O₂/CO₂ exchange  flow/ΔP/gas/air  temp  drug·blood·fluid
```
**All therapy enters the RETURN limb — the membrane never alters a drug dose.**
One disposable assembly = one part number, one shelf-life, one field-replace step.

### 7.2 Absorption matrix
| Function | Source | Decision |
|---|---|---|
| Ventilation (turbine, no compressed air) | T1 class | **ABSORB — core** |
| ECG / arrhythmia | ZOLL | ABSORB — state estimator input |
| SpO₂ / EtCO₂ | ZOLL | ABSORB — gas-exchange control |
| NIBP + IBP ×3 / temp ×2 | ZOLL | ABSORB — perfusion control |
| **SpHb — noninvasive haemoglobin** | ZOLL rainbow | **ABSORB — HIGH VALUE** |
| **PVI — fluid responsiveness** | ZOLL rainbow | **ABSORB — HIGH VALUE** |
| SpOC — oxygenation status | ZOLL | ABSORB |
| **Defibrillation (200 J)** | ZOLL | **CUT** — already carried; dock interface only |
| **Transcutaneous pacing** | ZOLL | **CUT** — dock interface only |
| Thermal printer | ZOLL | CUT — data is digital |
| Compressed-air input | hospital vents | CUT — turbine only |

**Why SpHb + PVI matter:** oxygen transfer falls as haemoglobin falls, so Hb must be an input
to the pulmonary controller, not an afterthought. The ZOLL front-end already supplies
noninvasive Hb and fluid responsiveness → **the monitor is the perfusion state estimator's
sensor front-end, not merely a display.**

**Why the defib cut is right:** internalising defibrillation would drag high-voltage isolation,
paddle/pad interfaces, capacitor charging, waveform validation and a separate EMC campaign into
the first DARPA build — schedule and regulatory cost with **no scored benefit**. Rev-A provides a
docking/electrical interface so the function can be added in Rev-B without redesigning ARES.

### 7.3 Why integrating ventilation is not feature creep
DARPA states the casualty may be assumed **already intubated** when partial extracorporeal O₂
support is proposed, and that proposals **integrating with mechanical ventilation when present
are preferred**. A T1-class ventilator integrated directly into ARES therefore strengthens the
response to the ventilation-integration preference rather than adding unrequested scope.

---

## 8. SCOPE-CUT LIST (publish this — it is a scoring instrument)

ARES will explicitly **NOT** do in the base period:
1. No autonomous cannulation (out of scope per DARPA)
2. No defibrillation or pacing in Rev-A (interface only)
3. No venous-access decision support
4. No new membrane chemistry — integrate existing oxygenator technology
5. No new pump development — integrate or license
6. No 72-hour onboard battery or oxygen (hot-swap + resupply architecture)
7. No RRT in the base period (option only)
8. No hospital-ward features — austere en-route care only

---

## 9. FEDERAL / ADMINISTRATIVE CRITICAL PATH

> DARPA: *"contract award cannot be made without an active SAM Registration and current
> NIST Assessment."* These have **weeks-long lead times and are now more urgent than the
> DP2 evidence sprint.**

| Gate | Status | Notes |
|---|---|---|
| **SAM.gov registration + UEI** | **OPEN** | Mandatory; UEI must appear *in* the proposal; 2–6 week lead |
| **NIST SP 800-171 DoD Assessment (SPRS)** | **OPEN** | 110 controls assessed against **live systems** — not a form |
| **DSIP registration** | OPEN | Via login.gov; required to submit |
| SBA Company Registry | OPEN | Required |
| **DARPA Cost Proposal template** | OPEN | **Use is mandatory** (stated twice in the instructions) |
| **DCMA accounting-system approval** | OPEN | Required **if** requesting FAR cost-plus — a second long-lead gate |
| Package volumes | mappable | Vol 1 Cover · 2 Technical · 3 Cost · 4 Commercialization · 5 Supporting · 6 Fraud/Waste/Abuse · 7 Foreign Affiliations (**webform; PDF no longer accepted**) |

**SPRS is not paperwork — NURA's own infrastructure is the evidence.** Concrete items that will
surface in an 800-171 assessment: the dashboard admin exposure with foreign-IP logins and a
static credential, and the unpatched kernel CVE-2026-31431 (privilege escalation + container
escape). Run a real gap analysis and produce a **POA&M** before claiming SPRS readiness.

**Unverified:** I could not confirm Nuratech's SAM status programmatically (the SAM entity API
requires a key; sbir.gov returned 403). **Eddie must confirm this — it may be the true blocker.**

---

## 10. SBIR ENTITY & AFFILIATION (eligibility, not paperwork)

On record:
- **Nuratech AI LLC (Wyoming)** — *"primary legal entity supporting NURATECH AI operations and IP"*
- **Nuratech AI 2 LLC (Montana)** — *"holding or special-purpose entity"*

Rules that bite:
- SBIR permits **ONE** qualifying small business as proposer; every other commonly controlled
  entity becomes an **affiliate**
- Affiliation rules **aggregate employees and revenue** for the size test (>500 employees fails)
- Proposer must be for-profit, **>50% owned/controlled by US citizens**, and must state its
  **UEI**
- **SAM registration is per legal entity** — registering the wrong one wastes the lead time

**Strategic consequence:** the durable IP (NURA OS, Hermes adaptation, AIME architecture,
digital twin, safety-governor framework) sits in the **Wyoming** entity. If Montana proposes,
background IP and proposed work sit in different legal persons — a data-rights and teaming
problem.

> **Recommendation:** propose through **Nuratech AI LLC (Wyoming)**, disclose the Montana entity
> as an affiliate, verify aggregated headcount/revenue, and obtain the UEI for Wyoming
> **before** starting SAM registration. **Counsel must confirm.**

---

## 11. TECHNICAL VOLUME SKELETON — 20-page map

The program plan is not the proposal. The binding artefact is a **20-page Technical Volume** in
DARPA's prescribed order: ≥10-pt type, 8.5×11", 1-inch margins, sequential page numbers,
required header, no marketing filler, no active media, no locked/encrypted upload.

| # | DARPA-prescribed sequence | pages | must answer |
|---|---|---|---|
| 1 | Significance of the problem | 1.5 | why this matters (haemorrhage + organ failure, LSCO) |
| 2 | Phase-II technical objectives | 1.5 | what exists at M24, measurably |
| 3 | **DP2 EVIDENCE PACKAGE (gate)** | **3.0** | the four thresholds + the autonomy loop ← **CRITICAL** |
| 4 | Detailed base SOW | 3.0 | by DARPA month 1/3/6/9/12/15/18/21/24 |
| 5 | Human / animal use + IACUC-ACURO | 1.5 | site, sequence, DoW secondary review |
| 6 | Option SOW (months 25/28/30) | 1.0 | 24-h integrated polytrauma model |
| 7 | Related work + competitive landscape | 1.0 | MELS, PAS, commercial ECLS |
| 8 | Relationship to future R&D / Phase III | 1.5 | transition + commercialization |
| 9 | Key personnel | 1.0 | PI, chief engineer, critical-care lead |
| 10 | Foreign citizens / facilities / equipment | 1.0 | disclosures + labs |
| 11 | Technical data rights + IP assertions | 1.0 | background/foreground; **MELS FTO** |
| 12 | Subcontractors / consultants | 0.5 | work share + **≥50% compliance** |
| | **TOTAL** | **~20** | |

**Required DARPA milestone cadence:** months 1, 3, 6, 9, 12, 15, 18, 21, 24 (+ option 25, 28, 30).

---

## 12. OPEN DECISIONS — what I need from you

### 12.1 🔴 Mass/volume closure (highest priority)
Gate 3 lands at **15.80 kg** against a 15 kg stretch. Gate 1 has only **0.40 kg** of margin and
Gate 2 only **0.40 kg**. The structure allowance of 2.60 kg is the only soft number.
**Question:** should we attempt to claw back mass from the enclosure/thermal design, or accept
16–17 kg and defend it on capability grounds? If we claw back, where?

### 12.2 Life Cartridge architecture
The cartridge is the highest-risk single item (blood-contacting, disposable, field-replaceable,
0.80 kg housing + 0.90 kg membrane + 0.40 kg heat exchanger + 1.00 kg valves/sensors/dry circuit).
**Question:** which of these belong INSIDE the disposable cartridge vs on the durable side?
Moving the heat exchanger to the durable side reduces per-mission cost; moving valves to the
disposable side reduces cross-contamination risk. Trade-off needs a decision before a partner
quotes it.

### 12.3 BEM implementation
The Barometric Environment Manager is now a firmware/system requirement with an altitude-chamber
test protocol. **Question:** should it also drive the *autonomy* layer (e.g. de-rate O₂ transfer
predictions at altitude, adjust alarm thresholds), or remain a signal-conditioning layer beneath
the digital twin?

### 12.4 Oxygen architecture
Cylinders (heavy, simple) vs LOX (light, needs a supply chain and venting) vs concentrator
(doubles power). **This single choice determines the entire SWaP story** and interacts with the
mass gates. Not yet decided.

### 12.5 Triage/allocation posture — **absent from every document so far**
One ARES, three casualties: something must decide who gets it. Options: (a) device never selects,
(b) device advises, medic/medical authority decides, (c) autonomous under pre-approved criteria.
Extreme option (c) creates a machine performing battlefield triage — legal and ethical weight no
proposal has addressed. **Recommendation: raise it with DARPA before they raise it with us.**

### 12.6 AI-specific safety mitigations
The safety governor defends against **unsafe commands**, not **wrong reasoning that produces
legal commands**. Failure mode: AIME misclassifies cardiogenic shock as haemorrhagic → orders
fluids within every limit → governor allows it → pulmonary oedema. **No rule violated.**
Mitigations required: mandatory differential · abstention on discordant evidence ·
ensemble-disagreement escalation · distributional-shift detection.

### 12.7 Perfusion estimator validation (chicken-and-egg)
You cannot validate a no-arterial-line estimator without arterial ground truth. Development must
fund invasive animal work **expressly as the ground-truth channel**. Also: oscillometric NIBP is
least reliable exactly where ARES operates (profound shock, low flow).

### 12.8 Termination / futility logic
A machine sustaining physiology indefinitely against finite consumables must have a stop rule.
Withdrawal of support is among the most consequential acts in medicine. Currently unspecified.

### 12.9 Staffing and PI
SBIR requires a named **Principal Investigator**. Current NURA roster (Jade — EA/content, Amrit —
Flutter, Oussama — CRM, Nancy — billing, Natalie — PM) contains **no critical-care engineer, no
extracorporeal/fluidic engineer, no embedded safety engineer, no regulatory lead, no animal-study
PI**. The **≥50% work-share rule** means this cannot simply be subcontracted away. **This may be
a harder gate than the DP2 evidence.**

### 12.10 Cost model
The internal blueprint modelled **$3.30M–$5.70M** for 24 months (+$0.9–1.6M for the integrated
animal option) against DARPA's **$1.8M "typical" Phase II** figure. That gap is a capture-killer
and no cost volume exists yet. The topic-specific ceiling must be verified in Release 6.

---

## 13. QUESTIONS TO SEND DARPA (drafted, awaiting Eddie's approval)
Send to **SBIR_BAA@darpa.mil** — narrow interpretation questions only, no requests for
engineering advice.

1. Must DP2 items 1–4 be demonstrated on the **same integrated prototype**, or may a newly formed
   team combine documented Phase-I-equivalent subsystem evidence?
2. Must the qualifying autonomous algorithm have **directly controlled** the proposed prototype
   before submission?
3. Is **≤15 Fr** a strict threshold or a preference permitting a quantitatively justified larger
   cannula?
4. What is the **topic-specific maximum base and option cost** for DV029?
5. What is the exact **technical-question deadline** for Release 6, and the exact DSIP close date
   and time?
6. Which Release 6 DP2 technical-volume template controls if it differs from the general Phase II
   instructions?
7. May DP2 feasibility reports and raw data reside in **Volume 5** beyond the 20-page Technical
   Volume?

---

## 14. 100-YEAR VIEW — the architecture conclusion

Extracorporeal circulation is a 20th-century hack: it takes blood **out** of the body, exposes it
to plastic, inflames it, requires anticoagulation, and returns it. A far-future reviewer would say
we are automating a Rube Goldberg machine instead of eliminating the need for it.

**But the conclusion is not "stop" — it is an architecture decision:**
- The pump, oxygenator and cannula are the **disposable substrate**
- The **autonomy layer is modality-independent**: physiologic state estimation, safety-bounded
  reasoning, an independent governor, resource-aware optimisation, degraded-mode operation —
  these survive every substrate change

**Therefore the proposal should explicitly claim the intelligence layer as the durable deliverable
and treat the ECMO circuit as the current substrate.** This also answers *"what if we lose?"* — the
same stack is the product for every future organ-support modality, and for RATCHET and LOM.

**The part that will still be correct in a hundred years:** refusing to let a generative model
touch an actuator.

---

## 15. THE WEDGE (why NURA, not just a hardware vendor)

Public-evidence screening found **no candidate** with a documented qualifying closed-loop
capability. Items 1–3 (portable battery ECLS, ≥2 L/min, gas exchange) are demonstrably possessed
by several players. **Item 4 — the autonomy algorithm — is exactly NURA/AIME's domain and is
precisely the gap.**

**Therefore the partner outreach should not ask "do you have all four?"** It should ask:
> *"Do you have 1–3, and will you give us bench access to your hardware under NDA so we can
> qualify item 4 together before 23 October?"*

That converts a screening exercise into a technical sprint with NURA as the indispensable party,
and strengthens the **NURA-prime** case rather than presupposing an SBC prime.

**Cheapest qualifying proof — Option A (DP2-G07):** SpO₂/EtCO₂ control via blood flow, sweep gas
and/or FiO₂ is **bench-demonstrable without blood products, vasopressors or animals** — a real
oxygenator in a recirculating loop with deoxygenated blood analogue plus inline gas analysis.
Options B (MAP/vasopressor) and C (potassium) both require blood, drugs or animal work.

### Partner screen (from public evidence)
| Candidate | Best role | Priority |
|---|---|---|
| Geneva Foundation / AREVA — MELS (~5 kg multimodal ECLS, US patent 11,654,225) | Platform/IP/animal collaborator; possible licence | **A+** |
| CMU / UPMC — Pulmonary Assist System (2 L/min, 10-day ovine) | Pump-lung / hemocompatibility | **A+** |
| Hemovent — MobyBox / MOBYO | Hardware supplier (foreign ownership → not SBIR prime) | A/B |
| Abiomed/J&J — OXY-1 (K223161) | Oxygenator supplier, regulatory benchmark | B |
| Getinge — CARDIOHELP | COTS benchmark | B |
| Inspira — ART100 · LivaNova — LifeSPARC | Pump/control supplier | B/C |

**New partner category to add:** **ventilation and monitoring integration partners.**
Hamilton Medical and ZOLL already own the austere qualification (MIL-STD-810G/461F,
RTCA/DO-160G, IP54/IP5X, altitude, −15→+50 °C, 2 m drop, JECETS airworthiness). Licensing OEM
subsystems is far faster than re-qualifying from scratch, and their test data supports
**similarity arguments** (never "inheritance" — see §5.4).

**IP/FTO flag:** US patent **11,654,225** (Geneva Foundation, Batchinsky et al.) is **ACTIVE to
2041-05-13** and overlaps the proposed ARES fluidic architecture (wearable modular ECLS,
dual-lumen access, lung + renal support, battery operation, drug/fluid administration, sensors,
remote monitoring, feedback regulation). **Patent counsel must run a formal claim chart before
Nuratech commits to a near-identical architecture.** The answer may be licence rather than
design-around.

---

## 16. EVIDENCE INDEX

| Claim | Source |
|---|---|
| Topic requirements, DP2 gate, Phase II targets, dates | darpa.mil/research/programs/icu-in-a-box |
| T1 dimensions/mass/power/battery/altitude/standards | Hamilton T1 Technical Specifications v3.1.x |
| T1 barometric compensation + RTCA/DO-160F testing | FDA 510(k) **K120670** |
| **T1 fails to hold set VT above 8,000 ft** | **PMID 25159349** (altitude-chamber study) |
| Propaq M dimensions/mass/battery/altitude/airworthiness/rainbow SET | ZOLL Propaq M spec sheet |
| Propaq M EtCO₂ altitude note (Dalton) | ZOLL Propaq M Operator's Guide |
| SAM/UEI requirement; NIST SP 800-171; DSIP; volume structure; cost template | DARPA SBIR/STTR Phase II instructions; DARPA Proposer General Terms |
| MELS patent | US 11,654,225 (Google Patents) |
| PAS 10-day ovine data | ASAIO 2025 programme (PULM5) |

---

## 17. WHAT IS DONE vs OUTSTANDING

**Done (Hermes):**
- Clock corrected to Oct 23 (verified against DARPA's live page)
- DP2 gate + Phase II requirements transcribed and verified verbatim
- T1 and Propaq M verified against datasheets; Propaq M adopted over X Series
- Altitude finding uncovered and documented (PMID 25159349)
- O₂ mass analysis — the consumables-dominance finding (35 kg vs 12 kg)
- Rev-A architecture frozen (shared substrate + BEM + safety governor)
- Three mass gates computed; **baseline frozen at 16–17 kg**
- Rev-A four-view industrial design produced
- Absorb/cut matrix; Life Cartridge concept; scope-cut list
- Federal critical path identified (SAM/UEI, SPRS, DARPA cost template, DCMA)
- SBIR entity/affiliation analysis
- 20-page Technical Volume skeleton
- 7 DARPA interpretation questions drafted
- Partner screen + the item-4 wedge reframe
- Notion record + four concept renders; Git commits

**Outstanding (needs Eddie):**
- **SAM.gov status + UEI — confirm today; possibly the true blocker**
- Proposing entity confirmation (counsel)
- PI + staffing model
- Cost model / topic ceiling verification
- Approval to send the 7 DARPA questions
- Decision on triage posture
- Partner outreach authorisation (no external contact made — that is Eddie's gate)

**Nothing has been sent externally. No ARES prototype exists. No partner has been contacted.**

---

*Document: NURA ARES Rev-A Architecture Baseline — Handoff to ChatGPT*
*Author: Hermes (CTO) · Date: 2026-09-11 · Supersedes all prior ARES notes*
*Companion artefacts: 4 concept renders (device, integrated design, Rev-A four-view, Rev-A baseline)*
*Notion: "🚨 NURA ARES — DARPA DPA26BZ06-DV029 — CTO Review & Capture Control"*
*Repo: eddieg73/NURA → ops/ares/*
