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
    "title": "NUR-42: Execute the NURA Launch Pack alongside Hermes (founder directive 2026-08-02)",
    "description": ("CEO directive: you are now wired to the Hermes gateway (adapter fixed). Execute the Launch Pack in "
                    "docs/manuals/FINAL-SOLUTION-DMAIC.md + deploy/launch-kvm4.sh + deploy/node-agent.sh in parallel with Hermes. "
                    "1) Verify adapter (hermes_gateway, apiBaseUrl http://127.0.0.1:8642/v1). 2) Assign corps: Docker Platform Lead "
                    "(host block + node agents), Infrastructure SRE Lead (crons + log rotation), Integrations Specialist "
                    "(OpenEMR creds, Notion share, n8n token). 3) Report progress on this issue. Guardrails: operator-charter, "
                    "no destructive actions without approval."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("ISSUE ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
