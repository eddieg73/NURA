#!/usr/bin/env python3
"""NURA RAF recapture work-queue builder.

From the real Solis MRA export, identifies the conditions/members that are being UNDER-SCORED
because they were scored under CMS-HCC v24 (where the export carries HCC Weight = 0.000) but the
same condition earns a real, non-zero weight under V28. Those are the recapture candidates — the
money-recovery queue.

Also flags members scored ENTIRELY under V24 (never V28) — the highest-risk under-capture cohort.

Output: a JSON work queue + a CSV the CarePilot/clinical team can triage. Evidence-first: every
row carries the member, HCC, V24 weight (0.000), V28 weight, and the delta.
"""
import csv, collections, json, statistics, datetime, os

SRC = "/tmp/solis-reports/MRA_Open_Cond_MRAExportFlatFile.csv"
OUT_DIR = "/opt/data/raf-recapture"
os.makedirs(OUT_DIR, exist_ok=True)

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig", newline="")))
def f(x):
    try: return float(x)
    except: return 0.0
def version(r): return (r.get("MRA Version") or "").strip()
def hcc(r): return (r.get("HCC") or "").strip()
def wt(r): return f(r.get("HCC Weight"))

# per-HCC weight by version (from the export's own weights)
hv = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    hv[hcc(r)][version(r)].append(wt(r))
# map HCC -> V28 weight (mean) and V24 weight (mean), only for HCCs visible in both
w28 = {h: statistics.mean(v["CMS-HCC v28"]) for h,v in hv.items() if "CMS-HCC v28" in v}
w24 = {h: statistics.mean(v["CMS-HCC v24"]) for h,v in hv.items() if "CMS-HCC v24" in v}

# --- Recapture candidates: a V24-scored row whose HCC has a real V28 weight (>0) ---
recapture = []
for r in rows:
    if version(r) != "CMS-HCC v24":
        continue
    h = hcc(r)
    if h not in w28 or w28[h] <= 0:
        continue
    delta = w28[h] - w24.get(h, 0.0)
    if delta <= 0:
        continue
    recapture.append({
        "member": (r.get("MemberNbr") or "").strip(),
        "member_name": (r.get("Patient Name") or "").strip(),
        "hcc": h,
        "hcc_desc": (r.get("HCC Description") or "").strip(),
        "v24_weight": round(w24.get(h, 0.0), 4),
        "v28_weight": round(w28[h], 4),
        "weight_delta": round(delta, 4),
        "mra_version": "CMS-HCC v24",   # the error: scored under the pre-V28 model
        "action": "RECAPTURE",           # re-document/re-code at V28 weight
        "priority": "HIGH" if delta >= 0.3 else ("MEDIUM" if delta >= 0.15 else "LOW"),
    })

# --- Fully-V24 members (never V28) ---
mem_vers = collections.defaultdict(set)
for r in rows:
    mem_vers[r.get("MemberNbr")].add(version(r))
fully_v24 = [m for m,v in mem_vers.items() if v == {"CMS-HCC v24"}]

# --- Aggregate per member (total delta) ---
by_member = collections.defaultdict(float)
for x in recapture:
    by_member[x["member"]] += x["weight_delta"]

queue = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source": SRC,
    "total_rows": len(rows),
    "v24_scored_rows": sum(1 for r in rows if version(r)=="CMS-HCC v24"),
    "recapture_candidates": recapture,
    "recapture_count": len(recapture),
    "sum_weight_delta": round(sum(x["weight_delta"] for x in recapture), 4),
    "fully_v24_members": fully_v24,
    "per_member_delta": [{"member":m, "delta":round(d,4)} for m,d in sorted(by_member.items(), key=lambda x:-x[1])],
}

with open(os.path.join(OUT_DIR,"recapture_queue.json"),"w") as fp:
    json.dump(queue, fp, indent=2)

# CSV for the team
with open(os.path.join(OUT_DIR,"recapture_queue.csv"),"w",newline="") as fp:
    w = csv.DictWriter(fp, fieldnames=["member","member_name","hcc","hcc_desc","v24_weight","v28_weight","weight_delta","mra_version","action","priority"])
    w.writeheader()
    for x in recapture:
        w.writerow(x)

print(f"=== RAF RECAPTURE QUEUE ===")
print(f"V24-scored rows: {queue['v24_scored_rows']} | recapture candidates: {len(recapture)}")
print(f"sum weight-delta (V28 - V24) across candidates: {queue['sum_weight_delta']:+.4f}")
print(f"fully-V24 members (never V28): {len(fully_v24)} -> {fully_v24}")
print(f"per-member delta (top): {queue['per_member_delta'][:6]}")
print(f"\nwrote: {OUT_DIR}/recapture_queue.json + .csv")
