#!/usr/bin/env python3
"""NURA Radiology Intelligence — the in-house Watson-style radiology assistant.
Deterministic engines (Fleischner, triage) + LLM drafting (OpenRouter/deepseek).
DOCTRINE: decision-support only — the radiologist signs every read. Never a diagnosis engine.
Endpoints: /health · /fleischner · /triage · /extract-findings · /draft-report"""
import json, os, urllib.request, urllib.error
from flask import Flask, request, jsonify

app = Flask(__name__)

def read_env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return ""

# ---------------- Deterministic: Fleischner 2017 (solid/subsolid) ----------------
def fleischner(size_mm: float, nodule_type: str, high_risk: bool = False):
    t = (nodule_type or "solid").lower()
    if t == "solid":
        if size_mm < 6:
            return {"rec": "No routine follow-up", "interval": None,
                    "note": "Optional 12-mo CT in high-risk patients" if high_risk else "Routine screening cadence"}
        if size_mm < 8:
            return {"rec": "CT at 6-12 months, then consider 18-24 months", "interval": "6-12mo"}
        return {"rec": "Consider CT at 3 months, PET/CT, or tissue sampling", "interval": "3mo / PET / biopsy"}
    # subsolid
    if size_mm < 6:
        return {"rec": "No routine follow-up", "interval": None, "note": "Subsolid <6mm — routine cadence"}
    return {"rec": "CT at 6-12 months, then every 2 years for 5 years (if persistent)", "interval": "6-12mo then q2y x5"}

def triage(text: str):
    """Deterministic urgency flags from findings/report text."""
    urgent = ["pneumothorax", "pneumoperitoneum", "free air", "dissection", "tension",
              "large pericardial effusion", "tamponade", "pulmonary embolism", "saddle embolus",
              "intracranial hemorrhage", "epidural hematoma", "bowel obstruction", "volvulus",
              "ischemic bowel", "fracture-dislocation", "acute stroke", "midline shift",
              "septic emboli", "ectopic pregnancy", "ruptured"]
    stat = ["malpositioned tube", "malpositioned line", "endotracheal tube", "hemorrhage",
            "hemothorax", "abscess", "appendicitis", "cholecystitis", "testicular torsion",
            "ovarian torsion", "cord compression"]
    low = text.lower()
    for w in urgent:
        if w in low:
            return {"level": "CRITICAL", "reason": f"keyword: {w}"}
    for w in stat:
        if w in low:
            return {"level": "STAT", "reason": f"keyword: {w}"}
    return {"level": "ROUTINE", "reason": None}

# ---------------- LLM lane (OpenRouter, budget-conscious) ----------------
def llm(system: str, user: str, max_tokens: int = 700):
    key = read_env("OPENROUTER_API_KEY") or read_env("OPENROUTER_OR_KEY")
    if not key:
        return {"error": "no OpenRouter key"}
    body = {"model": "google/gemma-4-31b-it:free",
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "max_tokens": max_tokens, "temperature": 0.2}
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        d = json.loads(r.read())
        return {"text": d["choices"][0]["message"]["content"].strip()}
    except Exception as e:
        return {"error": str(e)[:150]}

# ---------------- Endpoints ----------------
@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "nura-radiology-intelligence", "llm": bool(read_env("OPENROUTER_API_KEY"))})

@app.post("/fleischner")
def fleischner_ep():
    d = request.get_json(force=True) or {}
    try:
        size = float(d.get("size_mm"))
    except (TypeError, ValueError):
        return jsonify({"error": "size_mm required"}), 400
    return jsonify({"input": d, **fleischner(size, d.get("nodule_type"), bool(d.get("high_risk")))})

@app.post("/triage")
def triage_ep():
    d = request.get_json(force=True) or {}
    return jsonify(triage(d.get("text", "")))

@app.post("/extract-findings")
def extract_ep():
    d = request.get_json(force=True) or {}
    text = d.get("report", "")
    if not text:
        return jsonify({"error": "report text required"}), 400
    sys = ("You are a radiology NLP engine. Extract findings as JSON: {findings:[{description,location,severity}], "
           "recommendations:[], follow_up:{interval,modality}, critical_flags:[]}. No commentary, JSON only. "
           "Clinical decision-support only — the radiologist signs the read.")
    out = llm(sys, text)
    if "error" in out:
        return jsonify(out), 502
    try:
        return jsonify({"structured": json.loads(out["text"]), "triage": triage(text)})
    except json.JSONDecodeError:
        return jsonify({"structured_raw": out["text"], "triage": triage(text)})

@app.post("/draft-report")
def draft_ep():
    d = request.get_json(force=True) or {}
    findings = d.get("findings", "")
    indication = d.get("indication", "")
    if not findings:
        return jsonify({"error": "findings required"}), 400
    sys = ("You are a radiology report drafter. Produce a structured draft: INDICATION / TECHNIQUE (placeholder) / "
           "FINDINGS / IMPRESSION (ranked, brief). Flag anything needing the radiologist's attention with [VERIFY]. "
           "Decision-support only; the radiologist reviews and signs.")
    out = llm(sys, f"Indication: {indication}\nFindings dictation: {findings}")
    if "error" in out:
        return jsonify(out), 502
    return jsonify({"draft": out["text"], "triage": triage(findings)})

@app.post("/interpret-study")
def interpret_ep():
    """Vision-AI preliminary read: image render (PNG/JPG) -> structured findings draft.
    DOCTRINE: draft-only, radiologist reviews + signs. Never a final read."""
    d = request.get_json(force=True) or {}
    img = d.get("image_path")
    if not img or not os.path.exists(img):
        return jsonify({"error": "image_path required (Orthanc /rendered PNG or JPEG)"}), 400
    key = read_env("GEMINI_API_KEY")
    if not key:
        return jsonify({"error": "no GEMINI_API_KEY"}), 500
    import base64
    prompt = ("You are a radiology vision assistant (decision-support only, NEVER a final read). "
              "Analyze this radiology image. Return JSON: {\"image_type\": \"...\", \"preliminary_findings\": \"...\", "
              "\"suspicious_areas\": [...], \"urgency\": \"ROUTINE|SOON|STAT\", \"red_flags\": [...], "
              "\"draft_note\": \"PRELIMINARY AI DRAFT - radiologist review REQUIRED before signature\"}. "
              "If the image is not a medical image, say so. Be conservative; any doubt -> escalate urgency.")
    b = base64.b64encode(open(img, "rb").read()).decode()
    body = {"contents": [{"parts": [{"text": prompt},
        {"inline_data": {"mime_type": "image/jpeg", "data": b}}]}]}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={key}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=120)
        dd = json.loads(r.read())
        txt = dd["candidates"][0]["content"]["parts"][0]["text"].strip().lstrip("```json").rstrip("```").strip()
        try:
            return jsonify({"preliminary": json.loads(txt)})
        except json.JSONDecodeError:
            return jsonify({"preliminary_raw": txt})
    except Exception as e:
        return jsonify({"error": str(e)[:150]}), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8092)
