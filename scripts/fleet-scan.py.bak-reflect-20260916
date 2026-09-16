#!/usr/bin/env python3
"""Fleet scan — network-engineer assessment of all 3 VPS (read-only)."""
import json
import os
import subprocess
import sys

KEY = os.path.expanduser("~/.ssh/id_nura_clean")
NODES = {
    "CLINIC": ("72.61.71.211", "1441409"),
    "LAB": ("72.60.163.140", "1030183"),
    "EDGE": ("195.35.32.113", "817449"),
}

SCAN = r"""
echo "LOAD:$(cat /proc/loadavg | cut -d' ' -f1-3)"
echo "MEM:$(free -m | grep Mem: | sed 's/  */ /g' | cut -d' ' -f3)/$(free -m | grep Mem: | sed 's/  */ /g' | cut -d' ' -f2)"
echo "SWAP:$(free -m | grep Swap: | sed 's/  */ /g' | cut -d' ' -f3)/$(free -m | grep Swap: | sed 's/  */ /g' | cut -d' ' -f2)"
echo "DISK:$(df -h / | tail -1 | sed 's/  */ /g' | cut -d' ' -f3)/$(df -h / | tail -1 | sed 's/  */ /g' | cut -d' ' -f2)"
echo "UPTIME:$(uptime -p | sed 's/up //')"
echo "CONTAINERS:$(docker ps -q 2>/dev/null | wc -l)"
echo "EXPOSED:$(ss -tln 2>/dev/null | awk '{print $4}' | grep -E '^0\.0\.0\.0|^\[::\]' | grep -v ':22$' | sed 's/.*://' | sort -u | tr '\n' ',')"
echo "DOCKER_ERR:$(docker ps 2>&1 >/dev/null | head -1)"
"""


def scan(node, ip, vid):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                        "-i", KEY, f"root@{ip}", SCAN], capture_output=True, text=True, timeout=40)
    out = {}
    if r.returncode != 0:
        return {"node": node, "id": vid, "error": r.stderr.strip()[:120] or r.stdout.strip()[:120]}
    for line in r.stdout.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return {"node": node, "id": vid, **out}


def main():
    results = [scan(n, ip, vid) for n, (ip, vid) in NODES.items()]
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
