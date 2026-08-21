#!/usr/bin/env python3
"""NURA FLEET SWAP/MEM/DISK WATCHDOG — checks ALL 3 VPS (Clinic/Lab/Edge).
Silent when healthy (watchdog pattern). Alerts only on threshold breaches.
Triggers: swap >75% warn / >90% crit · mem avail <10% · disk >90% · swapfile MISSING = alert.
"""
import os
import subprocess
import sys

KEY = os.path.expanduser("~/.ssh/id_nura_clean")
NODES = {"CLINIC": "72.61.71.211", "LAB": "72.60.163.140", "EDGE": "195.35.32.113"}

CHECK = r"""
echo "NODE:$(hostname)"
echo "SWAP:$(free -m | grep Swap: | sed 's/  */ /g' | cut -d' ' -f3)/$(free -m | grep Swap: | sed 's/  */ /g' | cut -d' ' -f2)"
echo "MEMAV:$(free -m | grep Mem: | sed 's/  */ /g' | cut -d' ' -f7)"
echo "MEMTOT:$(free -m | grep Mem: | sed 's/  */ /g' | cut -d' ' -f2)"
echo "DISK:$(df -h / | tail -1 | sed 's/  */ /g' | cut -d' ' -f5 | tr -d '%')"
echo "SWAPFILE:$(swapon --show 2>/dev/null | tail -n +2 | wc -l)"
"""


def check(node, ip):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                        "-i", KEY, f"root@{ip}", CHECK], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return [f"{node}: SCAN FAILED ({r.stderr.strip()[:80] or r.stdout.strip()[:80]})"]
    d = {}
    for line in r.stdout.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            d[k.strip()] = v.strip()
    alerts = []
    try:
        su, st = map(int, d.get("SWAP", "0/0").split("/"))
        ma, mt = int(d.get("MEMAV", "0")), int(d.get("MEMTOT", "1"))
        disk = int(d.get("DISK", "0"))
        sf = int(d.get("SWAPFILE", "0"))
    except ValueError:
        return [f"{node}: PARSE ERROR ({d})"]
    sp = (su / st * 100) if st > 0 else 0
    if st == 0 or sf == 0:
        alerts.append(f"{node}: SWAPFILE MISSING (swap {su}/{st}MB, {sf} devices)")
    elif sp > 90:
        alerts.append(f"{node}: SWAP CRITICAL {sp:.0f}% ({su}/{st}MB)")
    elif sp > 75:
        alerts.append(f"{node}: SWAP WARNING {sp:.0f}% ({su}/{st}MB)")
    if mt > 0 and ma / mt * 100 < 10:
        alerts.append(f"{node}: MEMORY CRITICAL ({ma}/{mt}MB avail)")
    if disk > 90:
        alerts.append(f"{node}: DISK {disk}%")
    return alerts


def main():
    all_alerts = []
    for node, ip in NODES.items():
        all_alerts += check(node, ip)
    if all_alerts:
        print("FLEET ALERTS:")
        for a in all_alerts:
            print(" -", a)
    # else: SILENT (healthy)


if __name__ == "__main__":
    main()
