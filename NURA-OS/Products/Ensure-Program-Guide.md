# ENSURE DATA SOLUTIONS — PROGRAM GUIDE (how to use the platform · 2026-08-04)

**Source:** the vendor's public documentation (ensuredatasolutions.com) + live portal observation (solis.ensuredatasolutions.com, logged in as Eddie Garrido). The vendor = HITRUST R2 certified · SOC 2 Type II · NCQA-certified HEDIS measures · Miami, FL (founded 2019).

## 1. WHAT THE PLATFORM IS
Ensure = a value-based-care analytics platform (the "Data Warehouse as a Service") for MSOs, PCP groups, ACOs, and payviders — real-time data aggregation, EHR/FHIR connectivity, AI-supported analytics, population health, risk adjustment, and care management. The Solis portal = our tenant (the Medisun MSO).

## 2. THE MODULES (the program map)
| Module | What it does | Our portal menu |
|---|---|---|
| Membership | 360° member view: new patients, relocations, disenrollments, no-recent-visit, future assignments, financial reporting | Membership |
| Revenue | financial performance, high-risk tracking, trends, projections | Revenue |
| Referrals | referral volume, leakage, specialist cost-efficiency, PMPM referral cost, peer comparison | Referrals |
| Reports/KPIs | Admits/1,000 · Readmissions · ER visits/1,000 · peer performance · cost/utilization trends | (dashboard + Reports) |
| Coding (HCC/RAF) | prospective + retrospective suspects, clinical-condition tracking, re-documentation, risk-score prediction (even uncoded suspects) | Coding |
| Pharmacy (Rx) | brand/generic/OTC costs, PMPM Rx cost, brand→generic swap opportunities | Rx |
| Admissions | Inpatient/SNF-LTC/ED/elective/post-discharge, readmissions, days, hospitalization list with Dx + notes | Hospitalization |
| Claims | total claims paid per patient (IP/OP/etc.), grouping by type/description | Claims |
| CarePlan/ICP | the individualized care-plan letter workflow (the LT037 letters, recipients, ordering coordinators) | (CarePlan/ICPSummary) |
| EnsureQual© | NCQA HEDIS measures, star stratification, CAHPS/HOS mock surveys, HRAs | (quality lane) |
| EnsureStars© | predict + close care gaps, star ratings | (quality lane) |
| EnsureCM© | care-management workflows, alerts, tasks, remote monitoring, patient portal | (care lane) |
| EnsureFin© | fund management, stop-loss analysis, risk-score projections, membership/revenue analytics | (financial lane) |
| EnsureXcel© | capitation-network leakage, specialist cost efficiency, referral patterns (high-performance network) | (network lane) |
| EnsureExchange© | bi-directional EMR/FHIR interoperability — actions/tasks passed INTO the EHR | (interop lane) |
| EnsureCRM© | lead generation, sales team, practice growth/valuation | (growth lane) |
| EnsureOTG© | the On-The-Go mobile app (24/7/365 member/trend access) | (mobile) |

## 3. HOW THE DATA FLOWS (what we observed)
```
Solis/payer data → Ensure data warehouse (MSSQL) → the .NET/DevExtreme portal
  → grids + dashboards (ICP Summary: /CarePlan/ICPSummaryGrid?_=… · filters: /CFilter/GetJsonHeaderFiltersValues
  · imports: /Home/ViewImportInformation) → exports (CSV/XLSX/PDF/HTML per the vendor)
  → CarePilot's "97 SOLIS Imported from MRA report" = the MRA/risk data pulled from Ensure
```
The portal = cookie-authenticated ASP.NET/DevExtreme (DXR.axd resources, Knockout, exceljs/jspdf for exports). No public API endpoints found (all /api/* = 404) — browser automation or approved exports for machine access.

## 4. HOW TO USE IT (the workflow doctrine)
1. **Login** (username/password — MFA if presented; never bypass).
2. **Navigate by module** (the 8-menu core: Membership/Hospitalization/Referrals/Coding/Rx/Claims/Revenue + CarePlan for letters).
3. **Run/filter the view** (the DevExtreme grids: search, filter headers, pagination 10/20/50).
4. **Export** (CSV → XLSX → JSON → PDF preference) + validate: row counts, date ranges, totals, reconciliation vs dashboard (the Ensure skill's rules).
5. **Normalize** into the canonical contracts (the hermes-ensure-operations skill's references).
6. **Analyze** per the report families: RAF/HCC suspects · HEDIS/Stars gaps · pharmacy swaps · admissions/TOC · claims anomalies · referral leakage · financial trends — flag, never treat autonomously.
7. **Act only through approved gates**: the human-review gate for clinical/coding/outreach/financial actions; Perfex writes = minimum-necessary; the staged-transaction proposal for accounting.
8. **Audit**: every run = non-PHI event (timestamp, operator, tenant, method, correlation ID, artifact hash); terminate sessions after use.

## 5. THE KEY TERMS (the vendor's vocabulary)
Membership 360 · capitation · PMPM · MLR · risk score projections · prospective vs retrospective suspects · re-documentation · HEDIS/Stars/CAHPS/HOS · stop-loss/attachment points · fund pool surplus (PIP rules) · referral leakage · admits/1,000 · readmission rate · ER visits/1,000 · utilization trends · peer-to-peer comparison · care gaps · MRA (medical record audit) · ICP (individualized care plan) · LT037 (the letter type) · service assessment (patient experience).

## 6. THE GATES (the Ensure doctrine — non-negotiable)
- No autonomous diagnosis/medication/coding/outreach/financial action.
- No PHI off the Lattice; no PHI in logs/prompts/CRM.
- Exports must reconcile or the analysis stops (escalate).
- Unfamiliar terms = unresolved (ask the operator) — never silently map.

**The platform is the source of truth for Solis data — the playbook is documented, the skill is armed, and the portal answers, boss.**
