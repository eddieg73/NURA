import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
base = "http://127.0.0.1:3101"
iid = "fa0f9bb7-c478-4ee8-945f-e80c824a91a2"

body = ("HERMES STATUS CHECK (2026-08-02): issue shows BLOCKED on the CTO canvas with NO blocker comment — violates "
        "kanban discipline (every blocked issue carries blocker + next step). Founder asked for status.\n"
        "CURRENT STATE: directive filed (critical) · TAK feasibility doc DUE 08-10 (not yet on the issue) · earpiece "
        "integration plan DUE 08-15 · Anduril tie = doctrine-level only (no code).\n"
        "TECHNICAL REALITY (verified): ATAK/CIVTAK are open — plugin dev via the ATAK SDK (Android), CIVTAK "
        "available to first responders; earpiece lane = BLE/audio AI (our stack); Anduril = concept references only "
        "(IP-safe doctrine).\n"
        "ACTION REQUIRED (owner + CTO): state the blocker + next step on this issue BEFORE Monday scrum 09:00 EDT. "
        "Founder expects TAK feasibility evidence by 08-10.")
try:
    req = urllib.request.Request(base + f"/api/issues/{iid}/comments", data=json.dumps({"body": body}).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("status comment ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
