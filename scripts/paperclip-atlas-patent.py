import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-HERMES/1.0", "Content-Type": "application/json",
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
    "title": "CEO DIRECTIVE (founder): HIRE PATENT ATTORNEY — redraft the patent (Ford-style system/method claims) covering ALL products; file BEFORE Reg A qualification",
    "description": ("FOUNDER 2026-08-02: 'I did not file the patent. Find a patent attorney to redraft the patent. Much "
                    "like Ford patents on how systems work, and all the other products we have.' (Batman/Lucius Fox "
                    "style: the specialist who outfits every idea with protective IP.)\n\n"
                    "=== CRITICAL FACT ===\n"
                    "The provisional patent was NOT FILED (vault IP/Provisional-Patent-2025-06-16.md is a DRAFT). "
                    "Memory + Reg A draft corrected. The Reg A Offering Circular is PUBLIC DISCLOSURE: it starts the "
                    "12-month AIA grace clock — the provisional MUST be filed BEFORE qualification to preserve "
                    "novelty (counsel to confirm grace mechanics).\n\n"
                    "=== HIRE: PATENT ATTORNEY SPECIALIST (hermes_gateway, reports to CEO) ===\n"
                    "1) REDRAFT the provisional: Ford-style SYSTEM + METHOD claims ('how the systems work' — "
                    "orchestration, routing, memory, telemetry, sovereign inference — not just device/UI)\n"
                    "2) COVER ALL PRODUCTS: NURA OS/Hermes agentic core (MCP orchestration, routing, shared memory, "
                    "skills) · ambient documentation + coding pipeline · telemetry CDS (NEWS2) · sovereign/offline "
                    "inference (disk-streamed MoE) · dual-mode app (EA/MEDICAL + slash commands) · JARVIS radiology "
                    "workflow · RCM denial intelligence · NURA ONE vision form analysis · wearable/glasses/Capsule "
                    "proximity + scribe · drone/EMS mesh ops · Avionics Connect · IP HoldCo licensing architecture\n"
                    "3) DRAFTING POSTURE: prior-art aware (study Verge/Anduril/Lattice/OpenAI patterns as prior art — "
                    "NEVER copy; claims on OUR novel combinations); breadth vs. enablement balance\n"
                    "4) PORTFOLIO STRATEGY: one strong provisional now (or 2-3 by product family) → PCT/US "
                    "continuation plan → tie to the offering (IP = the collateral per Assurance capitalization)\n"
                    "5) RECORDS: inventor disclosures (founder + dev team), IP assignments from ALL developers "
                    "(Morocco/Afghanistan contractors covered — NDAs + assignments exist; verify), lab notebooks\n\n"
                    "=== DELIVERABLES ===\n"
                    "1) Claim-map + filing strategy (by 2026-08-08)\n"
                    "2) Provisional redraft v1 — ALL products (by 2026-08-15)\n"
                    "3) FILING package ready (by 2026-08-22) — BEFORE Reg A qualification\n"
                    "Evidence on this issue per deliverable. Outside licensed patent counsel reviews before filing."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Patent attorney directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
