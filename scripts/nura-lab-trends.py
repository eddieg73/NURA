#!/usr/bin/env python3
"""NURA Laboratory Intelligence — the lab-work engine (provider-approved).
Inputs: patient (age/sex/PMH) + SERIAL lab sets (timestamps + values).
Outputs: per-analyte trends (delta, % change, direction), the classifications
(normal/abnormal/critical per the skill's discipline), the pattern read
(rising/falling/fresh), and the PMH-aware recommendations (Med42).
DOCTRINE: decision-support only — Eddie (PA-C) makes the final approval.
Usage: python3 nura-lab-trends.py labs.json
labs.json = {"patient": {"age": 68, "sex": "M", "pmh": ["CKD3", "DM2"]},
             "results": [{"ts": "2026-08-15T08:00", "labs": {"Cr": 1.2, "K": 4.0, "Hgb": 12.1, "Glucose": 150}},
                         {"ts": "2026-08-17T08:00", "labs": {"Cr": 1.8, "K": 5.4, "Hgb": 10.9, "Glucose": 205}}]}
"""
import sys, json, urllib.request

REF = {  # adult reference ranges — flags only; the provider interprets
    "WBC": (4.0, 11.0, "10^9/L"), "Hgb": (13.5, 17.5, "g/dL"), "PLT": (150, 400, "10^9/L"),
    "Na": (135, 145, "mmol/L"), "K": (3.5, 5.0, "mmol/L"), "Cr": (0.6, 1.3, "mg/dL"),
    "BUN": (7, 20, "mg/dL"), "Glucose": (70, 110, "mg/dL"), "Lactate": (0.5, 2.0, "mmol/L"),
    "CRP": (0, 5, "mg/L"), "AST": (5, 40, "U/L"), "ALT": (5, 40, "U/L"),
}
CRIT = {  # the critical thresholds (per-lab overrides win in the provider's hands)
    "K": ((3.0, 6.0), "critical"), "Na": ((120, 160), "critical"),
    "Glucose": ((50, 400), "critical"), "Lactate": (None, (4.0,)),
}

def classify(name, v):
    r = REF.get(name)
    if not r:
        return "indeterminate"
    lo, hi, unit = r
    crit = CRIT.get(name)
    if crit and crit[0] and v < crit[0][0]:
        return "critical-low"
    if crit and crit[0] and v > crit[0][1]:
        return "critical-high"
    if v < lo:
        return "abnormal-low"
    if v > hi:
        return "abnormal-high"
    return "normal"

def analyze(case):
    patient = case.get("patient", {})
    results = sorted(case.get("results", []), key=lambda r: r["ts"])
    analytes = set()
    for r in results:
        analytes.update(r["labs"].keys())
    trends = {}
    for a in sorted(analytes):
        series = [(r["ts"], r["labs"][a]) for r in results if a in r["labs"] and isinstance(r["labs"][a], (int, float))]
        if len(series) < 2:
            trends[a] = {"values": series, "trend": "insufficient-points (need ≥2 draws)"}
            continue
        first, last = series[0][1], series[-1][1]
        delta = round(last - first, 2)
        pct = round(delta / first * 100, 1) if first else None
        direction = "rising" if delta > 0 else ("falling" if delta < 0 else "stable")
        rate = None
        from datetime import datetime
        t0 = datetime.fromisoformat(series[0][0]); t1 = datetime.fromisoformat(series[-1][0])
        hrs = max((t1 - t0).total_seconds() / 3600, 0.01)
        rate = round(delta / hrs, 3)
        trends[a] = {"values": series, "first": first, "last": last, "delta": delta,
                     "pct_change": pct, "direction": direction, "rate_per_hour": rate,
                     "classification": classify(a, last)}
    payload = {"PATIENT": json.dumps(patient), "SERIAL_LABS": json.dumps(trends, indent=1)}
    prompt = ("You are NURA laboratory intelligence for a licensed PA. Interpret the serial labs WITH the "
              "patient's PMH. For each analyte: the significance of its direction + rate, and the clinical "
              "correlation. Then: the pattern read (what the whole picture suggests) and 3-5 prioritized "
              "RECOMMENDATIONS grounded in the results + the PMH (rechecks, meds to hold, consults, workup). "
              "Never a final diagnosis. End with exactly: 'DRAFT — PROVIDER APPROVAL REQUIRED.'\n"
              "Return plain clinical text, no markdown.\n\n" + json.dumps(payload, indent=1))
    try:
        body = json.dumps({"model": "med42", "prompt": prompt, "stream": False,
                           "options": {"num_predict": 900, "temperature": 0.2}}).encode()
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        r = urllib.request.urlopen(req, timeout=1500)
        interp = json.loads(r.read()).get("response", "").strip()
    except Exception as e:
        interp = f"[interpretation unavailable: {str(e)[:80]}]"
    return {"patient": patient, "trends": trends, "interpretation_and_recommendations": interp}

if __name__ == "__main__":
    case = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
    print(json.dumps(analyze(case), indent=2))
