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

# 1. NUR-102 status
req = urllib.request.Request(base + f"/api/companies/{CID}/issues?limit=150", headers=hdr)
with urllib.request.urlopen(req, timeout=20) as r:
    data = json.loads(r.read())
issues = data if isinstance(data, list) else data.get("issues", data.get("data", []))
for it in issues:
    ident = str(it.get("identifier", ""))
    if ident == "NUR-102":
        print("NUR-102:", it.get("status"), "| priority:", it.get("priority"), "| assignee:", it.get("assigneeAgentId"))
        print("title:", it.get("title", "")[:90])
        print("desc head:", (it.get("description") or "")[:220].replace("\n", " "))

# 2. agent roster
req = urllib.request.Request(base + f"/api/companies/{CID}/agents", headers=hdr)
with urllib.request.urlopen(req, timeout=20) as r:
    agents = json.loads(r.read())
al = agents if isinstance(agents, list) else agents.get("agents", agents.get("items", []))
print("\nAGENT COUNT:", len(al))
for a in al:
    name = a.get("name", "")
    desc = (a.get("description") or "")
    blob = (name + " " + desc).lower()
    if any(k in blob for k in ["bridge", "edge", "voip", "interop", "designer", "telecom", "ml engineer", "ui/ux", "flutter"]):
        print("SPECIALIST:", name, "|", (a.get("adapterConfig") or {}).get("type", "?") if isinstance(a.get("adapterConfig"), dict) else "?")
