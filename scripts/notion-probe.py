import json, re, urllib.request, urllib.error

env = open("/opt/data/profiles/nura/.env").read()
m = re.search(r"^NOTION_API_TOKEN=(.+)$", env, re.M)
tok = m.group(1).strip().strip('"').strip("'") if m else ""
print("token present:", bool(tok), "| len:", len(tok))

if not tok:
    raise SystemExit(0)

def call(path, method="GET"):
    req = urllib.request.Request("https://api.notion.com/v1" + path, method=method,
                                 headers={"Authorization": "Bearer " + tok,
                                          "Notion-Version": "2022-06-28",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

st, me = call("/users/me")
print("GET /users/me ->", st)
if st == 200:
    print("user:", me.get("name"), "| type:", me.get("type"), "| bot:", me.get("bot", {}).get("owner", {}).get("type"))
    st2, search = call("/search", "POST") if False else (None, None)
    req2 = urllib.request.Request("https://api.notion.com/v1/search", method="POST",
                                  headers={"Authorization": "Bearer " + tok,
                                           "Notion-Version": "2022-06-28",
                                           "Content-Type": "application/json"},
                                  data=json.dumps({"page_size": 10}).encode())
    try:
        with urllib.request.urlopen(req2, timeout=20) as r2:
            d2 = json.loads(r2.read().decode())
            print("search ->", r2.status, "| results:", len(d2.get("results", [])))
            for r_ in d2.get("results", [])[:10]:
                obj = r_.get("object")
                title = ""
                props = r_.get("properties") or {}
                for v in props.values():
                    if v.get("type") == "title" and v.get("title"):
                        title = "".join(t.get("plain_text", "") for t in v["title"])
                        break
                print("  -", obj, "|", title[:60])
    except urllib.error.HTTPError as e2:
        print("search ->", e2.code, e2.read().decode()[:150])
else:
    print("body:", json.dumps(me)[:200])
