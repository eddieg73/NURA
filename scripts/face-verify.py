#!/usr/bin/env python3
"""NURA Opt-In Face Verify — 1:1 verification against a CONSENT ROSTER (never stranger-search).
Local-first doctrine: roster images live at /opt/data/optin-roster/<name>.jpg (consenting people only).
Uses the Gemini vision lane for face comparison.
Usage: python3 face-verify.py /path/to/photo.jpg [roster_name]   (blank name = check whole roster)
DOCTRINE: opt-in only · right-to-delete (remove the file = forgotten) · no scraping, no public-web matching."""
import sys, os, json, base64, urllib.request

ROSTER = "/opt/data/optin-roster"

def read_env(name):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(name + "="):
            return line.strip().split("=", 1)[1].strip("'\"")
    return ""

def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()

def verify(photo, roster_img, roster_name):
    key = read_env("GEMINI_API_KEY")
    body = {"contents": [{"parts": [
        {"text": f"Compare the two faces. First image: new photo. Second image: the rostered person '{roster_name}'. Respond JSON only: {{\"match\": true/false, \"confidence\": \"high|medium|low\", \"note\": \"one line\"}}. Never speculate on identity beyond this 1:1 comparison."},
        {"inline_data": {"mime_type": "image/jpeg", "data": b64(photo)}},
        {"inline_data": {"mime_type": "image/jpeg", "data": b64(roster_img)}}]}]}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={key}",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    import urllib.error
    try:
        r = urllib.request.urlopen(req, timeout=90)
        d = json.loads(r.read())
        txt = d["candidates"][0]["content"]["parts"][0]["text"].strip().lstrip("```json").rstrip("```").strip()
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return {"raw": txt}
    except Exception as e:
        return {"error": str(e)[:150]}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: face-verify.py <photo> [name]"); sys.exit(1)
    photo = sys.argv[1]
    if not os.path.exists(ROSTER):
        print(json.dumps({"error": "no roster dir — create /opt/data/optin-roster/ with <name>.jpg (consent only)"}, indent=2))
        sys.exit(1)
    if len(sys.argv) > 2:
        name = sys.argv[2]
        rimg = os.path.join(ROSTER, name + ".jpg")
        print(json.dumps(verify(photo, rimg, name) if os.path.exists(rimg) else {"error": f"{name} not in roster"}, indent=2))
    else:
        out = []
        for f in sorted(os.listdir(ROSTER)):
            if f.endswith((".jpg", ".jpeg", ".png")):
                name = os.path.splitext(f)[0]
                out.append({name: verify(photo, os.path.join(ROSTER, f), name)})
        print(json.dumps(out, indent=2))
