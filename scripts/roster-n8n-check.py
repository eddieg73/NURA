import json, re, urllib.request

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
hdr = {"User-Agent": "NURA-Hermes/1.0", "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"
req = urllib.request.Request(f"http://127.0.0.1:3101/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
print("total agents:", len(agents))
kw = ["n8n", "zapier", "integrat", "automation", "workflow", "api", "developer", "engineer", "dev"]
hits = []
for a in agents:
    name = (a.get("name") or "") + " " + (a.get("title") or "") + " " + (a.get("shortName") or "")
    low = name.lower()
    for k in kw:
        if k in low:
            hits.append((a.get("name"), a.get("title"), a.get("role")))
            break
for h in hits:
    print(" -", h)
