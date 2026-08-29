#!/usr/bin/env python3
"""NURA RAF V24-vs-V28 money-delta analysis on the real Solis MRA export.

HONEST BOUNDARY (stated up front): the MRA flat-file gives HCC number + weight + MRA + version,
NOT the raw ICD-10 codes. The true V28 RAF needs ICD-10 (V28 renumbered most HCCs vs V24). So
this computes what IS provable from the export alone:
  - For each HCC that appears under BOTH versions in the export, the export's own HCC Weight
    (V24 vs V28) — the empirical per-HCC weight drift the ~11% map represents.
  - Sum the (V28-weight - V24-weight) delta across the V24-scored member-condition rows (the ones
    that were scored under the pre-V28 model), and annualize with the Medisun PMPM.
This is a DIRECTIONAL/magnitude finding, not a certified claim — the gap between them is the
real question (did the V24-scored members get a lower RAF than V28 would have given).
"""
import csv, collections, statistics

SRC = "/tmp/solis-reports/MRA_Open_Cond_MRAExportFlatFile.csv"
PMPM = 360.0   # Medisun MA full-risk PMPM (memory)

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig", newline="")))
def f(x):
    try: return float(x)
    except: return 0.0
def version(r): return (r.get("MRA Version") or "").strip()
def hcc(r): return (r.get("HCC") or "").strip()
def wt(r): return f(r.get("HCC Weight"))
def mra(r): return f(r.get("MRA"))

# 1. Per-HCC weight by version (empirical, from the export's own HCC Weight column)
hv = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    hv[hcc(r)][version(r)].append(wt(r))

print("=== HCCs appearing under BOTH V24 and V28 (the map-drift cores) ===")
drift = []
for h, vers in sorted(hv.items()):
    if "CMS-HCC v24" in vers and "CMS-HCC v28" in vers:
        w24 = statistics.mean(vers["CMS-HCC v24"])
        w28 = statistics.mean(vers["CMS-HCC v28"])
        drift.append((h, w24, w28, w28 - w24))
        print(f"  HCC {h:>3}: V24 w={w24:.3f}  V28 w={w28:.3f}  delta={w28-w24:+.3f}")

# 2. The money delta: for the V24-scored rows, what's the per-row weight delta if V28 weights applied
v24rows = [r for r in rows if version(r) == "CMS-HCC v24"]
w24_to_w28 = {h: d for h,_,_,d in drift}
sum_delta = sum(w24_to_w28.get(hcc(r), 0.0) for r in v24rows if hcc(r) in w24_to_w28)
n_affected = sum(1 for r in v24rows if hcc(r) in w24_to_w28)
print(f"\n=== MONEY DELTA (V24-scored rows restated under V28) ===")
print(f"V24-scored rows total: {len(v24rows)} | rows with a measurable V28 weight: {n_affected}")
print(f"Sum of (V28 wt - V24 wt) across those rows: {sum_delta:+.4f} (partial — only HCCs in both)")
# 3. Annualized PMPM impact if this delta maps to per-member RAF
print(f"\nMedisun PMPM ${PMPM:.0f} -> annualized per member (12 mo): ${PMPM*12:,.0f}")
print(f"NOTE: this is a magnitude/order-of-magnitude direction check, not a certified figure.")

# 4. Members who are ENTIRELY under V24 (never V28) — the highest-risk cohort
mem_by_ver = collections.defaultdict(set)
for r in rows:
    mem_by_ver[version(r)].add(r.get("MemberNbr"))
v24_only = mem_by_ver.get("CMS-HCC v24", set()) - mem_by_ver.get("CMS-HCC v28", set())
print(f"\nMembers scored ONLY under V24 (never V28): {len(v24_only)} of {len(mem_by_ver.get('CMS-HCC v24',set()))} V24-scored")
