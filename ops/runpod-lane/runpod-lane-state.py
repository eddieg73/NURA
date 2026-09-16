#!/usr/bin/env python3
"""
Deterministic RunPod lane state — for the cron monitor gate.

Emits a STABLE string for a given health state so the cron monitor only fires when the
state CHANGES. No timestamps, no ordering noise: otherwise every tick looks "different"
and the watchdog floods.

Deliberately does NOT include the key, the account id, or anything volatile.
"""
import hashlib
import re
import sys
import os
import urllib.error
import urllib.request

ENV_FILE = "/opt/data/profiles/nura/.env"
CFG_FILE = "/opt/data/profiles/nura/config.yaml"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def key():
    v = os.getenv("RUNPOD_API_KEY")
    if v:
        return v.strip()
    try:
        raw = open(ENV_FILE, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    m = re.search(r"^RUNPOD_API_KEY=(.+)$", raw, re.M)
    return m.group(1).strip().strip("'\"") if m else None


def code_of(url, k):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {k}", "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


parts = []

# 1. is the provider URL still a placeholder / still wrong?
try:
    cfg = open(CFG_FILE, encoding="utf-8", errors="replace").read()
    m = re.search(r"^  runpod:\n    api_key_env: \S+\n    base_url: (\S+)\n", cfg, re.M)
    url = m.group(1) if m else "MISSING"
except OSError:
    url = "UNREADABLE"

if url == "MISSING":
    parts.append("provider-url=MISSING")
elif "ENDPOINT_ID_NOT_SET" in url:
    parts.append("provider-url=placeholder-no-endpoint")
elif "/openai/v1" in url:
    parts.append("provider-url=ok")
else:
    parts.append("provider-url=WRONG-SHAPE")

# 2. is the key present, and is it accepted by the API?
k = key()
if not k:
    parts.append("key=MISSING")
else:
    parts.append(f"key=len{len(k)}:sha{hashlib.sha256(k.encode()).hexdigest()[:8]}")
    c = code_of("https://api.runpod.io/v2/pods", k)
    parts.append(f"v2={c}")
    parts.append("auth=OK" if c in (200, 403) else f"auth=FAIL{c}")

print(" | ".join(parts))
sys.exit(0)
