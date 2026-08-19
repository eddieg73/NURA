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
    "title": "NUR-68: CTO DECISION — Docker access architecture (socket mount vs docker-mcp lanes)",
    "description": ("Founder request 2026-08-02: Hermes needs Docker control. Best-practices consultation — CTO "
                    "(Orion) rules, Docker Platform Lead (Helm) implements.\n\n"
                    "CONTEXT: Hermes container on 1441409 has NO docker socket (client-only, verified). Two paths:\n"
                    "A) MOUNT /var/run/docker.sock into the Hermes container (direct control; ROOT-EQUIVALENT risk; "
                    "loopback-only; container recreate; session drop).\n"
                    "B) DOCKER-MCP LANES (designed path per multi-node-docker-ops skill): launch-kvm4.sh systemd "
                    "units :8100-8102 on Clinic + node-agent.sh on Lab/Edge with firewall scoping (8100 from "
                    "72.61.71.211 only). Same capability, less blast radius, multi-node ready.\n\n"
                    "CONSTRAINTS: operator-charter gates (no prune -a / rm -rf without authorization); PHI boundary "
                    "Clinic=1441409; never ssh:// DOCKER_HOST; docker-mcp official Go binary (E404 phantoms "
                    "verified); 5-attempt circuit breaker; RAM/disk deploy guards.\n"
                    "ASK: ruling (A, B, or A+B) + implementation block (exact commands) + who executes (Helm or "
                    "Oussama). Hermes executes the ruling on confirmation; founder authorized the request, CTO owns "
                    "the architecture."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-68 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
