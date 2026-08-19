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

agent = {
    "name": "OpenEMR Concierge & Hormone Developer",
    "role": "general",
    "title": "OpenEMR Developer — Concierge Medicine, HRT, Peptides & GLP-1 Programs",
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "reportsTo": "0f81f292-5eea-4c6d-b64b-10b3345d29dd",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", data=json.dumps(agent).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("AGENT ->", r.status, d.get("id", "?"), d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:250])
