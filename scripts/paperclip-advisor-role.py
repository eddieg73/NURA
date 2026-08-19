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

# resolve Atlas
req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
aid = atlas["id"] if atlas else None
if not aid:
    print("ATLAS NOT FOUND"); raise SystemExit(1)

# 1) hire the Advisor
advisor = {
    "name": "Advisor", "role": "general", "title": "Board Advisor (6-CEO Advisory Council)",
    "adapterType": "hermes_gateway", "reportsTo": aid,
    "agentDefaultsPayload": {"apiBaseUrl": "http://127.0.0.1:8642", "apiKey": key,
                              "paperclipApiUrl": "http://127.0.0.1:3101"},
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/agents", data=json.dumps(advisor).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        advisor_id = d.get("id") or d.get("agentId") or "?"
        print("Advisor hired ->", r.status, advisor_id)
except urllib.error.HTTPError as e:
    print("HIRE ERR", e.code, e.read().decode()[:200])
    advisor_id = None

# 2) board notice to Atlas (division directive pattern)
if advisor_id and advisor_id != "?":
    issue = {
        "title": "ADVISORY ROLE created (founder) — Board Advisor + quarterly portfolio reviews",
        "description": ("FOUNDER 2026-08-02: advisory role institutionalized. Agent 'Advisor' hired (reports to CEO) "
                        "running the 6-CEO advisory council (ceo-advisory-board skill: Musk/Bezos/Jobs/Buffett/"
                        "Nadella/Huang MoE routing).\n"
                        "=== CHARTER ===\n"
                        "1) Quarterly portfolio reviews of ALL companies + projects (Nuratech core · Assurance · "
                        "Capital Markets · Aero · app · clinics · Solis · sync · content · UAP).\n"
                        "2) Decision framing on demand (routing matrix + synthesis, banked to vault Advisory-Board.md).\n"
                        "3) ADVISORY ONLY — no executive authority, never overrides the provider gate; recommendations "
                        "always survive founder review.\n"
                        "4) [D2] portfolio review complete 2026-08-02: ONE company to run (Nuratech), one division to "
                        "build (Aero), two utilities (Assurance + sync), two parked experiments (markets + content), "
                        "one bounded hobby (UAP).\n"
                        "Atlas: acknowledge; advisor participates in Monday scrum as consult."),
        "assigneeAgentId": aid, "priority": "medium", "status": "todo",
    }
    try:
        req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                     headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print("Advisory notice ->", r.status, d.get("id", d.get("issueId", "?")))
    except urllib.error.HTTPError as e:
        print("NOTICE ERR", e.code, e.read().decode()[:200])
