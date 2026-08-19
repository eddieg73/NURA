import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
hdr = {"User-Agent": "NURA-Hermes/1.0", "x-api-key": key, "Authorization": "Bearer " + key}
base = "http://127.0.0.1:3101"

for iid in ["fa0f9bb7-c478-4ee8-945f-e80c824a91a2"]:
    try:
        req = urllib.request.Request(base + f"/api/issues/{iid}", headers=hdr)
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print("status:", d.get("status"), "| priority:", d.get("priority"), "| assignee:", d.get("assigneeAgentId"))
            print("updated:", d.get("updatedAt", d.get("updated_at", "?")))
            c = d.get("comments") or []
            print("comments:", len(c))
            for x in c[-3:]:
                print("  -", (x.get("body") or "")[:100].replace("\n", " "))
    except urllib.error.HTTPError as e:
        print("issue", iid[:8], "->", e.code, e.read().decode()[:150])
