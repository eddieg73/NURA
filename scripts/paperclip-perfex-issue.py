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
CEO = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

agent = {
    "name": "Perfex CRM Developer",
    "role": "general",
    "title": "Perfex CRM Developer — RCM customization, integrations, bridge (NUR-41)",
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
    "title": "NUR-54: CEO DIRECTIVE — hire Perfex CRM Developer (done by Hermes) + Perfex build backlog",
    "description": ("CEO confirmed hire: Perfex CRM Developer (created, hermes_gateway). Scope (founder 2026-08-02):\n\n"
                    "1) LANE: Perfex API lane live (183 tools) — complete token wiring when PERFEX_API_TOKEN drops; "
                    "optional DB lane (mcp-perfex-crm) ONLY on 817449 loopback/tunnel.\n"
                    "2) BRIDGE NUR-41: build o2p-sync CLI then perfex-openemr-bridge MCP per openemr-perfex-integration "
                    "skill (SOP-1 lead onboarding, SOP-2 fee-sheet->invoice, idempotency external_ref, CF_OPENEMR_ID "
                    "custom field).\n"
                    "3) CUSTOMIZATION: membership ledger (concierge tiers synced from OpenEMR), payment reminders "
                    "(>30d sweeps), lead routing, custom fields + pipelines for clinical programs (HRT/GLP-1/peptide "
                    "packages), UTM tracking from media campaigns (SOP-5/6).\n"
                    "4) FINANCE SAFETY: financial guardrails per perfex-mcp skill (preview line items, never alter "
                    "paid invoices, audit attribution).\n"
                    "GATES: PHI never enters Perfex (sanitized billing only); relational integrity on deletes; "
                    "approval-gated invoice sends."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-54 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
