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

issue = {
    "title": "NUR-46: CEO DIRECTIVE — create an n8n Workflow Developer agent and commission the full workflow build",
    "description": ("CEO action (founder 2026-08-02): create a dedicated 'n8n Workflow Developer' agent (hermes_gateway "
                    "adapter, adapterConfig.apiBaseUrl=http://127.0.0.1:8642/v1, reports to CTO) and assign it the n8n "
                    "build: (1) Chatwoot resolved-conversation -> Perfex ticket, (2) clinical lead onboarding -> OpenEMR "
                    "patient + Perfex customer, (3) fee sheet -> Perfex invoice (sanitized), (4) recall campaigns + "
                    "appointment confirmations, (5) missed-call text-back, (6) financial hygiene sweep, (7) incident "
                    "alerts (escalate.py schema). Standards: idempotency keys, PHI stays in OpenEMR, audit attribution, "
                    "live test-run verification. If agent-creation is blocked by permissions, request Hermes to create "
                    "it on your behalf and confirm here."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-46 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
