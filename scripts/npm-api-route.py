#!/usr/bin/env python3
"""Create the NPM proxy host: api.nuratech.ai -> gateway 127.0.0.1:8642 (HTTP, no cert needed for the desktop client)."""
import json, os, urllib.request, urllib.error

def env_val(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

BASE = "http://127.0.0.1:8181"

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

E = env_val("/opt/data/profiles/nura/.env", ["NPM_ADMIN_EMAIL"])
P = env_val("/opt/data/profiles/nura/.env", ["NPM_ADMIN_PASS"])
s, tok = call("/api/tokens", "POST", {"identity": E, "secret": P})
print("token:", s)
if s != 200:
    print("auth failed:", tok)
    raise SystemExit(1)
tok = tok["token"]

s, hosts = call("/api/nginx/proxy-hosts", tok=tok)
print("existing hosts:", s, len(hosts) if isinstance(hosts, list) else hosts)

payload = {
    "domain_names": ["api.nuratech.ai"],
    "forward_scheme": "http",
    "forward_host": "127.0.0.1",
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
s, new = call("/api/nginx/proxy-hosts", "POST", payload, tok)
print("create:", s, new.get("id", new) if isinstance(new, dict) else new)
