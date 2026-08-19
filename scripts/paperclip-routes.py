import json, urllib.request, urllib.error

def env(name):
    try:
        for line in open("/opt/data/profiles/nura/.env"):
            if line.startswith(name + "="):
                return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env("PAPERCLIP_API_KEY") or env("PAPERCLIP_KEY") or env("NUR_API_KEY")
hdr = {"User-Agent": "NURA-Hermes/1.0"}
if key:
    hdr["x-api-key"] = key
    hdr["Authorization"] = "Bearer " + key

paths = [
    "/api/agents",
    "/api/agents?limit=5",
    "/api/companies",
    "/api/companies?limit=3",
    "/api/organizations",
    "/api/companies/999ff375-6128-41cf-b6c8-06b98673a29b",
    "/api/companies/999ff375/agents",
    "/api/company/999ff375-6128-41cf-b6c8-06b98673a29b/agents",
    "/api/v1/agents",
]
for p in paths:
    try:
        req = urllib.request.Request("http://127.0.0.1:3100" + p, headers=hdr)
        with urllib.request.urlopen(req, timeout=6) as r:
            print(p, "->", r.status, r.read().decode()[:160].replace("\n", " "))
    except urllib.error.HTTPError as e:
        print(p, "->", e.code)
    except Exception as e:
        print(p, "-> ERR", str(e)[:80])
