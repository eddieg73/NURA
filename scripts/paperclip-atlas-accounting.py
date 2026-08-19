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
if not atlas:
    print("ATLAS NOT FOUND")
    raise SystemExit(1)
aid = atlas["id"]

issue = {
    "title": "CEO DIRECTIVE (founder): Build NURA Assurance — internal accounting firm (Deloitte model, Musk discipline)",
    "description": ("FOUNDER DIRECTIVE 2026-08-02 — Atlas executes. Build a Big-4-STYLE internal accounting practice "
                    "to manage ALL Nuratech books. Use Musk companies as the operating example.\n\n"
                    "=== THE MUSK MODEL (how to run finance) ===\n"
                    "- SpaceX/Boring: first-principles cost engineering — question every dollar, build the capability "
                    "internally before buying it (vertical integration).\n"
                    "- Tesla: real-time financials in the factory — unit economics visible daily, not monthly.\n"
                    "- X/Neuralink: lean HQ, tiny finance staff, ruthless expense discipline.\n"
                    "- Net: centralized treasury, real-time dashboards, 10x cost reduction as a target, no sacred "
                    "budget lines.\n\n"
                    "=== SCOPE (Deloitte-style service lines) ===\n"
                    "1) BOOKKEEPING: full GL (Perfex finance modules), AP/AR, bank feeds, reconciliations, monthly close "
                    "calendar (books closed by day 5).\n"
                    "2) TAX: FL state + federal readiness; sales tax (SAAS: no FL sales tax on SaaS — verify); payroll "
                    "taxes (if any W-2s); 1099 filings for contractors.\n"
                    "3) FP&A / UNIT ECONOMICS: per-clinic P&L (N Miami / Little Haiti / Ft Lauderdale), per-SaaS-tenant "
                    "economics (ACV, gross margin, infra cost/tenant), Solis MA revenue tracking (PMPM $360 x 285), "
                    "agent/compute cost per dev (agent-cost-tracker.py exists — wire it into the dashboards).\n"
                    "4) RCM: tie to OpenEMR billing + NMI payments (Direct Connect v4) — claim-to-cash tracking, "
                    "denials, AR aging.\n"
                    "5) AUDIT READINESS: internal controls, audit trail (append-only), policy docs, capitalization of "
                    "software dev (IP), expense policy. External-audit-ready file by Q4.\n\n"
                    "=== TEAM (under Midas CFO — Atlas hires/assigns) ===\n"
                    "Controller · Bookkeeper · Tax specialist · FP&A analyst · Audit/compliance lead. Use the Paperclip "
                    "hire lane (hermes_gateway adapter, apiKey included). Size: lean — the Musk way: small, senior, "
                    "automated.\n\n"
                    "=== DELIVERABLES (evidence on this issue) ===\n"
                    "1) Chart of accounts draft (D1)\n"
                    "2) Monthly close calendar + who owns each step (D2)\n"
                    "3) Cash + per-clinic P&L dashboard spec (D3 — real-time, not monthly)\n"
                    "4) SaaS unit-economics template (D4)\n"
                    "5) Team roster with roles + first task assignments (D5 — by Monday scrum)\n"
                    "Hermes supports: agent-cost-tracker.py, Perfex MCP (183 tools), NMI lane, OpenEMR billing. "
                    "Books = single source of truth; no shadow spreadsheets."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Atlas directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
