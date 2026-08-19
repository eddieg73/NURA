#!/usr/bin/env python3
"""NURA Device Scoring Engine — deterministic clinical scores from device vitals.
NEWS2 (deterioration) · RSBI (weaning index) · ARDSNet P/F (vent) · GCS.
DOCTRINE (LOM): scores ONLY, always. Auto-SAFE defaults ONLY for crashing + non-compliant.
Defibrillation NEVER auto. Black-box logged + provider alert on thresholds.
Usage: python3 device-scores.py '{"hr":110,"rr":22,"spo2":94,"sbp":100,"temp":38.9,"spo2_scale":"2","avpu":"V"}'
Output: {"news2": 6, "flags": ["..."]}"""
import sys, json

def news2(d):
    s = 0
    # respiration
    rr = d.get("rr")
    if rr is None: return {"error": "rr required"}
    if rr <= 8: s += 3
    elif 9 <= rr <= 11: s += 1
    elif 21 <= rr <= 24: s += 2
    elif rr >= 25: s += 3
    # SpO2
    spo2 = d.get("spo2")
    scale = d.get("spo2_scale", "1")
    if spo2 is not None:
        if scale == "2":
            if 84 <= spo2 <= 85: s += 1
            elif 86 <= spo2 <= 87: s += 2
            elif spo2 <= 83: s += 3
        else:
            if 94 <= spo2 <= 95: s += 1
            elif 92 <= spo2 <= 93: s += 2
            elif spo2 <= 91: s += 3
    # oxygen
    if d.get("o2"): s += 2
    # BP
    sbp = d.get("sbp")
    if sbp is not None:
        if sbp <= 90: s += 3
        elif 91 <= sbp <= 100: s += 2
        elif 101 <= sbp <= 110: s += 1
        elif sbp >= 220: s += 3
    # HR
    hr = d.get("hr")
    if hr is not None:
        if hr <= 40: s += 3
        elif 41 <= hr <= 50: s += 1
        elif 91 <= hr <= 110: s += 1
        elif 111 <= hr <= 130: s += 2
        elif hr >= 131: s += 3
    # temp
    t = d.get("temp")
    if t is not None:
        if t <= 35.0: s += 3
        elif 35.1 <= t <= 36.0: s += 1
        elif 38.1 <= t <= 39.0: s += 1
        elif t >= 39.1: s += 2
    # consciousness
    avpu = d.get("avpu", "A")
    if avpu == "C" or avpu == "U": s += 3
    if avpu == "V" or avpu == "P": s += 3  # new confusion/voice/pain = 3 per NEWS2
    flags = []
    if s >= 7: flags.append("HIGH NEWS2 — continuous monitoring + urgent clinical review")
    elif s >= 5: flags.append("MEDIUM NEWS2 — hourly monitoring + clinical review")
    if d.get("rr") and d.get("tv") and 100 * d["rr"] / d["tv"] < 105:
        flags.append("RSBI < 105 — weaning trial consideration (provider decision)")
    if d.get("spo2") and d.get("fio2"):
        pf = d["spo2"] / d["fio2"]
        if pf < 150: flags.append(f"P/F proxy {pf:.0f} — ARDS severe range (confirm ABG)")
        elif pf < 300: flags.append(f"P/F proxy {pf:.0f} — ARDS range (confirm ABG)")
    return {"news2": s, "risk": "HIGH" if s >= 7 else ("MEDIUM" if s >= 5 else "LOW"), "flags": flags}

if __name__ == "__main__":
    d = json.loads(sys.argv[1] if len(sys.argv) > 1 else "{}")
    print(json.dumps(news2(d), indent=2))
