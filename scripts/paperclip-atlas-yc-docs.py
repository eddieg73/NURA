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
    "title": "CEO DIRECTIVE (founder): HIRE FUNDRAISING-DOCS TEAM — YC SAFE suite + founding documents, legal/accounting supervised",
    "description": ("FOUNDER 2026-08-02: 'Safe act, documents for YC Combinator. Have Atlas hire the team to produce "
                    "all documents and work with and supervised legal and accounting.'\n\n"
                    "=== SCOPE: PRODUCE THE COMPLETE YC-STYLE DOCUMENT SUITE ===\n"
                    "1) YC SAFE SUITE (post-money SAFE — current YC template): SAFE + Board Consent + Side Letter + "
                    "SAFE holder questionnaire; instruments tailored to the NURA structure (WY LLC → corporate "
                    "conversion at Reg A trigger — conversion mechanics per counsel)\n"
                    "2) FOUNDING DOCS: Co-Founder Agreement template · IP Assignment (founder → company; the 22-claim "
                    "patent package + continuation) · standard vesting schedule (4-year/1-year cliff — harmonize with "
                    "the Musk-style performance award: SEC/Founder-Compensation-Plan.md)\n"
                    "3) CAP TABLE + EQUITY ADMIN: full cap table build (founder 100% pre-offering; WY trust holdings "
                    "disclosed), future-raise scenario modeling (SAFE → priced round → Reg A notes)\n"
                    "4) INTEGRATION: SAFE terms reconciled with the Reg A convertible-note offering (no integration "
                    "of offerings risk — SEC specialist)\n\n"
                    "=== TEAM (hire via Atlas) ===\n"
                    "Fundraising Docs Specialist(s) producing the suite — WORKING WITH AND SUPERVISED BY:\n"
                    "- LEGAL: Securities Attorney Specialist (issue 1ed6ab0e — Reg A + SAFE consistency, state "
                    "coordination, WY operating agreement amendments)\n"
                    "- ACCOUNTING: NURA Assurance / Midas CFO (cap table, ASC 718, 409A valuation prep, expense "
                    "schedules)\n"
                    "- COUNCEL: outside licensed counsel reviews + signs (AI-assisted drafting is never a substitute)\n\n"
                    "=== DELIVERABLES ===\n"
                    "1) Document-production plan + team roster (by 2026-08-06)\n"
                    "2) SAFE suite v1 (by 2026-08-13)\n"
                    "3) Founding docs + IP assignment + cap table (by 2026-08-20)\n"
                    "4) Legal + accounting sign-off evidence on each (by 2026-08-27)\n"
                    "Evidence on this issue per deliverable."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("YC docs team directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
