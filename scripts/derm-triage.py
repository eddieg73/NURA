#!/usr/bin/env python3
"""NURA Derm Triage — lesion photo → structured triage (decision-support, NOT diagnosis).
Uses the Gemini vision lane (gemini-3-flash-preview, sealed key).
Usage: python3 derm-triage.py /path/to/lesion.jpg
Output: structured JSON — ABCDE-style assessment + triage level + [DERM REVIEW RECOMMENDED] flag.
DOCTRINE: provider-gated. Never renders a diagnosis. Severity flags = triage routing only."""
import sys, os, json, base64, urllib.request, urllib.error

def read_env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return ""

PROMPT = """You are a dermatology triage assistant (decision-support only, never a diagnosis).
Analyze this image. If it is not a skin lesion/photo, say so. For a skin lesion, return JSON:
{"is_lesion": true/false, "description": "...", "abcde": {"asymmetry": "...", "border": "...", "color": "...", "diameter": "...", "evolving": "unknown"},
 "triage": "ROUTINE|SOON|URGENT", "flag_derm_review": true/false,
 "reasons_to_refer": [...], "red_flags": [...], "note": "All assessments require clinician review."}
Be conservative: any red flag or uncertainty -> triage SOON/URGENT and flag_derm_review true. JSON only."""

def triage(path):
    key = read_env("GEMINI_API_KEY")
    if not key:
        return {"error": "no GEMINI_API_KEY"}
    img = base64.b64encode(open(path, "rb").read()).decode()
    body = {"contents": [{"parts": [
        {"text": PROMPT},
        {"inline_data": {"mime_type": "image/jpeg", "data": img}}]}]}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={key}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=90)
        d = json.loads(r.read())
        txt = d["candidates"][0]["content"]["parts"][0]["text"]
        txt = txt.strip().lstrip("```json").rstrip("```").strip()
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return {"raw": txt}
    except Exception as e:
        return {"error": str(e)[:150]}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: derm-triage.py <image>"); sys.exit(1)
    print(json.dumps(triage(sys.argv[1]), indent=2))
