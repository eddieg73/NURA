#!/usr/bin/env python3
"""Fix NPM host 5: forward_host 127.0.0.1 -> hermes-gateway (same docker network)."""
import json, os, urllib.request, urllib.error

BASE = "http://127.0.0.1:8181"
E = os.environ.get("NPM_EMAIL", "")
P = os.environ.get("NPM_PASS", "")

def call(path, method="GET", data=None, tok=None):
    hdr = {"Content-Type": "application/json"}
    if tok:
        hdr["Authorization"] = "Bearer " + tok
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode() if data else None, headers=hdr, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode()[:200] if e.code != 401 else "auth")

s, tok = call("/api/tokens", "POST", {"identity": E, "secret": P})
if s != 200:
    print("auth failed:", tok); raise SystemExit(1)
tok = tok["token"]

s, host = call("/api/nginx/proxy-hosts/5", tok=tok)
print("get host5:", s)
if s == 200:
    host["forward_host"] = "hermes-gateway"
    s2, upd = call("/api/nginx/proxy-hosts/5", "PUT", host, tok)
    print("update:", s2, upd.get("forward_host", upd) if isinstance(upd, dict) else upd)
