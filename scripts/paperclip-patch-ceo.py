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
CEO = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"
body = {"adapter": "hermes_gateway",
        "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"}}

try:
    req = urllib.request.Request(base + f"/api/agents/{CEO}", data=json.dumps(body).encode(),
                                 headers=hdr, method="PATCH")
    with urllib.request.urlopen(req, timeout=8) as r:
        print("PATCH ->", r.status)
        print(r.read().decode()[:400])
except urllib.error.HTTPError as e:
    print("PATCH ERR", e.code, e.read().decode()[:250])
