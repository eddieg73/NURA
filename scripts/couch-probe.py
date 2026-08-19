import json, urllib.request, urllib.error, base64

def get(path, auth=None, timeout=20):
    req = urllib.request.Request("http://72.61.71.211:5984" + path)
    if auth:
        cred = base64.b64encode(auth.encode()).decode()
        req.add_header("Authorization", "Basic " + cred)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200]
    except Exception as e:
        return 0, str(e)[:150]

creds = {}
for line in open("/opt/data/uploads/couchdb-credentials.txt"):
    line = line.strip()
    if "=" in line and line.split("=", 1)[0] in ("COUCHDB_USER", "COUCHDB_PASSWORD"):
        k, v = line.split("=", 1)
        creds[k] = v

print("welcome:", get("/"))
s, b = get("/_up", auth=f"{creds.get('COUCHDB_USER','')}:{creds.get('COUCHDB_PASSWORD','')}")
print("auth _up:", s)
s2, _ = get("/_membership")
print("unauth _membership:", s2, "(401 = auth enforced)")
print("user db check:", get("/_session", auth=f"{creds.get('COUCHDB_USER','')}:{creds.get('COUCHDB_PASSWORD','')}")[0])
