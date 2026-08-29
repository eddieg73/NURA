# MY2026 Quality & Operational Transformations — Medisun 62 Addendum (founder, 2026-08-02)

Executive addendum: 5 problems + implemented solutions. Banked for CarePilot/HEDIS ops.

## P1 — Low HEDIS/Star scores
Gaps: Care for Older Adults 71% · Diabetic Eye Exams 54% · Colorectal 40% · BP Control 58%.
Solutions: Managed Care Enrollment & Risk Stratification Form (AWV/screenings at check-in) · recall campaigns · in-clinic teleretinal eye screening · home FIT/Cologuard kits · nurse-led BP re-checks.

## P2 — TRC 0% (Transitions of Care)
0% Inpatient Admission Notification + Discharge Documentation (delayed outreach, missing HIE/ADT).
Solutions: mandatory 2-day post-discharge contact + Med Rec documentation (Page 4 of intake) · CPT II 1111F + TCM 99495/99496 on post-discharge encounters · daily discharge logs with admitting hospitals.

## P3 — Mirra→Solis clearinghouse drops
CPT II (1000F–9000F) applied but DROPPED by MSO clearinghouse (Mirra) → Solis quality engine showed zero credit.
Solutions: executive escalation with Solis (Gerardo Zuleta) · audit 837 outbound files · PARALLEL supplemental feed: batch billing logs + CPT II records direct to Solis Quality via fax: hedisfax@solishealthplans.com — OUR LANE: Documo outbound fax → hedisfax (NUR-109 hook).

## P4 — High-risk chronic mgmt
Launched 4 RPM/CCM programs: CHF & Cardiac (daily weight/BP) · CHD & Post-MI (secondary prevention) · Respiratory/Pulmonary (COPD, spirometry, pulse-ox) · Integrated Behavioral Health CoCM (53+ pts, PHQ-9/GAD-7).

## P5 — SDOH + RAF
Mandatory SDOH screening (Page 2) → CMS Z-codes (Z59.4x, Z59.82…) on intake → claim inclusion for Solis risk-adjustment uplift (ties SNS-E measure).

## System mapping (NURA)
CarePilot reminder tabs ↔ P1 solutions · Mirth ADT (NUR-82) + 2-day tracker ↔ P2 · Documo outbound fax → hedisfax@solishealthplans.com ↔ P3 · OpenEMR RPM/CCM program flags + PHQ-9/GAD-7 (LOINC) ↔ P4 · annual-patient-measures §5 (MA intake form, Z-codes) ↔ P5.
