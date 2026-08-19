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
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-108: Control EA — manager-agent layer (n8n sub-agent routing + Paperclip integration, staged trust)",
    "description": ("Founder 2026-08-02 Dan Martell Control blueprint (skill control-executive-assistant): "
                    "manager agent, narrow scope, never executes directly.\n"
                    "ROUTING (locked): Amrit = tech/API blueprints · Osama = healthcare/compliance specs · "
                    "Marco = e-commerce (supply chain, inventory/API keys, CRM consolidation) · Esther "
                    "Garrido (mother) = legal/property/admin docs to HIGH-PRIORITY personal folder.\n"
                    "SUB-AGENTS (n8n + Paperclip): 1) DevOps Translator (idea -> SOW, split medical->Osama/"
                    "API->Amrit) 2) E-Commerce Integrator (supplier email -> inventory + keys -> Marco) 3) "
                    "Inbox Triage (daily cron, escalate NURATECH.ai + paramedic-program topics).\n"
                    "TRUST ROLLOUT (mandatory): Stage 1 GHOST (2 weeks, log intended actions only, daily "
                    "review of healthcare-vs-tech split) -> Stage 2 DRAFT (produce specs/emails/workflows, "
                    "ALL paused for principal Approve) -> Stage 3 AUTONOMY (only after CarePilot nuance "
                    "mastered; 15-min heartbeat).\n"
                    "CTO: wire sub-agent routing + ghost-mode logger; evidence: ghost log first week on "
                    "this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-108 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
