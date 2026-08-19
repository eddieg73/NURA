import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}

# find company + Atlas (CEO)
req = urllib.request.Request(base + "/api/companies?limit=1", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
companies = d if isinstance(d, list) else d.get("companies", [])
cid = companies[0]["id"] if companies else "999ff375-6128-41cf-b6c8-06b98673a29b"

req = urllib.request.Request(base + f"/api/companies/{cid}/agents?limit=200", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = None
for a in agents:
    name = (a.get("name") or "").lower()
    if "atlas" in name or (a.get("role") or "").lower() in ("ceo", "founder"):
        atlas = a
        break
if not atlas:
    print("ATLAS NOT FOUND; agents:", len(agents))
    for a in agents[:5]:
        print("-", a.get("name"), a.get("role"), a.get("id"))
    raise SystemExit(1)
print("Atlas:", atlas.get("name"), "|", atlas.get("role"), "|", atlas.get("id"))

issue = {
    "title": "Housekeeping: workout program fully removed (2026-08-02)",
    "description": ("Informational for Atlas CEO. Founder-approved removal of the workout program:\n"
                    "1) Cron jobs removed: daily workout reminder + weekly review (earlier).\n"
                    "2) Skill deleted: workout-schedule-and-progress-tracking.\n"
                    "3) Stack deleted TODAY via Hostinger API: compose project workout-cool-660n on VM "
                    "1441409 (app container was UNHEALTHY) — action docker_compose_down id 107345367; "
                    "containers + postgres db removed; host port 32795 freed. Project shell still listed "
                    "(created state) pending final cleanup.\n"
                    "No org impact: no active workflows referenced the stack. Hermes handled directly; "
                    "logging for the org record."),
    "assigneeAgentId": atlas["id"], "priority": "low", "status": "done",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Atlas notice ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
