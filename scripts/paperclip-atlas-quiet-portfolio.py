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
    "title": "CEO DIRECTIVE (founder): QUIET PORTFOLIO LANE — keep parked divisions developing, no noise",
    "description": ("FOUNDER 2026-08-02: 'Have the team quietly work on the portfolio.' (Post-Martell review: "
                    "simplify to multiply — the CORE = Healthcare AI OS for clinics; the portfolio = parked "
                    "optionality that KEEPS BUILDING quietly.)\n"
                    "QUIET RULES (mandatory):\n"
                    "1) NO public attention: no social posts, no press, no site features, no founder time, no "
                    "Reg A feature — the portfolio stays invisible to the outside world\n"
                    "2) Internal-only evidence: milestones reported on the board, receipts to Hermes, zero "
                    "marketing\n"
                    "3) The 90-day core focus is UNTOUCHED: app (TestFlight 08-20) · Reg A qualification · 5 "
                    "clinics by 11-01 — portfolio work never steals those lanes\n"
                    "4) Founder time = zero for portfolio; founders' sign-offs only where legally required\n"
                    "PORTFOLIO WORK (continue quietly, existing directives' gates):\n"
                    "- AERO: drone sim milestones (08-22 sim gate) · pod doctrine · Manatee research (done) — "
                    "no hardware spend without sign-off\n"
                    "- EMS AGENCY: licensure package (FL 631/COPCN) prep only · partnership conversations "
                    "confidential\n"
                    "- AVIONICS CONNECT: equipment scan + PoC 08-31 (read-only doctrine)\n"
                    "- ASSURANCE: books/entity prep quietly with the accounting lane\n"
                    "- CAPITAL MARKETS: stays parked\n"
                    "EVIDENCE GATE: each division posts a one-line quiet status on this issue each Friday 17:00 "
                    "EST — no fanfare, just progress or blockers."),
    "assigneeAgentId": aid, "priority": "medium", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Quiet portfolio directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
