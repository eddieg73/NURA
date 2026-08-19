#!/usr/bin/env python3
"""NURA FLEET INVENTORY + HEALTH ENGINE (the directive §1-2, 3.2) — machine-readable, re-runnable.
Discovers every container/project/port across the 3-node fleet + probes critical endpoints.
Output: JSON inventory at ~/nura-ops/inventory.json + a flat status line (for the cron watchdog)."""
import json, subprocess, socket, sys, os, datetime

NODES = {
    "clinic":  {"host": "72.61.71.211", "ssh": "root@72.61.71.211"},
    "lab":     {"host": "72.60.163.140", "ssh": "root@72.60.163.140"},
    "edge":    {"host": "195.35.32.113", "ssh": "root@195.35.32.113"},
}
KEY = os.path.expanduser("~/.ssh/id_nura_clean")
OUT = os.path.expanduser("~/nura-ops/inventory.json")
CRITICAL = [  # (name, host, port, expected-http-prefix)
    ("api.nuratech.ai", "api.nuratech.ai", 80, ""),
    ("hermes-gateway", "72.61.71.211", 8642, ""),
    ("orthanc", "72.61.71.211", 8042, ""),
    ("mirth", "72.61.71.211", 8444, ""),
    ("npm", "72.61.71.211", 8181, ""),
    ("mattermost", "72.61.71.211", 32777, ""),
    ("redis", "72.61.71.211", 32772, ""),
    ("qdrant", "72.61.71.211", 32769, ""),
    ("openemr", "72.61.71.211", 32776, ""),
]

def ssh(node, cmd, timeout=25):
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                            "-i", KEY, node["ssh"], cmd], capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR {e}"

def probe(host, port, timeout=4):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "open"
    except Exception:
        return "closed"

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    inventory = {"generated": datetime.datetime.utcnow().isoformat() + "Z", "nodes": {}}
    status_line = []
    for name, node in NODES.items():
        out = ssh(node, "docker ps -a --format '{{.Names}}|{{.Status}}|{{.Ports}}' 2>/dev/null | head -40; echo '---'; free -m | awk 'NR==2{print \"mem_used_mb=\"$3\"/\"$2}'; df -h / | awk 'NR==2{print \"disk=\"$5}'")
        containers = []
        mem = disk = "?"
        for line in out.splitlines():
            if line.startswith("mem_used_mb="):
                mem = line.split("=")[1]
            elif line.startswith("disk="):
                disk = line.split("=")[1]
            elif "|" in line:
                cname, cstatus, cports = line.split("|", 2)
                containers.append({"name": cname, "status": cstatus, "ports": cports})
        inventory["nodes"][name] = {"host": node["host"], "containers": containers, "mem": mem, "disk": disk}
        up = sum(1 for c in containers if "Up" in c["status"])
        status_line.append(f"{name}:{up}/{len(containers)}up")
    # Critical endpoint probes
    probes = {}
    for name, host, port, _ in CRITICAL:
        probes[name] = probe(host, port)
    inventory["endpoints"] = probes
    unhealthy = [n for n, s in probes.items() if s != "open"]
    with open(OUT, "w") as f:
        json.dump(inventory, f, indent=2)
    line = " | ".join(status_line) + f" | endpoints: {sum(1 for s in probes.values() if s=='open')}/{len(probes)} open"
    if unhealthy:
        line += " | UNHEALTHY: " + ",".join(unhealthy)
    print(line)
    sys.exit(1 if unhealthy else 0)

if __name__ == "__main__":
    main()
