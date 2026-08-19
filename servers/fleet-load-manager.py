#!/usr/bin/env python3
"""Fleet load manager — score all 3 nodes + local box; print anomalies only (watchdog pattern).
Writes data/fleet-load.json. Host sensors via docker-mcp :8100-8102 when live (else local-only)."""
import json, os, time
from pathlib import Path

def load_local():
    out = {}
    try:
        with open("/proc/meminfo") as f:
            m = dict(l.split(":", 1) for l in f if l.strip())
        mem_tot = int(m.get("MemTotal", "0").split()[0]); mem_avail = int(m.get("MemAvailable", "0").split()[0])
        out["ram_used_pct"] = round(100 * (1 - mem_avail / max(mem_tot, 1)), 1)
        out["swap_used_pct"] = None
    except Exception:
        out["ram_used_pct"] = None
    try:
        st = os.statvfs("/")
        out["disk_used_pct"] = round(100 * (1 - st.f_bavail / max(st.f_blocks, 1)), 1)
    except Exception:
        out["disk_used_pct"] = None
    try:
        out["cpu_pct"] = round(float(os.popen("top -bn1 | grep 'Cpu(s)' | awk '{print $2+$4}'").read().strip() or 0), 1)
    except Exception:
        out["cpu_pct"] = None
    return out

NODES = {
    "clinic_1441409": {"ip": "72.61.71.211", "ram_gb": 16},
    "lab_1030183": {"ip": "72.60.163.140", "ram_gb": 32},
    "edge_817449": {"ip": "195.35.32.113", "ram_gb": 4},
}

def score(metrics):
    if not metrics:
        return None
    s = 0
    weights = {"ram_used_pct": 0.4, "cpu_pct": 0.3, "disk_used_pct": 0.2}
    for k, w in weights.items():
        v = metrics.get(k)
        if v is not None:
            s += w * v
    return round(s, 1)

report = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "nodes": {}}
anomalies = []

# local box = the Clinic (Hermes host node)
local = load_local()
sc = score(local)
report["nodes"]["clinic_1441409"] = {**local, "score": sc, "source": "local"}
if sc and sc >= 80:
    anomalies.append(f"clinic_1441409 RED (score {sc})")

# remote nodes via docker-mcp sensor when live (probe :8102 vps-system or fallback TCP checks)
for name, info in NODES.items():
    if name == "clinic_1441409":
        continue
    # TCP reachability only (no ssh key); full metrics need host sensor (node-agent.sh)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((info["ip"], 22))
        reach = "reachable"
    except Exception:
        reach = "down"
    finally:
        sock.close()
    report["nodes"][name] = {"reachability": reach, "score": None, "source": "tcp"}
    if reach == "down":
        anomalies.append(f"{name} DOWN (port 22)")

Path("/opt/data/profiles/nura/data/fleet-load.json").write_text(json.dumps(report, indent=1))
if anomalies:
    print("LOAD ALERT: " + " | ".join(anomalies))
# silent when healthy
