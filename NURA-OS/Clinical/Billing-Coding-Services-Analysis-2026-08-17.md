# Billing & Coding Services — Performance Analysis (2026-08-17)

The cross-platform audit: CarePilot (the MSO Command Center) + Solis/Ensure + the EMR lane.
De-identified — member counts and categories only, no PHI.

## 1. The coding review (CarePilot error queue, live pull)
| Error state | Count | What it means |
|---|---|---|
| low_mra (undercoded) | 55 | The charts below the RAF band — the combo-code/specificity opportunities |
| needs_followup | 13 | The open follow-up states (the documentation gaps) |
| emr_not_found | 4 | The charts missing in the EMR — the charting gaps |
| **Total open** | **72** | The coding-services backlog |

## 2. The RAF position (Solis CMS-HCC V28 + CarePilot)
- The current MRA: **1.09** vs the **≥1.30** target (both platforms reconcile).
- The RAF gap: **~$7.8K/month** (the 08-04 baseline) — the undercoded chronic conditions.
- The recapture pipeline: **696 recapture + 874 suspected** rows in solis_hermes.
- The 55 low_mra + the combo-code upgrades (E11.22, I11.0, I13.x, the staged N18) = the direct recovery path.

## 3. The billing review (completed vs pending)
- The claims ride the eMed clearinghouse (the 96% first-time acceptance, the automated EOB posting).
- The CarePilot financials page = live; the pending items = the 13 needs_followup + the unreconciled EMR-not-found rows.
- The revenue side: the MLR 23.1% (the healthy band), the pharmacy savings $15.8K/mo (the generic conversions).

## 4. The team-services scorecard
| Service | Performed | The gaps |
|---|---|---|
| The combo-code capture | partial | 55 undercoded rows (the biggest dollar gap) |
| The staged specificity (N18/CKD) | partial | the recapture rows awaiting the codes |
| The EMR charting | partial | 4 charts missing entirely |
| The claims submission | strong | the 96% acceptance lane |
| The EOB posting | automated | — |

## 5. The recommendations (the priority order)
1. Run the 55 low_mra through the combo-code map → the query drafts → the provider signatures.
2. Clear the 13 follow-ups + the 4 EMR-not-found charts (the eMedical verification — the FHIR gate).
3. The annual recapture sweep on the 696 rows (the MEAT documentation).
4. The EMR verification lane: the eMedical FHIR client (the founder's 60s form).

## The doctrine
The no-upcoding line holds — every code = the documented + the provider-signed. The analysis = the counts and the categories only.
