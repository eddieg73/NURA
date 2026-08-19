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
body = {"adapter": "hermes_gateway",
        "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"}}

try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", headers=hdr)
    with urllib.request.urlopen(req, timeout=8) as r:
        agents = json.loads(r.read())
except Exception as e:
    print("list ERR", str(e)[:100]); raise SystemExit

ids = [a["id"] for a in agents] if isinstance(agents, list) else []
ok = fail = 0
for aid in ids:
    try:
        req = urllib.request.Request(base + f"/api/agents/{aid}", data=json.dumps(body).encode(),
                                     headers=hdr, method="PATCH")
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
            ok += 1 if d.get("adapterType") == "hermes_gateway" else 0
    except Exception:
        fail += 1
print(f"PATCHED {ok}/{len(ids)} agents to hermes_gateway (fail {fail})")
