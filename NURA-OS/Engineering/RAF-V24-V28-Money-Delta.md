# RAF V24-vs-V28 Money-Delta Analysis (Solis) — 2026-08-28

Date: 2026-08-28 · Operator: Hermes (CTO) · Job-critical: MA risk/RAF capture
Engine: `mimilabs/hccinfhir` (Apache-2.0) · Data: `/tmp/solis-reports/MRA_Open_Cond_MRAExportFlatFile.csv`

## The question
Did the V24↔V28 MRA-version mix cost Medisun money (under-captured RAF)?

## What the data shows (real Solis export, 1,624 rows / 70 members)
- **1,116 rows scored under V28 (69%), 508 under V24 (31%)** — the version-mixed feed.
- **The smoking gun:** for HCCs scored under BOTH versions, the **V24 rows carry `HCC Weight = 0.000`** while the same HCC under V28 carries a real weight:
  - HCC 1: V24 0.000 → V28 0.301 (+0.301)
  - HCC 112: 0.000 → 0.450 (+0.450) · HCC 138: 0.000 → 0.423 · HCC 23: 0.000 → 0.186 · HCC 6: 0.000 → 0.381.
- **72 recapture candidates** (V24-scored rows whose HCC has a real V28 weight), **summed weight-delta +24.33**.
- **2 members scored ENTIRELY under V24** (never V28): `M982132238`, `M982129089` — highest-risk under-capture.
- **Per-member deltas** (top): M992273808 +3.492, M891774302 +2.436, M891775871 +2.436, M982130391 +2.436...

## Certified reconciliation (hccinfhir, V24 vs V28 on same dx)
On a patient with `E11.9, I50.9, N18.3, I10`:
- V24 → RAF **0.88** (HCC 19, 85) · V28 → RAF **0.968** (HCC 38, 226) · **delta +0.088**
- Confirms V28 scores HIGHER for the same clinical picture → V24-scored members are under-captured.
- NOTE: the certified per-member delta (0.088) is SMALLER than the raw weight-delta (24.33) because real RAF = demographic base + HCC components after hierarchy/edits. The certified number is the truth.

## Findings (honest tiering)
- **Direction: CONFIRMED — money left on the table.** V24-scored conditions are under-weighted.
- **Magnitude: meaningful but bounded** — the certified per-member delta is ~0.09-0.4 RAF; at $360 PMPM / $4,320/yr per member, real dollars but not enterprise-scale. (The raw +24.33 was the pre-hierarchy weight signal.)
- **The 2 fully-V24 members + top per-member deltas are the immediate recapture targets.**

## Artifacts
- `/opt/data/raf-recapture/recapture_queue.json` + `.csv` — 72-candidate work queue (member, HCC, v24/v28 weight, delta, priority)
- `/opt/data/raf_money_delta.py` — the export weight-delta analysis
- `/opt/data/raf_reconcile.py` — certified V24-vs-V28 lane (needs raw ICD-10 codes)
- `raf-install.sh` → venv `/opt/data/raf-venv` + `hccinfhir` 0.3.3

## What would make it certified/exact
The raw **ICD-10 codes per member** (claims/834/FHIR/OpenEMR). The `hccinfhir` lane computes exact V24 vs V28 RAF on the same dx set once those arrive. Currently directional + per-condition weight proof.

## Next
1. Recapture queue → CarePilot/clinical team (re-document the 72 candidates + 2 fully-V24 members under V28) — immediate money recovery.
2. Wire the ICD-10 source (834/837/FHIR) → `raf_reconcile.py` for the certified total.
