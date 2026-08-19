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
    "title": "CEO DIRECTIVE (founder): HIRE SECURITIES ATTORNEY SPECIALIST — own the Reg A filing workstream",
    "description": ("FOUNDER 2026-08-02: hire an attorney SEC specialist.\n"
                    "MISSION: own the Regulation A+ (Form 1-A Tier 1) offering workstream end-to-end for Nuratech.\n\n"
                    "=== CURRENT STATE (banked) ===\n"
                    "Vault SEC/NURA-RegA-Offering-Circular-DRAFT.md — AI-assisted redraft complete (2026-08-02); "
                    "counsel checklist at end (entity confirmation, cap table, audit engagement, state coordination "
                    "FL OFR + WY SOS).\n\n"
                    "=== ROLE (hermes_gateway, reports to CEO) ===\n"
                    "1) Review the redraft vs current Reg A rules (Securities Act of 1933, Regulation A Tier 1, "
                    "Rule 251/257; Form 1-A Part II) — identify gaps/updates\n"
                    "2) State coordination matrix: Florida (Ch 517, OFR) + Wyoming (SOS) + all target states — "
                    "fees, forms, timing\n"
                    "3) Compliance calendar: qualification → 1-Z exit (30 days) → 1-K/1-SA ongoing reporting "
                    "(Tier 1 continuous reporting)\n"
                    "4) Coordinate with the REAL outside licensed counsel (the specialist manages, counsel signs) — "
                    "the specialist is NOT a substitute for licensed counsel; filings require licensed attorney "
                    "signature + officer certifications\n"
                    "5) Investor suitability (Rule 251(d)(2)(i)(C) 10% test), no-escrow/best-efforts mechanics, "
                    "integration-of-offerings risk check\n\n"
                    "=== DELIVERABLES ===\n"
                    "1) Gap review of the draft (by 2026-08-06)\n"
                    "2) State coordination matrix (by 2026-08-10)\n"
                    "3) Filing checklist + compliance calendar (by 2026-08-10)\n"
                    "Evidence on this issue per deliverable."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Sec attorney hire directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
