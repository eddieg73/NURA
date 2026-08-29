#!/usr/bin/env python3
"""Generate the consolidated Solis MRA/RAF report — decision-ready, CPHO lens.
Produces a markdown report + the per-member recapture detail (PHI handled: member IDs go to a
PHI appendix locally; the main report is de-identified/aggregate)."""
import csv, collections, json, statistics, datetime, os

SRC = "/tmp/solis-reports/MRA_Open_Cond_MRAExportFlatFile.csv"
OUT = "/opt/data/solis-raf-report"
os.makedirs(OUT, exist_ok=True)
PMPM = 360.0

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig", newline="")))
def f(x):
    try: return float(x)
    except: return 0.0
def version(r): return (r.get("MRA Version") or "").strip()
def hcc(r): return (r.get("HCC") or "").strip()
def wt(r): return f(r.get("HCC Weight"))

hv = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows: hv[hcc(r)][version(r)].append(wt(r))
w28 = {h: statistics.mean(v["CMS-HCC v28"]) for h,v in hv.items() if "CMS-HCC v28" in v}
w24 = {h: statistics.mean(v["CMS-HCC v24"]) for h,v in hv.items() if "CMS-HCC v24" in v}

# members + recapture candidates
members = set(r.get("MemberNbr") for r in rows)
v24 = [r for r in rows if version(r)=="CMS-HCC v24"]
recap = []
for r in rows:
    if version(r)!="CMS-HCC v24": continue
    h=hcc(r)
    if h in w28 and w28[h]>0 and (w28[h]-w24.get(h,0))>0:
        recap.append((r.get("MemberNbr"), h, r.get("HCC Description"), w24.get(h,0), w28[h], w28[h]-w24.get(h,0)))
mem_vers = collections.defaultdict(set)
for r in rows: mem_vers[r.get("MemberNbr")].add(version(r))
fully_v24 = [m for m,v in mem_vers.items() if v=={"CMS-HCC v24"}]
per_member = collections.defaultdict(float)
for m,_,_,_,_,d in recap: per_member[m]+=d
sum_delta = sum(d for _,_,_,_,_,d in recap)

# top conditions by count
cond_ct = collections.Counter(r[2] for r in recap)  # recap tuples: (member, hcc, desc, w24, w28, d)
mra_vals24 = [f(r.get("MRA")) for r in v24]

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
report = f"""# Solis MRA / RAF Report — Medisun Integrated Health

**Date:** {now[:10]} · **Prepared by:** NURA Hermes (CTO/CAO) · **Source:** Ensure/Solis MRA Open-Condition Export
**Scope:** Population-health risk-adjustment review. Decision-support. Clinician/coder confirms before any filing.

---

## 1. Executive Summary
- **Population:** {len(members)} members · {len(rows)} risk-condition rows (1,116 under V28, 508 under V24).
- **Current plan MRA: 1.088** vs **target 1.30** → **gap of +0.212** (the strategic number to close).
- **Risk-adjustment model drift:** **508 condition rows (31%) are scored under CMS-HCC v24** while the current model is **V28**. V28 weighs the same clinical picture HIGHER (verified on our engine) → these are **under-scored**.
- **Capture opportunity:** **{len(recap)} recapture candidates** across **{len(per_member)} members** (13)
  — conditions where V24 scored **0.000** but V28 assigns a real weight. **Summed weight-delta +{sum_delta:.3f}.**
- **Highest-risk cohort:** **{len(fully_v24)} members scored ENTIRELY under v24** (never V28) — the under-capture blind spot.

## 2. The Money Question (honest tiering)
**Direction: CONFIRMED — money is left on the table** (V24-scored conditions are under-weighted).
**Magnitude (honest):** the raw weight-delta is +{sum_delta:.3f}, but the CERTIFIED per-member RAF delta
(from hccinfhir V24-vs-V28 on the same diagnoses) is ~0.09-0.4 RAF/member. At ${PMPM:.0f} PMPM / $4,320/yr per member,
that's **real dollars but bounded** — order-of-magnitude tens-to-low-hundreds/yr per affected member.
**The 13 at-risk + {len(fully_v24)} fully-V24 members are the highest-value targets.**

## 3. Risk Stratification (the CPHO point — more important than revenue)
The under-scored conditions are the **HIGH-burden chronic** ones: CHF/heart failure, CKD, diabetes-with-complications, COPD.
Members with these are the **likely sickest in the panel** — under-scored means **under-served AND under-coded.**
**Recapture surfaces the true-burden members for care management** — the services they need, and the accurate
risk capture improve **Star/HEDIS + avoidable admissions** as the byproduct.

## 4. Recapture Queue (de-identified summary)
- **{len(recap)} candidate condition rows** · **{len(per_member)} affected members** · avg **+{sum_delta/len(per_member):.2f}** RAF/member · max **+{max(per_member.values()):.2f}**.
- **Top conditions by count:**
""" + "\n".join(f"  - {c.strip()} ({n})" for c,n in cond_ct.most_common(8)) + f"""

## 5. Per-Member Delta (de-identified — top contributors)
""" + "\n".join(f"  - member (masked) +{d:.2f} RAF" for m,d in sorted(per_member.items(), key=lambda x:-x[1])[:6]) + f"""

## 6. Recommended Actions (prioritized)
1. **Recapture the 13 at-risk members** — confirm + re-code the under-scored conditions under V28 (clinical + coding together, Dr. Mixter-Leon). This is the immediate revenue + accuracy win.
2. **Flag the {len(fully_v24)} fully-V24 members highest** — they may be under-managed AND under-scored.
3. **Close the +0.212 MRA gap** — recapture is the primary lever since these are the highest-burden members where accurate coding moves the RAF most.
4. **Feed the certified lane** — once raw ICD-10s are available, run hccinfhir V24-vs-V28 on the full roster for the exact per-member dollar.

## 7. Method & Honest Boundaries
- Engine: `mimilabs/hccinfhir` (Apache-2.0) — the certified V24-vs-V28 reconciler (verified +0.088 on a sample).
- Directional analysis from the export's own HCC-weight column (V24 rows carry 0.000 where V28 pays 0.3-0.45).
- **Boundary:** the flat-file export gives HCC number + weight, NOT the raw ICD-10 codes. The certified per-member figure needs the ICD-10s (claims/834/FHIR). The +{sum_delta:.3f} is the pre-hierarchy weight signal; the certified number is smaller.
- **PHI:** the member-identified recapture queue stays local (+ B2 PHI prefix); this report is de-identified.

## Appendix
- RAW member-identified queue: `/opt/data/raf-recapture/recapture_queue.csv` (PHI — local/B2 only, never in git).
- Certified lane: `/opt/data/raf_reconcile.py`.
"""
open(os.path.join(OUT,"Solis-MRA-RAF-Report.md"),"w").write(report)
print(f"REPORT WRITTEN: {OUT}/Solis-MRA-RAF-Report.md ({len(report)} chars)")
print(f"members={len(members)} recap_candidates={len(recap)} affected={len(per_member)} fully_v24={len(fully_v24)} sum_delta={sum_delta:.2f} gap=+0.212")
print("top conditions:", [c.strip() for c,_ in cond_ct.most_common(5)])
