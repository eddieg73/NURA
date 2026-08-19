#!/usr/bin/env python3
"""Fix NPM host 5 forward (minimal PUT payload)."""
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
        return e.code, (e.read().decode()[:250] if e.code != 401 else "auth")

s, tok = call("/api/tokens", "POST", {"identity": E, "secret": P})
if s != 200:
    print("auth failed:", tok); raise SystemExit(1)
tok = tok["token"]

payload = {
    "domain_names": ["api.nuratech.ai"],
    "forward_scheme": "http",
    "forward_host": "hermes-gateway",
    "forward_port": 8642,
    "access_list_id": 0,
    "certificate_id": None,
    "ssl_forced": False,
    "block_exploits": True,
    "caching_enabled": False,
    "allow_websocket_upgrade": True,
    "http2_support": False,
    "hsts_enabled": False,
    "hsts_subdomains": False,
    "meta": {"letsencrypt_agree": False, "dns_challenge": False},
    "advanced_config": "",
    "locations": [],
}
s2, upd = call("/api/nginx/proxy-hosts/5", "PUT", payload, tok)
print("update:", s2, upd.get("forward_host", upd) if isinstance(upd, dict) else upd)
