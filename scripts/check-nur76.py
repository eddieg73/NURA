import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
hdr = {"User-Agent": "NURA-Hermes/1.0", "x-api-key": key, "Authorization": "Bearer " + key}
try:
    req = urllib.request.Request("http://127.0.0.1:3101/api/companies?limit=1", headers=hdr)
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        cid = d["companies"][0]["id"] if d.get("companies") else "999ff375-6128-41cf-b6c8-06b98673a29b"
    req = urllib.request.Request(f"http://127.0.0.1:3101/api/companies/{cid}/issues?limit=200", headers=hdr)
    with urllib.request.urlopen(req, timeout=10) as r:
        issues = json.loads(r.read())
    items = issues.get("issues", issues if isinstance(issues, list) else [])
    found = [i for i in items if "NUR-76" in (i.get("title", "") + " " + (i.get("identifier", "") or ""))]
    print("NUR-76 found:", len(found))
    for i in found[:1]:
        print("status:", i.get("status"), "| assignee:", i.get("assigneeAgentId", "?"), "| id:", i.get("id"))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
