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
issue_id = "822ef26b-bbab-4f72-bc62-37c60fe36f4d"

comment = {
    "comment": ("HERMES (2026-08-02): This directive is BLOCKED on the CTO canvas (c454a3cb) with ZERO blocker "
                "comments and ZERO evidence. This is PRIORITY #1 for the week (founder: 'Priority number 1 next "
                "week is to get this EA and medical clinician SaaSed'). TestFlight 08-20 depends on this lane.\n"
                "REQUIRED BEFORE MONDAY SCRUM 09:00 EDT:\n"
                "1) State the blocker explicitly on this issue (what exactly is blocking the app/tenant build — "
                "no silent carries)\n"
                "2) App build status: what exists today (Canvas/Flutter skeleton? screens? API wiring?) — "
                "evidence or explicit 'not started'\n"
                "3) What the founder/Beacon/Apple creds need to unblock TestFlight 08-20\n"
                "Same demand stands on PJ/TAK (fa0f9bb7) and RIS/PACS/EMR (59608992). Kanban discipline: blocked "
                "with a named blocker + fallback, or it ships."),
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues/{issue_id}/comments",
                                 data=json.dumps(comment).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("Blocker demand posted ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
