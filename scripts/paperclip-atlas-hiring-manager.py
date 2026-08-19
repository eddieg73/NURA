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

req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
aid = atlas["id"] if atlas else None
if not aid:
    print("ATLAS NOT FOUND"); raise SystemExit(1)

issue = {
    "title": "CEO DIRECTIVE (founder): DEVELOP AI HIRING MANAGER — AI hires the humans who finish the build",
    "description": ("FOUNDER 2026-08-02: 'Do I need to hire humans? If so develop a manager to hire developers to "
                    "assist you. AI hiring humans to finish the build.'\n"
                    "ANSWER (Hermes analysis): YES — a small strategic set of humans; AI runs the whole funnel; "
                    "founder signs.\n"
                    "HUMAN HIRES REQUIRED (the lanes AI cannot legally/medically own):\n"
                    "1) RADIOLOGY ML ENGINEER (highest value — none of the 65 agents has trained a production "
                    "vision model) — detection/caption/structured-report cascade\n"
                    "2) RADIOLOGIST CLINICAL ADVISOR (founder network — labels, validation, reader studies; medical "
                    "judgment is a licensed lane)\n"
                    "3) LICENSED CPA / AUDITOR (Reg A audited financials — statutory)\n"
                    "4) FLUTTER SENIOR (optional, only if Canvas misses 08-20 TestFlight)\n"
                    "5) Already in motion (human by law): SEC attorney · patent attorney · FDA de novo team (Alexis)\n"
                    "BUILD — THE AI HIRING MANAGER (Atlas creates this agent role):\n"
                    "A) ROLE SPECS: structured reqs per role (skills, evidence, scorecards) — Hermes drafts\n"
                    "B) SOURCING: job posts (LinkedIn/Indeed/Upwork/network) + direct outreach from the org\n"
                    "C) AI SCREENING PIPELINE: resume parse → skill-fit scoring → technical eval (take-home "
                    "validated by agents) → structured interview (Atlas/Hermes) → ranked shortlist\n"
                    "D) FOUNDER GATE: founder approves finalist (the only human signature in the funnel)\n"
                    "E) ONBOARDING: NDA + IP assignment (docs already banked), equity/comp per policy, Paperclip "
                    "roster entry, 30-day evidence gate (deliverables verified like agents')\n"
                    "RULE: AI never signs. AI recruits, screens, evaluates, and tracks — the founder hires.\n"
                    "DELIVERABLES: hiring-manager role + pipeline live by 2026-08-06 · Radiology ML Engineer "
                    "shortlist by 2026-08-10 · first human offer by 2026-08-14."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("AI Hiring Manager directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
