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

agent = {
    "name": "Workflow Automation Developer",
    "role": "general",
    "title": "n8n · OpenEMR · Perfex · Chatwoot Workflow Builder",
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "reportsTo": CTO,
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", data=json.dumps(agent).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        dev_id = d.get("id")
        print("AGENT ->", r.status, dev_id, d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("AGENT ERR", e.code, e.read().decode()[:250])
    raise SystemExit

issue = {
    "title": "NUR-45: Build ALL workflows — n8n + OpenEMR + Perfex + Chatwoot",
    "description": ("Workflow build directive (founder 2026-08-02). Specs: NURATECH-MASTER-MANIFEST.md (SOP-1..4), "
                    "THREE-PLATFORM-TOOL-MAP.md (gaps), openemr-perfex-integration skill, chatwoot lane (123 tools).\n\n"
                    "N8N (workflows MCP-enabled by founder): 1) Chatwoot resolved-conversation -> Perfex support ticket "
                    "(external_ref chatwoot:{id}) 2) Clinical lead onboarding -> OpenEMR patient + Perfex customer (SOP-1) "
                    "3) Encounter fee sheet -> Perfex invoice (SOP-2, sanitized) 4) Recall campaigns + appointment "
                    "confirmations (OpenEMR schedule -> patient SMS) 5) Missed-call text-back 6) Financial hygiene sweep "
                    "(unpaid >30d -> summary) 7) Incident alert -> Telegram/email payload (escalate.py schema).\n"
                    "OPENEMR: concierge/HRT/GLP-1 automation with the OpenEMR Concierge Developer (NUR-44) — portal "
                    "messaging, scheduling rules, order-draft routing.\n"
                    "PERFEX: payment reminders, lead routing, membership ledger sync.\n"
                    "CHATWOOT: inbox routing rules, canned responses, SLA escalation, kanban<->appointments mirror "
                    "(Medisun front desk).\n\n"
                    "STANDARDS: idempotency keys (external_ref), PHI stays in OpenEMR (sanitized descriptions to "
                    "Perfex/Chatwoot), audit attribution to Hermes Agent, .bak before edits, verify each workflow with "
                    "a live test run.\n"
                    "BLOCKERS: n8n token append (30s operator block), OpenEMR creds drop, Chatwoot API token."),
    "assigneeAgentId": dev_id,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-45 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
