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
hdr = {"User-Agent": "NURA-Hermes/1.0", "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"

try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", headers=hdr)
    with urllib.request.urlopen(req, timeout=8) as r:
        data = json.loads(r.read())
    agents = data if isinstance(data, list) else data.get("agents", data.get("items", []))
    print("agents:", len(agents))
    for a in agents:
        print("-", a.get("id", "?"), a.get("name", "?"), "| status:", a.get("status"), "| role:", a.get("role", "?"))
        ac = a.get("adapterConfig") or {}
        print("   adapter:", a.get("adapter"), "| apiBaseUrl:", str(ac.get("apiBaseUrl"))[:60])
except urllib.error.HTTPError as e:
    print("list ERR", e.code, e.read().decode()[:200])
