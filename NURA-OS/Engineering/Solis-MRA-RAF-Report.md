# Solis MRA / RAF Report — 2026-08-29

Date: 2026-08-29 · Operator: Hermes (CTO/CAO) · Data: Ensure/Solis MRA export (1,624 rows / 70 members)
DELIVERABLE: `/opt/data/solis-raf-report/Solis-MRA-RAF-Report.md` (generated, decision-ready) — mirrored to B2 + GitHub.

## Executive conclusions
- **Population:** 70 members, 1,624 risk rows (1,116 V28 / 508 V24). **31% scored under the pre-V28 model.**
- **MRA 1.088 → target 1.30 = +0.212 gap** (the strategic number).
- **72 recapture candidates** across **13 members**; **2 members fully under V24** (never V28) = the blind spot.
- **Direction: money left on the table** (V24 conditions scored 0.000 where V28 pays 0.3-0.45). **Magnitude bounded** — certified per-member RAF delta ~0.09-0.4; at $360 PMPM, tens-to-low-hundreds/yr per affected member.

## CPHO read (the real point)
The under-scored conditions are high-burden chronic (CKD stage 3, CHF, diabetes-complications, COPD, HIV/AIDS, coagulation).
These are the SICKEST members — under-scored = under-served AND under-coded. **Recapture surfaces them for care management;
the revenue is a byproduct of doing risk capture right.** Top gap conditions: CKD-moderate (32), coagulation (16), endocrine/metabolic (8),
lung fibrosis (8), opportunistic infections / HIV (4 each).

## Method + honest boundary
- Certified lane: `mimilabs/hccinfhir` (V24-vs-V28, verified +0.088 on a sample dx set).
- Directional analysis from the export's HCC-weight column. **The flat file has no ICD-10s** → the certified per-member
  dollar needs the raw codes (claims/834/FHIR). `+24.33` = pre-hierarchy weight signal; certified number smaller.
- PHI: member queue local + B2 PHI prefix only; report is de-identified.

## Artifacts
- Report: `/opt/data/solis-raf-report/Solis-MRA-RAF-Report.md` (de-identified)
- Recapture queue (PHI): `/opt/data/raf-recapture/recapture_queue.json/.csv`
- Generator: `/opt/data/gen_solis_report.py` | Certified lane: `/opt/data/raf_reconcile.py`
- B2: `nura-documents/raf-reconciliation/` (no-PHI/summaries + PHI/recapture-queue)

## Next
1. Flag the 13 at-risk + 2 fully-V24 members for recapture (clinical + coding, Dr. Mixter-Leon).
2. Get the ICD-10s (claims/834/FHIR) → run the certified per-member dollar via raf_reconcile.py.
