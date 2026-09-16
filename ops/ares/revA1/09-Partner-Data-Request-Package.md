# NURA ARES Rev-A.1 — PARTNER HARDWARE DATA-REQUEST PACKAGE
**Artifact 09 of 10** · Revision A.1 · 2026-09-11 · Status: **READY TO SEND (pending Eddie's authorisation)**
Every value tagged: `VERIFIED` `PARTNER DATA` `CALCULATED` `ENGINEERING ESTIMATE` `TARGET` `UNKNOWN`

> ⚠️ **NOT SENT.** No partner has been contacted. External communication is Eddie's gate.
> This package is prepared so that authorisation is the only remaining step.

---

## 1. THE ASK — REFRAMED (this is the strategic move)

**Do not ask "do you have all four DP2 items?"** Public screening found **no candidate** with a
documented qualifying closed-loop capability. Items 1–3 are demonstrably possessed by several
players. **Item 4 is the gap — and it is exactly NURA's domain.**

**Ask instead:**
> *"Do you have 1–3, and will you give us bench access to your hardware under NDA so we can qualify
> item 4 together before 23 October?"*

That converts a screening exercise into a technical sprint with NURA as the indispensable party, and
strengthens the NURA-prime case rather than presupposing an SBC prime.

**Backup framing if the partner wants to lead:** hardware-SBC prime with NURA as **exclusive
autonomy subcontractor** (once DP2 evidence is secured).

---

## 2. TARGET LIST (from public evidence)

| # | Candidate | Relevant public evidence | Key gap vs DP2 | Best role | Priority |
|---|---|---|---|---|---|
| 1 | **Geneva Foundation / AREVA — MELS** | ~5 kg portable multimodal ECLS; pump + oxygenator + renal + power; patented dual-lumen; battery + feedback-control concepts | No public quantitative O₂/CO₂ DP2 package; patent describes 2 L/min at 23 Fr not 15 Fr; tested qualifying autonomy not established | Platform/IP/animal collaborator; possible licence | **A+** |
| 2 | **CMU / UPMC — Pulmonary Assist System** | 2 L/min, 10-day ovine; O₂ transfer ~117 mL/min initial → ~90–92 late as Hb fell; stable pfHb ~7.6 mg/dL | CO₂ ≥40/80 documentation and battery/autonomy/≤15 Fr package not verified publicly | Pump-lung / hemocompatibility | **A+** |
| 3 | Hemovent — MobyBox / MOBYO | Integrated extracorporeal pump/gas-exchange; compact pneumatic MobyBox | No public qualifying autonomy; **foreign ownership prevents SBIR prime** | Hardware supplier/subcontractor | A/B |
| 4 | Abiomed / J&J — OXY-1 | FDA 510(k) K223161; preclinical sheep work ongoing | Large company; no public DP2 autonomy or ≤15 Fr evidence | Oxygenator supplier; regulatory benchmark | B |
| 5 | Getinge — CARDIOHELP / HLS | Mature portable ECLS; ~12 kg; battery capability | Size/power/cannula/autonomy not DV029-optimised | COTS benchmark | B |
| 6 | Inspira — ART100 | up to 8 L/min, >4 h battery, integrated sensors, ~12 kg | Controller/pump platform, not a proven integrated device | Pump/control supplier | B/C |
| 7 | LivaNova — LifeSPARC | compact controller/pump, up to 8 L/min, battery | Large company; no DP2 gas-transfer/autonomy evidence | Hardware benchmark | C |
| **8** | **NEW CATEGORY — ventilation integration:** Hamilton Medical | T1: MIL-STD-810G/461F, IP54, 25,000 ft, −15→+50 °C, integrated turbine, 43 dB(A), FDA 510(k) K120670 | n/a — ventilation is a DP2 *preference*, not a gate | **Licensed/OEM ventilation subsystem** | **A** |
| **9** | **NEW CATEGORY — monitoring integration:** ZOLL | Propaq M: 3.9 kg, 10.6 L, USAF ATL / US Army USAARL airworthiness (JECETS), Masimo rainbow SET incl. SpHb/POC/PVI | n/a — sensor front-end | **Licensed/OEM acquisition subsystem** | **A** |
| 10 | Autonomous-resuscitation group (per DARPA's own citation of Pinsky 2024 porcine work) | Closed-loop haemorrhagic resuscitation demonstrated | Not an ECLS platform | Autonomy research collaborator | A |

> **Priority is an outreach ranking, not a claim that any candidate already qualifies.** On public
> evidence, **no candidate should be certified as meeting all DP2 entry requirements** without
> confidential due diligence.

---

## 3. DATA-REQUEST CHECKLIST (send to every candidate)

Request **raw evidence**, not a marketing brochure.

| # | Evidence item | Required artifact | Feeds |
|---|---|---|---|
| 1 | Portable configuration | photos, BOM, dimensions, weight | DP2-G02 |
| 2 | Battery operation | runtime test, power draw, battery capacity/config | DP2-G02 |
| 3 | **≥2 L/min blood flow** | flow-vs-RPM and flow-vs-pressure **raw data** | DP2-G03 |
| 4 | **≥75 mL/min O₂ transfer** | raw pre/post blood gas, Hb, flow, temperature, FiO₂, sweep | DP2-G04 |
| 5 | **≥40 mL/min CO₂ removal** | raw pre/post blood gas and calculated removal | DP2-G05 |
| 6 | **Autonomy** | controller description, perturbation protocol, **logs, results** | **DP2-G06/G07** |
| 7 | Max continuous duration | longest bench/animal/patient support | DP2-G12 |
| 8 | Cannula | manufacturer/design, Fr, lumen geometry, vessel, pressure-flow curves | SYS-04 |
| 9 | Hemolysis | pfHb / NIH / related evidence | PERF |
| 10 | Thrombosis | ΔP, clot observations, coating/anticoagulation data | PERF |
| 11 | Sensors | flow, pressure, gas, saturation, air, temperature, chemistry | SYS-07 |
| 12 | Existing safety | alarms, interlocks, fail states | SYS-11 |
| 13 | Animal evidence | protocol, species, N, duration, raw/summary data | PERF-08 |
| 14 | Regulatory | 510(k)/PMA/IDE/CE/MDR status if applicable | REG |
| 15 | IP | patents, ownership, licences, government rights | DATA RIGHTS |
| 16 | **Proposal rights** | written permission to cite and submit confidential data to DARPA | DP2-G13 |
| 17 | O₂ consumption truth | measured sweep flow and O₂ consumption at the DP2 gate conditions | Artifact 05 model |
| 18 | Gas exhaust architecture | ambient-exhaust vs pressure-regulated — **and any altitude test data** | Artifact 05 / BEM |

**Item 18 is the one most candidates will not have.** If a partner's exhaust is ambient, their
24 h O₂ requirement at 25,000 ft is **2.69× the sea-level figure** — which changes the entire
logistics case. Ask early.

---

## 4. DRAFT OUTREACH EMAIL

> **Subject:** Confidential DP2 teaming inquiry — DARPA DPA26BZ06-DV029 ICU-in-a-Box
>
> Dr./Mr./Ms. [NAME],
>
> Nuratech AI is evaluating a team for DARPA SBIR topic **DPA26BZ06-DV029**, *"ICU-in-a-Box:
> Autonomous Extracorporeal Multiple-Organ Support Therapies."* The topic is **Direct-to-Phase-II**
> and closes **23 October 2026**.
>
> We are developing **NURA ARES powered by AIME**, focused on autonomous physiologic control,
> safety-bounded medical reasoning, embedded closed-loop control, systems integration, cybersecurity
> and remote critical-care supervision.
>
> DARPA requires Phase-I-equivalent evidence for a portable battery-operated extracorporeal
> prototype. We are therefore seeking a partner with **documented** performance — not a conceptual
> platform.
>
> Our public review of your work suggests you may hold **three of the four** DP2 entry requirements.
> The fourth — a qualifying closed-loop autonomy capability — is where we believe we add the most
> value, and we would like to explore qualifying it **together, on your hardware, under NDA**.
>
> Under NDA we would like to determine documented evidence for:
> 1. Portable / battery-operated extracorporeal operation
> 2. Blood flow ≥2 L/min
> 3. Direct O₂ transfer ≥75 mL/min
> 4. CO₂ removal ≥40 mL/min
> 5. Maximum demonstrated continuous support duration
> 6. Cannula configuration, French size, access site, pressure-flow behaviour
> 7. Existing automated/closed-loop control of SpO₂/EtCO₂ (via blood flow, sweep gas and/or FiO₂)
> 8. Available ex-vivo or large-animal hemolysis/thrombosis data
> 9. Device weight, power demand, battery runtime, sensors, safety systems
> 10. **Gas exhaust architecture** — ambient-exhaust or pressure-regulated — and any altitude test data
> 11. Background IP and the ability to make technical data available in a confidential DARPA proposal
>
> We propose a mutual NDA, a 30–45 minute engineering review, exchange of a focused DP2 evidence
> matrix, and — if technically aligned — rapid discussion of a teaming agreement or LOI.
>
> This inquiry is to establish **documented eligibility and technical fit** only. We are not asking
> for proprietary information before an NDA.
>
> Best regards,
> [NAME] · Nuratech AI · Clearwater, Florida · [PHONE] · [EMAIL]

---

## 5. INTERNAL SCORECARD (100-point, gate-oriented)

| Criterion | Weight |
|---|---|
| **Same integrated prototype satisfies the DP2 evidence standard** | **20** |
| Tested qualifying autonomy loop | **15** |
| Single-access / ≤15 Fr pathway | 10 |
| ≥2 L/min documented blood flow | 8 |
| ≥75 mL/min O₂ documented | 8 |
| ≥40 mL/min CO₂ documented | 8 |
| 24–72+ h hemocompatibility / endurance evidence | 8 |
| Battery-operated portable configuration | 6 |
| Raw data and test-report availability for the proposal | 5 |
| IP / FTO / data-rights compatibility | 5 |
| Large-animal / regulatory capability | 4 |
| Integration speed before 23 Oct | 3 |
| **Total** | **100** |

> Any candidate scoring **zero** on *"same integrated prototype DP2 evidence"* is treat as **RED**
> until DARPA clarifies whether team-combined evidence is permissible.

---

## 6. IP / FREEDOM-TO-OPERATE FLAGS TO RAISE WITH COUNSEL

| Item | Detail | Tag |
|---|---|---|
| **US patent 11,654,225** | Geneva Foundation, Batchinsky et al., *"Wearable modular extracorporeal life support device…"* — **ACTIVE to 2041-05-13**. Overlaps: wearable modular ECLS, dual-lumen access, lung + renal support, battery operation, drug/fluid administration, sensors, remote monitoring, feedback regulation | VERIFIED |
| Action | **Formal claim chart before Nuratech commits to a near-identical fluidic architecture.** The answer may be licence rather than design-around | TARGET |
| MELS quantitative caveat | public record describes 2 L/min at 23 Fr, not 15 Fr | VERIFIED |
| SBIR data rights | DARPA Phase II instructions give SBIR technical-data protections with defined government licence rights; assertions must be identified in the proposal. **Patent ownership and SBIR data rights are separate issues** | VERIFIED |

---

## 7. OUTREACH LOG

| # | Target | Owner | NDA status | First contact | Response | Score |
|---|---|---|---|---|---|---|
| 1 | Geneva / AREVA | Eddie | NOT SENT | — | — | — |
| 2 | CMU / UPMC PAS | Eddie | NOT SENT | — | — | — |
| 3 | Hemovent | Eddie | NOT SENT | — | — | — |
| 4 | Abiomed / J&J | Eddie | NOT SENT | — | — | — |
| 5 | Getinge | Eddie | NOT SENT | — | — | — |
| 6 | Inspira | Eddie | NOT SENT | — | — | — |
| 7 | LivaNova | Eddie | NOT SENT | — | — | — |
| 8 | Hamilton Medical (ventilation) | Eddie | NOT SENT | — | — | — |
| 9 | ZOLL (monitoring) | Eddie | NOT SENT | — | — | — |
| 10 | Autonomous-resuscitation group | Eddie | NOT SENT | — | — | — |

**No external contact has been made. This log is empty by design.**

---

*Artifact 09 of 10 · NURA ARES Rev-A.1 · Hermes CTO · 2026-09-11*
