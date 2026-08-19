#!/usr/bin/env python3
"""Telemetry CDS engine — NEWS2-based deterioration scoring + device-specific red flags.
Evidence: NEWS2 (RCP London, NHS standard, 2017) for physiologic scoring; device flags from
manufacturer/guideline reference values (VALIDATE against your device's spec before production).
Output: interpretation narrative + score + red flags — DECISION SUPPORT ONLY, provider reviews.
"""
import json, sys, time
from pathlib import Path

# NEWS2 score components (adult): [value, score] boundaries per RCP chart
def news2_score(hr, rr, spo2, sbp, temp_c, conscious=True, on_oxygen=False):
    """Returns NEWS2 (0-20) per Royal College of Physicians chart. None = missing (0)."""
    s = 0; detail = {}
    # Respiration rate (bpm)
    if rr is not None:
        v = 3 if rr <= 8 else 1 if rr <= 11 else 0 if rr <= 20 else 2 if rr <= 24 else 3
        detail["RR"] = v; s += v
    # SpO2 scale 1 (no oxygen): >=96:0, 94-95:1, 92-93:2, <=91:3
    if spo2 is not None and not on_oxygen:
        v = 0 if spo2 >= 96 else 1 if spo2 >= 94 else 2 if spo2 >= 92 else 3
        detail["SpO2"] = v; s += v
    # SpO2 scale 2 (on oxygen): >=97:0, 95-96:1, 93-94:2, <=92:3
    if spo2 is not None and on_oxygen:
        v = 0 if spo2 >= 97 else 1 if spo2 >= 95 else 2 if spo2 >= 93 else 3
        detail["SpO2"] = v; s += v
    # Air or oxygen: +2 if on oxygen
    if on_oxygen:
        detail["O2"] = 2; s += 2
    # HR (bpm): <=40:3, 41-50:1, 51-90:0, 91-110:1, 111-130:2, >=131:3
    if hr is not None:
        v = 3 if hr <= 40 else 1 if hr <= 50 else 0 if hr <= 90 else 1 if hr <= 110 else 2 if hr <= 130 else 3
        detail["HR"] = v; s += v
    # SBP (mmHg): <=90:3, 91-100:2, 101-110:1, 111-219:0, >=220:3
    if sbp is not None:
        v = 3 if sbp <= 90 else 2 if sbp <= 100 else 1 if sbp <= 110 else 0 if sbp <= 219 else 3
        detail["SBP"] = v; s += v
    # Temperature (C): <=35:3, 35.1-36:1, 36.1-38:0, 38.1-39:1, >=39.1:2
    if temp_c is not None:
        v = 3 if temp_c <= 35 else 1 if temp_c <= 36 else 0 if temp_c <= 38 else 1 if temp_c <= 39 else 2
        detail["Temp"] = v; s += v
    # Consciousness: +3 if new confusion/AVPU != A
    if not conscious:
        detail["Neuro"] = 3; s += 3
    return s, detail

def device_flags(dev):
    """Device-type specific red flags (reference thresholds — validate per device spec)."""
    flags = []
    if dev.get("type") == "ventilator":
        if dev.get("etco2") is not None and dev["etco2"] > 50: flags.append("EtCO2 elevated >50 — hypoventilation risk")
        if dev.get("etco2") is not None and dev["etco2"] < 25: flags.append("EtCO2 low <25 — hyperventilation/perfusion concern")
        if dev.get("peak_pressure") is not None and dev["peak_pressure"] > 35: flags.append("Peak pressure >35 cmH2O — compliance/airway concern")
        if dev.get("vte") is not None and dev["vte"] < 6: flags.append("Vt <6 mL/kg IBW — hypoventilation risk")
    if dev.get("type") == "monitor":
        if dev.get("st_change") is not None and abs(dev["st_change"]) >= 2: flags.append(f"ST deviation {dev['st_change']} mm — ischemia review needed")
        if dev.get("arrhythmia") in ("vt", "vf", "asystole", "svt_hr_gt_180"): flags.append(f"Arrhythmia flag: {dev['arrhythmia']}")
        if dev.get("spo2") is not None and dev["spo2"] < 88: flags.append("SpO2 <88% — severe hypoxemia")
    if dev.get("type") == "cgm":
        if dev.get("glucose") is not None and dev["glucose"] < 70: flags.append("Glucose <70 mg/dL — hypoglycemia alert")
        if dev.get("glucose") is not None and dev["glucose"] > 250: flags.append("Glucose >250 mg/dL — hyperglycemia alert")
        if dev.get("rate_of_change") is not None and abs(dev["rate_of_change"]) >= 2: flags.append(f"Glucose ROC {dev['rate_of_change']} mg/dL/min — rapid change")
    return flags

def interpret(vitals, devices):
    score, detail = news2_score(vitals.get("hr"), vitals.get("rr"), vitals.get("spo2"),
                                vitals.get("sbp"), vitals.get("temp_c"), vitals.get("conscious", True),
                                vitals.get("on_oxygen", False))
    flags = []
    for d in devices:
        flags += device_flags(d)
    if score >= 7: level = "HIGH — urgent clinical review (NEWS2 >=7 escalation threshold)"
    elif score >= 5: level = "MEDIUM-HIGH — frequent monitoring + review (NEWS2 5-6)"
    elif score >= 3: level = "LOW-MEDIUM — increased monitoring (NEWS2 3-4)"
    else: level = "LOW — routine monitoring"
    return {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "news2": score, "news2_detail": detail, "level": level,
            "device_flags": flags,
            "interpretation": (f"NEWS2 {score} ({level}). " +
                               ("Device red flags: " + "; ".join(flags) + ". " if flags else "") +
                               "Decision support only — provider review required before any action."),
            "provider_gate": True}

if __name__ == "__main__":
    case = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {
        "vitals": {"hr": 118, "rr": 26, "spo2": 89, "sbp": 96, "temp_c": 38.4, "conscious": True, "on_oxygen": True},
        "devices": [{"type": "monitor", "spo2": 89, "st_change": 1.5, "arrhythmia": "svt_hr_gt_180"},
                    {"type": "ventilator", "etco2": 48, "peak_pressure": 32}]}
    out = interpret(case["vitals"], case["devices"])
    print(json.dumps(out, indent=1))
    Path("/opt/data/profiles/nura/data/telemetry-cds.json").write_text(json.dumps(out, indent=1))
