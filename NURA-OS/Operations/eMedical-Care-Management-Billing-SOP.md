# e-Medical EHR — the Care Management Billing SOP (the Medisun GHL pipeline)

The reference pipeline: the Medisun Health Group v3 (the GoHighLevel automation) → the e-Medical EHR. The goal: the compliant claim generation, the quality code capture, the zero-leakage revenue posting.

## 1. The payer setup & plan config
| Payer | e-Medical profile | The rules |
|---|---|---|
| SOLIS Health Plans | SOLIS-MA-01 | The capitation vs FFS carve-outs mapped; the ENSURE Data Solutions API import tag linked |
| Oscar MA | OSCAR-MA-02 | The HEDIS/STARS Category II tracking enabled ($0.00 charge lines) for the quality upside |
| FFS Medicare | MEDICARE-PART-B | The standard FFS schedule; the 20% coinsurance auto-crossover enabled |
| Dual Eligible | DUAL-MED-MED | The Medicare Part B primary / Medicaid secondary; the forced $0 patient balance; the auto-bill Medicaid |

## 2. The clinical thresholds (the hard gates — never bill below)
- **CCM**: ≥20 min non-face-to-face staff time / calendar month
- **RPM**: ≥16 days of readings in the 30-day window + 20 min clinical staff
- **TCM**: the contact within 2 business days + the face-to-face within 7 (99496) / 14 (99495) days
- **BH**: ≥20 min (the General BHI 99484) or 60–70 min (the CoCM initial 99492)

## 3. The code matrix
| Track | Code | The requirement |
|---|---|---|
| CCM | 99490 / 99439 / 99487 | 20 min / +20 min / 60 min complex |
| RPM | 99453 / 99454 / 99457 / 99458 | setup (once) / 16+ days / 20 min / +20 min |
| TCM | 99495 / 99496 | 14-day / 7-day visit window |
| BH | 99484 / 99492 / 99493 | 20 min / 70 min initial / 60 min subsequent |

**The compliance hard stop**: the RPM 99454 requires the device transmission log ≥16 distinct days in the 30-day cycle. The no log proof → the no bill. If <16 days: the suppress 99454, the bill 99457 only if the 20+ staff minutes logged.

## 4. The GHL → e-Medical field mapping
| GHL workflow | The source field | The EHR target | The action |
|---|---|---|---|
| WF1/3 import | Payer, SNP, chronic conditions | Demographics & Insurance | The billing rules + the active problem list |
| WF4 auto-qual | CCM/RPM-HF/TCM/BH-Qualified | Billing alert flags | The monthly scrub queues per track |
| WF5 consent | Signed PDF, Consent=Yes | Document Management → Consents | The audit defense — required BEFORE the first claim (99453/99490) |
| WF8 ongoing | Monthly time target, device cadence | Encounter time tracker / flowsheet | The CPT threshold accumulation |
| WF9 BH escalation | BH-Escalated, high PHQ-9 | Chart banner alert | The billing hold on the BHI until the safety review closed |
| WF10 closeout | Billing codes entered | Billing → Unbilled Encounters | The Pending → Ready to Scrub transition |

## 5. The month-end closeout sequence (the exact order)
1. **The GHL export** (the 1st): the monthly summary for all CCM/RPM/TCM/BH enrollees; the time logs vs the staff records verified.
2. **The consent cross-validation**: the signed PDF intake attached under Consents & Care Plans for the new enrollees. The no consent → the no 99453/99490.
3. **The RPM transmission reconcile**: the ≥16 distinct days. The shortfall → the suppress 99454, the bill 99457 only.
4. **The ICD-10 pairing verify**: the CCM needs ≥2 chronic codes (e.g. E11.9 + I10); the TCM's primary must match the discharge summary.
5. **The Oscar Category II codes**: the 3074F (BP <130/80), 2022F (the dilated retinal exam) etc. at $0.00 for the HEDIS/STARS capture.
6. **The EDI 837 batch**: the scrub, the generate, the submit to the clearinghouse; the GHL status → "8. Billing & Revenue Posted" + the Revenue-Captured tag.

## 6. The leakage-prevention audit (the weekly)
- **Monday unbilled audit**: the e-Medical Unbilled Encounters report vs the GHL Weekly Leakage report — the patients at 20+ min in GHL with the no charges in the EHR.
- **The TCM window check**: the missed 7/14-day windows → the re-code to the standard E/M (99214/99215), never the CCM code.
- **The dual-eligible rule**: the never bill the dual-eligible patient directly for the copays/deductibles on the CCM/RPM; the auto-forward to Medicaid.

## The machine-lane constraints (the standing law)
- The eMedical = the single-session-only for the browser work (the no MCP/CLI into the UI); the FHIR API = the only machine lane (the client registration pending with the founder).
- The audit scripts log out explicitly; the no session leakage.
- The OpenEMR = the internal truth; the eMedical = the dest EMR. The never DB writes.
