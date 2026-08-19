#!/usr/bin/env python3
"""Query Paperclip API (port 3101 — the LIVE fork per memory-archive) for issues."""
import json, urllib.request, urllib.error, sys, re

# Try both 3100 and 3101
for port in [3101, 3100]:
    try:
        url = f"http://127.0.0.1:{port}/api/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            print(f"PORT {port}: HEALTH OK — {json.dumps(data, indent=2)[:300]}")
    except Exception as e:
        print(f"PORT {port}: {type(e).__name__}: {e}")

# Try listing companies on 3101
base = "http://127.0.0.1:3101"
try:
    req = urllib.request.Request(base + "/api/companies")
    req.add_header("User-Agent", "NURA-Hermes/1.0")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=5) as r:
        data = json.loads(r.read())
        print(f"\nCompanies (3101): {json.dumps(data, indent=2)[:2000]}")
except Exception as e:
    print(f"Companies 3101: {type(e).__name__}: {e}")

# Try with auth from env
def envval(name):
    try:
        env = open("/opt/data/profiles/nura/.env").read()
        m = re.search(rf"^{name}=(.+)$", env, re.M)
        return m.group(1).strip().strip('"').strip("'") if m else ""
    except Exception as e:
        print(f"env read error: {e}")
        return ""

key = envval("API_SERVER_KEY")
if key:
    hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
           "x-api-key": key, "Authorization": "Bearer " + key}
    try:
        req = urllib.request.Request(base + "/api/companies", headers=hdr)
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            print(f"\nCompanies (3101 AUTH): {json.dumps(data, indent=2)[:2000]}")
    except Exception as e:
        print(f"Companies 3101 AUTH: {type(e).__name__}: {e}")
        if isinstance(e, urllib.error.HTTPError):
            print(f"  Body: {e.read().decode()[:500]}")
else:
    print("NO API KEY FOUND in .env")
