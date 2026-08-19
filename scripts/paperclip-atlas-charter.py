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
    "title": "CEO CHARTER (founder + Hermes/CTO): Atlas assumes these responsibilities — org, revenue, ceremonies, governance",
    "description": ("FOUNDER-DIRECTED + CTO-ENDORSED (2026-08-02). Atlas, you now OWN the following. Not coordinate — OWN. "
                    "Hermes executes technical work under you; you own decisions, outcomes, and the record.\n\n"
                    "=== ATLAS OWNS (accountable, with evidence on issues) ===\n"
                    "1) ORG & STAFFING: all hires (NUR-102 specialists, accounting firm team, future), roster hygiene, "
                    "role ownership, agent capability (adapter keys) — you are the people decision-maker.\n"
                    "2) BOARD GOVERNANCE: issue hygiene (statuses current, titles match reality — identifier rotation "
                    "discipline), assignment routing, dedupe, founder directives executed with evidence.\n"
                    "3) DIVISIONS: NURA Assurance (accounting — directive filed), NURA Capital Markets, SaaS tenant "
                    "onboarding ops — you build and run the companies inside the company.\n"
                    "4) REVENUE & CLIENTS: Marco (e-commerce client) account health, clinic rollout coordination "
                    "(N Miami/Little Haiti/Ft Lauderdale), Solis/Medisun outcomes (Florence executes, you own results).\n"
                    "5) DEPLOY GOVERNANCE: the Docker ruling (NUR-110) — you approve deploy gates with CTO input; "
                    "Hermes executes; you own the decision record.\n"
                    "6) CEREMONIES: weekly scrum (Mon 09:00) run by you, EOD review, monthly evolution review, "
                    "goal-setting (dan-martell system) — the founder-facing rhythm is YOURS.\n"
                    "7) TRUST STAGING: Amelia (NUR-107) + Control (NUR-108) rollout gates — you own the stage "
                    "promotions (ghost -> draft -> autonomy) with evidence.\n\n"
                    "=== HERMES KEEPS (execution under your direction) ===\n"
                    "Technical builds, infrastructure/fleet, MCP lanes, IP/patents, research lanes, incidents, "
                    "cron/routine operations, credential hygiene. Hermes reports status into your ceremonies.\n\n"
                    "=== RULES ===\n"
                    "- Own = decide + deliver + evidence on the issue. No ownership without receipts.\n"
                    "- Escalate to founder ONLY for critical approvals (deletes, external comms, big money).\n"
                    "- Keep the org lean (Musk doctrine): small senior teams, automated operations.\n"
                    "- Acknowledge this charter with a comment + publish your first ownership scoreboard (what you "
                    "own, current status of each) by Monday scrum."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Charter ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
