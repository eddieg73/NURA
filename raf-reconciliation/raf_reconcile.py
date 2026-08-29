#!/usr/bin/env python3
"""NURA RAF V24-vs-V28 reconciliation lane (certified path) via hccinfhir.

Once the raw ICD-10 codes for the Solis roster are provided (claims/834/FHIR/OpenEMR), this
computes each member's RAF under BOTH CMS-HCC Model V24 and V28 on the SAME diagnosis set, and
reports the per-member + total delta. That's the certified dollar figure.

Usage:
  python3 raf_reconcile.py --icd 'I50.9,I10,N18.3' --age 67 --sex F
  python3 raf_reconcile.py --file members.json   # [{member, icd:[], age, sex}]
"""
import argparse, json, os, sys

sys.path.insert(0, "/opt/data/raf-venv/lib/python3.11/site-packages")

def safe_import():
    from hccinfhir import HCCInFHIR, Demographics  # noqa
    return HCCInFHIR, Demographics

def score_one(HCCInFHIR, Demographics, icds, age, sex):
    """Compute RAF under V24 and V28 for the SAME diagnosis set."""
    out = {}
    for model in ["CMS-HCC Model V24", "CMS-HCC Model V28"]:
        proc = HCCInFHIR(model_name=model)
        demo = Demographics(age=age, sex=sex)
        res = proc.calculate_from_diagnosis(icds, demo)
        out[model] = {
            "risk_score": float(getattr(res, "risk_score", 0.0)),
            "hccs": getattr(res, "hcc_list", []),
        }
    d = out["CMS-HCC Model V28"]["risk_score"] - out["CMS-HCC Model V24"]["risk_score"]
    return {"v24": out["CMS-HCC Model V24"], "v28": out["CMS-HCC Model V28"], "delta": d}

def main():
    HCCInFHIR, Demographics = safe_import()
    ap = argparse.ArgumentParser()
    ap.add_argument("--icd", help="comma-separated ICD-10 codes")
    ap.add_argument("--age", type=int, default=67)
    ap.add_argument("--sex", default="F")
    ap.add_argument("--file", help="members.json [{member,icd,age,sex}]")
    a = ap.parse_args()

    if a.icd:
        icds = [c.strip() for c in a.icd.split(",") if c.strip()]
        r = score_one(HCCInFHIR, Demographics, icds, a.age, a.sex)
        print(json.dumps(r, indent=2))
    elif a.file:
        members = json.load(open(a.file))
        total_delta, per = 0.0, []
        for m in members:
            r = score_one(HCCInFHIR, Demographics, m.get("icd",[]), m.get("age",67), m.get("sex","F"))
            per.append({"member": m.get("member"), **r})
            total_delta += r["delta"]
        print(json.dumps({"members": per, "total_v28_minus_v24_delta": round(total_delta,4)}, indent=2))
    else:
        print("pass --icd 'I50.9,...' or --file members.json")

if __name__ == "__main__":
    main()
