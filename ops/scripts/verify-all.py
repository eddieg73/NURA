#!/usr/bin/env python3
"""NURA verify-all — local stack audit. Prints PASS/FAIL per check with evidence."""
import json, subprocess, urllib.request

def http(url, timeout=6):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NURA-Hermes/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except Exception as e:
        return f"FAIL {str(e)[:60]}"

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception as e:
        return f"ERR {str(e)[:50]}"

print("== LOCAL SERVICES ==")
for name, url in [("gateway", "http://127.0.0.1:8642/health"),
                  ("paperclip", "http://127.0.0.1:3100/health"),
                  ("qdrant", "http://127.0.0.1:6333/healthz"),
                  ("mission-control", "file:///opt/data/profiles/nura/mission-control/index.html")]:
    if url.startswith("file"):
        import os
        print(f"  {name}: {'OK' if os.path.exists(url[7:]) else 'MISSING'}")
    else:
        print(f"  {name}: {http(url)}")

print("== DASHBOARD (env-gated s6 slot) ==")
import os as _os
try:
    _env = set(_os.listdir("/run/s6/container_environment"))
    if "HERMES_DASHBOARD" not in _env:
        print("  WARN: HERMES_DASHBOARD missing from container env — s6 slot down (root: echo 1 > /run/s6/container_environment/HERMES_DASHBOARD && s6-svc -u /run/service/dashboard)")
    else:
        print("  env OK (HERMES_DASHBOARD present)")
    _sv = _os.path.exists("/run/service/dashboard/supervise/status")
    print(f"  slot supervised: {_sv}")
except Exception as e:
    print(f"  ERR {e}")

print("== PUBLIC ENDPOINTS ==")
for name, url in [("n8n", "https://n8n.nuratech.ai/"), ("apex", "https://nuratech.ai/"),
                  ("pay", "https://pay.nuratech.ai/"), ("carepilot", "https://carepilot.nuratech.ai/"),
                  ("n8n-mcp", "https://n8n.nuratech.ai/mcp-server/http")]:
    print(f"  {name}: {http(url)}")

print("== RESOURCES ==")
mem = sh("free -h | head -2 | tail -1")
disk = sh("df -h /opt/data | tail -1 | awk '{print $3\"/\"$2\" (\"$5\")\"}'")
print(f"  mem: {mem}")
print(f"  disk: {disk}")

print("== PROCESSES ==")
gw = sh("ps aux | grep -c '[g]ateway run'")
pp = sh("ps aux | grep -c '[p]aperclipai'")
print(f"  gateway procs: {gw} | paperclip procs: {pp}")

print("== SLA LEDGER (last 3) ==")
try:
    lines = open("/opt/data/profiles/nura/data/uptime/paperclip.log").read().strip().splitlines()[-3:]
    for l in lines:
        print(f"  {l}")
except Exception as e:
    print(f"  ERR {e}")

print("== CRON ERROR COUNT ==")
try:
    d = json.load(open("/opt/data/profiles/nura/cron/jobs.json"))
    jobs = d if isinstance(d, list) else d.get("jobs", [])
    errs = [j for j in jobs if j.get("last_status") and "error" in str(j.get("last_status")).lower()]
    print(f"  jobs: {len(jobs)} | with last error: {len(errs)}")
except Exception as e:
    print(f"  ERR {e}")

print("== FREE LANES ==")
try:
    st = json.load(open("/opt/data/profiles/nura/data/lessons/free-lanes.json"))
    healthy = sum(1 for v in st.values() if v.get("healthy"))
    print(f"  {healthy}/{len(st)} healthy")
except Exception as e:
    print(f"  ERR {e}")

print("== MEMORY ==")
k = sh("wc -c /opt/data/profiles/nura/memories/MEMORY.md /opt/data/profiles/nura/memories/USER.md | tail -1")
print(f"  kernel store: {k}")
