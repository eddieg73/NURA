#!/usr/bin/env python3
"""
RunPod lane CLI — the missing third surface (API + MCP + **CLI** + webhook).

Why this exists: the RunPod lane was `enabled: true` with an invalid key for an unknown
period and nothing surfaced it. A lane that is enabled but dead must fail loudly. This
script is the deterministic probe: `status`, `probe`, `catalog`, `pods`.

    python3 scripts/runpod-lane.py status     # exit 0 = usable, 1 = not
    python3 scripts/runpod-lane.py probe      # per-surface detail
    python3 scripts/runpod-lane.py catalog    # GPU catalog (needs a live key)

Silent-OK doctrine: prints nothing and exits 0 only when everything is healthy, so it can
run from cron without generating noise.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

ENV_FILE = "/opt/data/profiles/nura/.env"
CFG_FILE = "/opt/data/profiles/nura/config.yaml"

# RunPod ships two different APIs one letter apart. Do not conflate them.
V2_CONTROL_PLANE = "https://api.runpod.io/v2"      # REST v2 (pods/serverless/catalog/billing)
V1_REST = "https://rest.runpod.io/v1"              # deprecated, retires 2026-11-15
V1_GRAPHQL = "https://api.runpod.io/graphql"       # legacy
SERVERLESS_JOBS = "https://api.runpod.ai/v2"       # NOT migrating, different API

# Cloudflare (error 1010) blocks default user-agents. A browser UA is required to reach
# the API host at all; without it every request 403s and looks like an auth failure.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def load_key() -> str | None:
    """Read the key from .env (the wrapper's source of truth), never from config.yaml."""
    key = os.getenv("RUNPOD_API_KEY")
    if key:
        return key.strip()
    try:
        raw = open(ENV_FILE, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    m = re.search(r"^RUNPOD_API_KEY=(.+)$", raw, re.M)
    return m.group(1).strip().strip("'\"") if m else None


def call(url: str, key: str, method: str = "GET", body: dict | None = None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body else None
    headers = {"Authorization": f"Bearer {key}", "Accept": "application/json",
               "User-Agent": UA}
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()[:400]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:  # noqa: BLE001 - surface anything else as a probe result
        return 0, f"{type(e).__name__}: {e}"


def probe() -> list[dict]:
    key = load_key()
    results: list[dict] = []

    results.append({
        "surface": "credential",
        "target": ".env RUNPOD_API_KEY",
        "ok": bool(key),
        "detail": f"present, len={len(key)}" if key else "MISSING",
    })
    if not key:
        return results

    checks = [
        ("API v2 control plane", f"{V2_CONTROL_PLANE}/pods"),
        ("API v1 REST (deprecated 2026-11-15)", f"{V1_REST}/pods"),
        ("GPU catalog (v2)", f"{V2_CONTROL_PLANE}/catalog/gpus?include=AVAILABILITY&product=POD"),
        ("Billing (v2)", f"{V2_CONTROL_PLANE}/billing"),
    ]
    for name, url in checks:
        code, body = call(url, key)
        results.append({
            "surface": "api",
            "target": name,
            "ok": 200 <= code < 300,
            "detail": f"HTTP {code} {body[:110]}",
        })

    code, body = call(V1_GRAPHQL, key, "POST", {"query": "{ myself { id } }"})
    results.append({
        "surface": "api",
        "target": "GraphQL (canonical key check)",
        "ok": 200 <= code < 300 and '"errors"' not in body,
        "detail": f"HTTP {code} {body[:110]}",
    })
    return results


def cmd_status() -> int:
    results = probe()
    bad = [r for r in results if not r["ok"]]
    if not bad:
        return 0  # silent-OK
    print("RunPod lane NOT healthy:")
    for r in bad:
        print(f"  x {r['surface']:<10} {r['target']:<38} {r['detail']}")
    return 1


def cmd_probe() -> int:
    for r in probe():
        mark = "OK " if r["ok"] else "FAIL"
        print(f"  [{mark}] {r['surface']:<10} {r['target']:<38} {r['detail']}")
    return cmd_status()


def cmd_catalog() -> int:
    key = load_key()
    if not key:
        print("no key"); return 1
    code, body = call(f"{V2_CONTROL_PLANE}/catalog/gpus?include=AVAILABILITY&product=POD", key)
    if not (200 <= code < 300):
        print(f"catalog unavailable: HTTP {code} {body[:200]}"); return 1
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(body[:400]); return 1
    rows = data if isinstance(data, list) else data.get("data") or data.get("gpus") or []
    print(f"{len(rows)} GPU types")
    for g in rows[:25]:
        if isinstance(g, dict):
            print(f"  {g.get('id') or g.get('name')}  {g.get('displayName','')}")
    return 0


def cmd_pods() -> int:
    key = load_key()
    if not key:
        print("no key"); return 1
    code, body = call(f"{V2_CONTROL_PLANE}/pods", key)
    if not (200 <= code < 300):
        print(f"pods unavailable: HTTP {code} {body[:200]}"); return 1
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(body[:400]); return 1
    rows = data if isinstance(data, list) else data.get("data") or data.get("pods") or []
    print(f"{len(rows)} pods")
    for p in rows:
        if isinstance(p, dict):
            print(f"  {p.get('id')}  {p.get('name','')}  {p.get('status') or p.get('desiredStatus','')}")
    return 0


COMMANDS = {"status": cmd_status, "probe": cmd_probe,
            "catalog": cmd_catalog, "pods": cmd_pods}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    fn = COMMANDS.get(cmd)
    if not fn:
        print(f"usage: {sys.argv[0]} [{'|'.join(COMMANDS)}]", file=sys.stderr)
        sys.exit(2)
    sys.exit(fn())
