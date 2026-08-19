#!/usr/bin/env python3
"""NURA Docker verification — silent when healthy, alerts on failures.
Checks: daemon state, expected containers (from canonical compose files),
and endpoint probes for every service. Watchdog-safe (exit 0, empty stdout = OK).
"""
import json, os, re, subprocess, sys, urllib.request
from pathlib import Path

COMPOSES = [
    "/opt/data/saas-stack/docker-compose.yml",
    "/opt/data/mirth-docker-stack/docker-compose.yml",
    "/opt/data/imaging-stack/docker-compose.pacs.yml",
    "/opt/data/home/behive/docker-compose.yml",
]
# endpoint probes: (name, url, expected_http_codes)
ENDPOINTS = [
    ("n8n",        "https://n8n.nuratech.ai",        {200, 302}),
    ("pay",        "https://pay.nuratech.ai",        {200, 307, 302}),
    ("carepilot",  "https://carepilot.nuratech.ai",  {200, 302}),
    ("openfda-mcp","https://openfda.caseyjhand.com/mcp", {200, 405}),
]

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""

def expected_services():
    svcs = set()
    for p in COMPOSES:
        if not Path(p).exists():
            continue
        try:
            import yaml
            d = yaml.safe_load(open(p))
            for k, v in (d.get("services") or {}).items():
                if isinstance(v, dict):
                    svcs.add(k)
        except Exception:
            pass
    return sorted(svcs)

alerts = []

# 1. Docker daemon
daemon = sh("docker ps --format '{{.Names}}' 2>/dev/null | head -1")
if daemon:
    running = sh("docker ps --format '{{.Names}}'").splitlines()
    expected = expected_services()
    missing = [s for s in expected if s not in running and s not in ("npm",)]
    if missing:
        alerts.append(f"DOCKER: containers not running: {', '.join(missing)}")
else:
    print("DOCKER SKIP: no engine on Hermes box (expected; verify via docker-mcp lane on host 1441409)")
# 2. Endpoint sweep
for name, url, codes in ENDPOINTS:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NURA-Hermes/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.status
        if code not in codes:
            alerts.append(f"ENDPOINT {name}: HTTP {code} (expected {sorted(codes)})")
    except Exception as e:
        alerts.append(f"ENDPOINT {name}: unreachable ({str(e)[:60]})")

# 3. Local services
for name, port in [("qdrant", 6333), ("paperclip", 3100), ("gateway", 8642)]:
    if sh(f"curl -s -m 4 -o /dev/null -w '%{{http_code}}' http://127.0.0.1:{port}/") == "000":
        alerts.append(f"LOCAL {name}: :{port} not responding")

if alerts:
    print("DOCKER VERIFY FAIL:")
    for a in alerts:
        print(" -", a)
