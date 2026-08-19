import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"

# resolve CTO (Orion) from roster
req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
cto = next((a for a in agents if (a.get("name") or "").lower() in ("cto", "orion cto", "orion")), None)
aid = cto["id"] if cto else None
if not aid:
    print("CTO NOT FOUND — falling back to Atlas")
    atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
    aid = atlas["id"] if atlas else None
if not aid:
    print("NO ASSIGNEE"); raise SystemExit(1)

issue = {
    "title": "BUILD: NURA Glasses — wearable AI hardware (Meta Ray-Ban class) — hardware lane",
    "description": ("FOUNDER 2026-08-02: 'Incorporate Nura into glasses like Meta.' Spec banked: vault IP/NURA-Glasses-"
                    "Hardware.md (form factor, 7 AI lanes, architecture, consent rules, IP).\n"
                    "=== SCOPE ===\n"
                    "1) Form: ~50-60g smart glasses — 12MP POV camera, mic array, bone-conduction, BLE/WiFi; phone is "
                    "the brain (doctrine: glasses = senses).\n"
                    "2) Lanes: ambient scribe (CORA) · POV telehealth/EMS scene streaming · voice Hermes · steth "
                    "audio-Ddx · photo/OCR → vault · sky capture · EHR context whisper (PHI-gated).\n"
                    "3) Offline-capable (offline-ai-agent); E2EE; no PHI at rest on device.\n"
                    "4) Consent: FL two-party recording law — consent flows mandatory.\n"
                    "5) IP: continuation-worthy — claim 1 + 14-15 embodiment; attorney package.\n\n"
                    "=== EXECUTE ===\n"
                    "1) Hardware eval: Snapdragon AR1 Gen 1 class + open SDKs; BOM sketch.\n"
                    "2) Consent + privacy spec (beep/indicator, deletion).\n"
                    "3) Integrate with the app's audio/vision pipeline (vision cascade + STT already live).\n"
                    "4) Add to continuation package + patent watch lanes.\n"
                    "Evidence: eval doc + consent spec by 2026-08-15; no hardware purchases without founder sign-off."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Glasses build issue ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
