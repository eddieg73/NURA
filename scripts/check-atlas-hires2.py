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

# issues: find anything with 102
req = urllib.request.Request(base + f"/api/companies/{CID}/issues?limit=200", headers=hdr)
with urllib.request.urlopen(req, timeout=20) as r:
    data = json.loads(r.read())
issues = data if isinstance(data, list) else data.get("issues", data.get("data", []))
print("issues fetched:", len(issues))
for it in issues:
    ident = str(it.get("identifier", ""))
    if "102" in ident:
        print("FOUND:", ident, "|", it.get("status"), "|", it.get("title", "")[:80])

# agents: full config of specialist candidates
req = urllib.request.Request(base + f"/api/companies/{CID}/agents", headers=hdr)
with urllib.request.urlopen(req, timeout=20) as r:
    agents = json.loads(r.read())
al = agents if isinstance(agents, list) else agents.get("agents", agents.get("items", []))
for a in al:
    name = a.get("name", "")
    if name in ("Mobile Telecom Bridge Engineer", "Healthcare UX Designer", "Edge AI/ML Engineer", "Bridge"):
        cfg = a.get("adapterConfig")
        print("\n---", name)
        print("  role:", a.get("role"), "| created:", a.get("createdAt", a.get("created_at", "?")))
        print("  adapter type:", (cfg or {}).get("type") if isinstance(cfg, dict) else cfg)
        print("  has apiKey:", bool((cfg or {}).get("apiKey")) if isinstance(cfg, dict) else "?")
