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
GATEWAY = {"baseUrl": "http://127.0.0.1:8642/v1", "apiKey": env_file("/opt/data/profiles/nura/.env", ["API_SERVER_KEY"])}

HIRES = [
    ("DevOps Engineer — Docker", "Package and deploy apps with Docker across the NURA fleet (Clinic/Lab/Storefront); CI/CD, compose builds, healthchecks; evidence-first deploys."),
    ("Site Reliability Engineer (SRE)", "Fleet stability + scale: load/connection managers, watchdog cadence, fail-fast recovery, capacity reviews; keeps 6h health checks green."),
    ("Cloud Architect — Hostinger Fleet", "Placement + optimization across KVM4/KVM8/KVM1; firewall groups, resource sizing, cost-aware architecture decisions with the CTO."),
    ("Platform Engineer — Internal Infra", "Standardize dev environments (docker-mcp lanes :8100-8102, node-agent sensors, shared images); developer tooling for Paperclip devs."),
    ("SysAdmin — Container Hosts", "Host-level container management: mem_limits, volumes, backups, swap discipline; never kills s6 children; host-side changes documented."),
]

for name, desc in HIRES:
    body = {"companyId": CID, "name": name, "description": desc,
            "adapterConfig": {"type": "hermes_gateway", **GATEWAY}}
    try:
        req = urllib.request.Request(base + "/api/companies/" + CID + "/agents",
                                     data=json.dumps(body).encode(), headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
            print("HIRED:", name, "->", r.status, d.get("id", d.get("agentId", "?")))
    except urllib.error.HTTPError as e:
        print("ERR", name, e.code, e.read().decode()[:150])
