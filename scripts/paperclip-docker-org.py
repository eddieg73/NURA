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
    "title": "NUR-105: Docker engineering team hired — CTO owns the 5 container roles",
    "description": ("Founder 2026-08-02: ensure the CTO has the 5 Docker-management roles. HIRED (hermes_"
                    "gateway, verified 201): DevOps Engineer — Docker (75ff53d4), SRE (060b4c56), Cloud "
                    "Architect — Hostinger Fleet (f8689442), Platform Engineer — Internal Infra (adf60903), "
                    "SysAdmin — Container Hosts (16b27620). Existing: Docker App Governance Manager + "
                    "Systems Admin — EHR/CRM/OMNI/Workspace + OpenEMR SysAdmin.\n"
                    "CTO: assign responsibilities into the fleet operating rhythm — deploy guard (RAM/disk), "
                    "6h health checks, docker-mcp lanes, NUR-68 ruling execution, capacity reviews; report "
                    "the Docker org chart on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-105 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
