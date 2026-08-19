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
gwkey = env_file("/opt/data/profiles/nura/.env", ["API_SERVER_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"

try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", headers=hdr)
    with urllib.request.urlopen(req, timeout=10) as r:
        agents = json.loads(r.read())
except Exception as e:
    print("LIST ERR", str(e)[:100]); raise SystemExit

alist = agents if isinstance(agents, list) else agents.get("agents", agents.get("items", []))
ok = fail = 0
for a in alist:
    aid = a.get("id")
    if not aid:
        continue
    try:
        payload = {"adapter": "hermes_gateway",
                   "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1", "apiKey": gwkey}}
        req = urllib.request.Request(base + f"/api/agents/{aid}", data=json.dumps(payload).encode(),
                                     headers=hdr, method="PATCH")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            cfg = (d.get("adapterConfig") or {})
            has_key = bool(cfg.get("apiKey"))
            ok += 1 if has_key else 0
            if not has_key:
                print("NO KEY on", d.get("name", aid)[:40])
    except Exception as e:
        fail += 1
        print("FAIL", a.get("name", "?")[:40], str(e)[:60])
print(f"PATCHED with gateway key: {ok}/{len(alist)} (fail {fail})")
