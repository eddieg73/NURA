# FLORIDA 2026 PAYER FEE SCHEDULES — LOADED (Medisun lane, 2026-08-02)

**Founder: load current fee-for-service tables for FL payers 2026 — MA PMPM: Solis, Oscar (FFS with upside). For Medisun. Sources verified [V] / unverified [U].**

## 1. MEDICARE PHYSICIAN FEE SCHEDULE — FL 2026 [V]
- **CY 2026 conversion factors** (CMS final rule): qualifying APM **$33.57** (+3.77%) · non-QP **$33.40** (+3.26%) — from $32.35 (2025)
- **FL localities**: 03 · 04 · 99 (county map per FCSO; Clearwater/Tampa Bay = Loc 03)
- **Source**: FCSO (First Coast Service Options) — 2026 schedules downloadable (PDF/Excel/TXT) + contractor-priced fees + anesthesia CFs: medicare.fcso.com/fees
- **Sample Loc 03 rates (Jan 2026, PAR / Non-PAR / LC)** [V]:
  - G0011 $30.64 / $29.11 / $33.48 · G0017 $220.57 / $209.54 / $240.97 · G0101 $40.12 [Loc99] · G0104 $209.57 / $199.09 / $228.95 · G0105 $375.49 / $356.72 / $410.23 · G0121 $375.99 / $357.19 / $410.77 · Q0091 $47.33 / $44.96 / $51.70 · A2001 $128.91 / $122.46 / $140.83 · Q4101-Q4405 skin subs $128.91 (Loc 03) / $122.26 (Loc 99)
  - (Full tables: FCSO downloads — rate-file pipeline to load, below)

## 2. FL MEDICARE ADVANTAGE PAYER LANDSCAPE — CONFIRMED (founder 08-02 — ONLY TWO MA payers in scope)
**Full FL MA carrier roster (2026, ~21 companies / 611 plans, 3.1M beneficiaries, 60% penetration) [V]**: Humana (85 plans) · UnitedHealthcare (75) · Aetna (50) · Florida Blue (45) · WellCare/Centene (40) · Devoted Health (33, 5-star) · Cigna HealthSpring (30) · CarePlus (Humana sub, 20) · Optimum HealthCare · HealthSun · Freedom Health · Simply Healthcare · Ultimate Health · Health First · Leon Health · **Solis** · **Oscar** · others per CMS/medicare.gov plan compare.
**OUR SCOPE (Medisun + NURA clients) — ONLY TWO, per founder 08-02**:
- **SOLIS HEALTH PLANS = FULL RISK (PMPM/capitation)** — Healthy Living (HMO): $0 premium · $0 deductible · MOOP $2,900 · $0 PCP/specialist · inpatient $50 d1-5 · service area Orange/Osceola/Seminole [V] · Guardian (D-SNP) MOOP $3,400 · Wellness MOOP ~$2,500
- **OSCAR HEALTH = FEE FOR SERVICE WITH UPSIDE** — lesser-of billed-charges-or-schedule · %CMS IPPS/OPPS · fallback % billed charges · **Quality Incentive Programs = the upside** (Exhibit 5.1.2) [V] — upside mechanics contract-specific [U]
- **No other commercial MA payers in scope. (Traditional Medicare FFS + FL Medicaid are separate lanes.)**

## 3. MEDICARE PHYSICIAN FEE SCHEDULE — FL 2026 [V]

## 4. MEDISUN CONTRACT — PMPM STRUCTURE [V — founder 08-02]
**PMPM = $360 total** · **$60 = nutrition + OTC benefit** · **$300 = the practice (clinical services)**
- Practice revenue math: $300 PMPM × members (e.g., 285 pts = **$85,500/mo** practice PMPM)
- $60 lane = nutrition/OTC benefit fulfillment (tracked separately — benefit spend, not practice revenue)
- Full-risk structure: Solis PMPM is the capitated revenue; utilization/cost discipline = margin (RAF 1.27; MA contract per credentialing docs [U] for upside/QIP mechanics)
- The RCM + fee-schedule lanes (skill payer-fee-schedule-ops) manage against THIS structure

## 5. RATE-FILE PIPELINE (process — skill payer-fee-schedule-ops)
1. **Load**: FCSO 2026 PDF/Excel/TXT → parse → normalized table (code · mod · locality · PAR/Non-PAR/LC · eff date) → Qdrant + vault
2. **Align**: OpenEMR fee sheets (CPT/ICD10 + fee) ↔ payer tables (charge master sync — RCM directive 05943ac5)
3. **Monitor**: annual updates (Jan), mid-year changes, contractor-priced fee changes → alert lane (monthly rate-watch cron)
4. **Contracts**: MA plan structures (Solis/Oscar) tracked per client — PMPM vs FFS-with-upside + quality upside mechanics
5. **Report**: clean-claim rate, denial patterns per payer, rate-change impact on A/R (KPI lane)

## Organization
Vault: this file (SEC/Medisun section) · Qdrant: indexed (nura-docs) · Paperclip: RCM directive 05943ac5 (Medisun client lane) · Perfex: pending token (client task mirror)
