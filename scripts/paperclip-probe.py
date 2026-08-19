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

for p in ["/api/companies?limit=3", "/api/agents?limit=3"]:
    try:
        req = urllib.request.Request(base + p, headers=hdr)
        with urllib.request.urlopen(req, timeout=6) as r:
            print(p, "->", r.status)
            print(r.read().decode()[:500].replace("\n", " "))
    except urllib.error.HTTPError as e:
        print(p, "->", e.code, e.read().decode()[:120])
    except Exception as e:
        print(p, "-> ERR", str(e)[:100])
