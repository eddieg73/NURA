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
    "name": "MCP Integrations Developer",
    "role": "general",
    "title": "MCP Developer — build, wire & govern all integration lanes",
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
    "title": "NUR-48: CEO DIRECTIVE — develop MCP Integrations Developer (done by Hermes on CEO behalf) + build backlog",
    "description": ("CEO confirmed hire: MCP Integrations Developer agent (created, hermes_gateway). Scope (founder "
                    "2026-08-02):\n\n"
                    "BUILD BACKLOG (in order): 1) Google Workspace lane (gmail/calendar — OAuth drop pending) 2) Twilio "
                    "lane completion (creds present; wire SMS/voice tools) 3) GitHub lane (repo/PR/issue tools) 4) "
                    "Mattermost lane 5) Notion lane completion (share pending) 6) S3/R2 storage lane (token pending) 7) "
                    "OpenEMR-API lane completion (OAuth drop) 8) Perfex-OpenEMR bridge MCP (NUR-41) 9) host-side lanes: "
                    "docker/filesystem/vps-system units + per-node docker-mcp (launch-kvm4.sh/node-agent.sh) 10) "
                    "integration registry + governance docs.\n"
                    "GOVERNANCE (mandatory): wrapper pattern (secrets from .env 0600, never config), probe-first "
                    "(tools/list before wire), no PHI to external lanes, dedupe registry (one canonical lane per "
                    "service), config check + round-trip test per lane, skill+memory per new lane.\n"
                    "REFERENCE: mcp-integration-ops skill, external-api-credential-hygiene, integration registry "
                    "(docs/manuals/MCP-INTEGRATION-REGISTRY.md), operator-charter."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-48 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
