import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"

def get(path):
    req = urllib.request.Request(base + path, headers=hdr)
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

try:
    issues = get(f"/api/companies/{cid}/issues")
    if isinstance(issues, dict):
        issues = issues.get("issues", issues.get("data", []))
    for it in issues:
        t = (it.get("title") or "")
        if "APP PRIORITY" in t.upper() or "SAAS-IFY" in t.upper() or "TestFlight" in t:
            print("ID:", it.get("id"))
            print("TITLE:", t[:90])
            print("STATUS:", it.get("status"), "| PRIORITY:", it.get("priority"))
            print("ASSIGNEE:", it.get("assigneeAgentId", "?"))
            print("UPDATED:", it.get("updatedAt", "?"))
            print("---")
except Exception as e:
    print("ERR:", e)
