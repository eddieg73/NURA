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

issue = {
    "title": "FOUNDER DIRECTIVES 08-03 — reporting hierarchy + Brawlerz continues + harvest complete",
    "description": ("1) REPORTING HIERARCHY: EVERYONE (agents + humans) reports to ATLAS; ATLAS reports to "
                    "HERMES. Org lane = Atlas (org/staff/revenue/ceremonies); infrastructure/tech lane = "
                    "Hermes. No side-channels.\n"
                    "2) CODE HARVEST COMPLETE: nura-jarvis-mvp + nura-cosmo extracted (EMS calculator "
                    "VERIFIED, scribe pipeline, EM level estimator, FHIR interface, tool router, offline "
                    "services) -> folded into nura-medical. Harvested source repos DELETED.\n"
                    "3) BRAWLERZ BOX: CONTINUED as a live product (founder 08-03) - eddieg73/NURA stays its "
                    "home; development continues. NOT parked, NOT killed.\n"
                    "4) nura-medical = the EA + Medical Clinician dual-mode app (TestFlight 08-20 lane).\n"
                    "ACTION: Atlas - update org chart (all -> Atlas -> Hermes), keep Brawlerz in the product "
                    "lineup with continued dev, route the medical app build on nura-medical."),
    "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Directive ->", r.status, d.get("id", d.get("issueId", d)))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
