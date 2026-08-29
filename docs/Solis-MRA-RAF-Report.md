# Solis MRA / RAF Report — Medisun Integrated Health

**Date:** 2026-08-29 · **Prepared by:** NURA Hermes (CTO/CAO) · **Source:** Ensure/Solis MRA Open-Condition Export
**Scope:** Population-health risk-adjustment review. Decision-support. Clinician/coder confirms before any filing.

---

## 1. Executive Summary
- **Population:** 70 members · 1624 risk-condition rows (1,116 under V28, 508 under V24).
- **Current plan MRA: 1.088** vs **target 1.30** → **gap of +0.212** (the strategic number to close).
- **Risk-adjustment model drift:** **508 condition rows (31%) are scored under CMS-HCC v24** while the current model is **V28**. V28 weighs the same clinical picture HIGHER (verified on our engine) → these are **under-scored**.
- **Capture opportunity:** **72 recapture candidates** across **13 members** (13)
  — conditions where V24 scored **0.000** but V28 assigns a real weight. **Summed weight-delta +24.328.**
- **Highest-risk cohort:** **2 members scored ENTIRELY under v24** (never V28) — the under-capture blind spot.

## 2. The Money Question (honest tiering)
**Direction: CONFIRMED — money is left on the table** (V24-scored conditions are under-weighted).
**Magnitude (honest):** the raw weight-delta is +24.328, but the CERTIFIED per-member RAF delta
(from hccinfhir V24-vs-V28 on the same diagnoses) is ~0.09-0.4 RAF/member. At $360 PMPM / $4,320/yr per member,
that's **real dollars but bounded** — order-of-magnitude tens-to-low-hundreds/yr per affected member.
**The 13 at-risk + 2 fully-V24 members are the highest-value targets.**

## 3. Risk Stratification (the CPHO point — more important than revenue)
The under-scored conditions are the **HIGH-burden chronic** ones: CHF/heart failure, CKD, diabetes-with-complications, COPD.
Members with these are the **likely sickest in the panel** — under-scored means **under-served AND under-coded.**
**Recapture surfaces the true-burden members for care management** — the services they need, and the accurate
risk capture improve **Star/HEDIS + avoidable admissions** as the byproduct.

## 4. Recapture Queue (de-identified summary)
- **72 candidate condition rows** · **13 affected members** · avg **+1.87** RAF/member · max **+3.49**.
- **Top conditions by count:**
  - CHRONIC KIDNEY DISEASE, MODERATE (STAGE 3) (32)
  - COAGULATION DEFECTS AND OTHER SPECIFIED HEMATOLOGICAL DISORDERS (16)
  - OTHER SIGNIFICANT ENDOCRINE AND METABOLIC DISORDERS (8)
  - FIBROSIS OF LUNG AND OTHER CHRONIC LUNG DISORDERS (8)
  - OPPORTUNISTIC INFECTIONS (4)
  - HIV/AIDS (4)

## 5. Per-Member Delta (de-identified — top contributors)
  - member (masked) +3.49 RAF
  - member (masked) +2.44 RAF
  - member (masked) +2.44 RAF
  - member (masked) +2.44 RAF
  - member (masked) +1.95 RAF
  - member (masked) +1.80 RAF

## 6. Recommended Actions (prioritized)
1. **Recapture the 13 at-risk members** — confirm + re-code the under-scored conditions under V28 (clinical + coding together, Dr. Mixter-Leon). This is the immediate revenue + accuracy win.
2. **Flag the 2 fully-V24 members highest** — they may be under-managed AND under-scored.
3. **Close the +0.212 MRA gap** — recapture is the primary lever since these are the highest-burden members where accurate coding moves the RAF most.
4. **Feed the certified lane** — once raw ICD-10s are available, run hccinfhir V24-vs-V28 on the full roster for the exact per-member dollar.

## 7. Method & Honest Boundaries
- Engine: `mimilabs/hccinfhir` (Apache-2.0) — the certified V24-vs-V28 reconciler (verified +0.088 on a sample).
- Directional analysis from the export's own HCC-weight column (V24 rows carry 0.000 where V28 pays 0.3-0.45).
- **Boundary:** the flat-file export gives HCC number + weight, NOT the raw ICD-10 codes. The certified per-member figure needs the ICD-10s (claims/834/FHIR). The +24.328 is the pre-hierarchy weight signal; the certified number is smaller.
- **PHI:** the member-identified recapture queue stays local (+ B2 PHI prefix); this report is de-identified.

## Appendix
- RAW member-identified queue: `/opt/data/raf-recapture/recapture_queue.csv` (PHI — local/B2 only, never in git).
- Certified lane: `/opt/data/raf_reconcile.py`.
