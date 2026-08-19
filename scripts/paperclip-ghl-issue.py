import json, urllib.request, urllib.error

def env_file(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env_file("/opt/data/paperclip-runtime/mcp.env", ["PAPERCLIP_API_KEY", "API_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

issue = {
    "title": "NUR-70: CTO — GoHighLevel MCP connector: identify EVERY endpoint, use ALL connectors (API+CLI+MCP)",
    "description": ("Founder 2026-08-02: GHL MCP connector exists (reference label pit-d715a64d-72e8-4157-bfb3-a17c0771653c; "
                    "skill gohighlevel-mcp). CTO (Orion) owns:\n\n"
                    "1) ENDPOINT INVENTORY — enumerate EVERY GHL API endpoint group and map each to a connector "
                    "surface: Contacts, Conversations, Calendars/Appointments, Pipelines/Opportunities, Tasks, "
                    "Tags/Custom fields, Workflows/Automations, Campaigns, Snapshots, Notes/Activity, Messaging "
                    "(SMS/email/call), Media Library, Products/Invoices, Surveys, Triggers, OAuth/tokens. Deliver "
                    "the full registry on this issue (endpoint -> method -> purpose -> status: wired/pending).\n"
                    "2) CONNECTOR MODES — wire ALL of: (a) MCP lane (wrapper pattern, tools allowlisted per "
                    "gohighlevel-mcp skill; safety gates for sends/deletes/bulk), (b) direct REST API lane "
                    "(curl/script, creds in .env 0600), (c) CLI/scripting mode (ghl-cli or scripted calls) for "
                    "cron/watchdog use.\n"
                    "3) AUTH: GHL API key (private integration) or OAuth; verify live with ONE read-only call "
                    "(contacts list) — evidence required before 'connected'.\n"
                    "4) TENANT SCOPE: per-location scoping (Medisun location, NURA locations) per SaaS-ready "
                    "mandate; RBAC allowlist; audit logging.\n"
                    "5) INTEGRATION REGISTRY: add GHL to the MCP topology registry (NUR-48 backlog item).\n"
                    "Deliver: endpoint registry + 3 connector modes live + verification evidence. Bridge "
                    "(MCP Integrations Dev) implements under Orion; Hermes holds the skill + wrapper patterns."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-70 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
