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

RENAME = {
    "RCM Billing Lead": "Midas",
    "Customer Success Lead": "Nova",
    "HR Ops Lead": "Harmony",
    "Infrastructure SRE Lead": "Sentinel",
    "Docker Platform Lead": "Helm",
    "GoHighLevel Integration Specialist": "Relay",
    "Mobile Release & Store Lead": "Beacon",
    "Doximity App Flutter Lead": "Pixel",
    "Doximity App Backend Lead": "Forge",
    "Wearables & Bluetooth Developer": "Pulse",
    "Integrations Specialist": "Weaver",
    "Flutter Mobile Lead": "Canvas",
    "Compliance SecOps Lead": "Vigil",
    "NextGen Mirth Integration Developer": "Meridian",
}

try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", headers=hdr)
    with urllib.request.urlopen(req, timeout=8) as r:
        agents = json.loads(r.read())
except Exception as e:
    print("LIST ERR", str(e)[:100]); raise SystemExit

by_name = {a.get("name"): a.get("id") for a in agents}
ok = fail = 0
for orig, new in RENAME.items():
    aid = by_name.get(orig)
    if not aid:
        print(f"SKIP {orig} (not found)"); fail += 1; continue
    try:
        req = urllib.request.Request(base + f"/api/agents/{aid}",
                                     data=json.dumps({"name": new}).encode(),
                                     headers=hdr, method="PATCH")
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
            print(f"{new} <- {d.get('name', '?')}")
            ok += 1
    except Exception as e:
        print(f"FAIL {orig}: {str(e)[:80]}"); fail += 1
print(f"RENAMED {ok}/{len(RENAME)} (fail {fail})")
