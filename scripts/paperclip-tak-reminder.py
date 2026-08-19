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

try:
    req = urllib.request.Request(base + f"/api/issues/{iid}", headers=hdr)
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("status:", d.get("status"), "| assignee:", d.get("assigneeAgentId"), "| updated:", d.get("updatedAt", "?"))
except urllib.error.HTTPError as e:
    print("issue ->", e.code)

body = ("FOUNDER REMINDER (2026-08-02): CIVTAK/ATAK — the tactical + overwatch + medical drone modes ALL operate "
        "inside the TAK/CIVTAK operating picture. Scope already filed; reminder of the concrete ties:\n"
        "1) DRONE ON TAK: MAVSDK plugin (ATAK-CIV SDK 5.5 pattern, verified) — drone telemetry, camera feed, casualty "
        "pins, pod-delivery markers on the tactical map (spec: Aero/EMS-Drone-Spec.md — tactical medical role, "
        "overwatch, EMD modes)\n"
        "2) PJ EARPIECE lane: in-ear guidance + TAK map shared with the drone feed (the founder's special-forces "
        "story)\n"
        "3) CIVTAK = first-responder lane: EMS truck crews + paramedics carry the same map (drone + casualty + "
        "truck pins)\n"
        "4) STATUS: this issue is/was BLOCKED on the CTO canvas with no blocker comment — resolve BEFORE Monday "
        "scrum 09:00 EDT; TAK feasibility evidence due 08-10 stands.")
try:
    req = urllib.request.Request(base + f"/api/issues/{iid}/comments", data=json.dumps({"body": body}).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("tak reminder ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
