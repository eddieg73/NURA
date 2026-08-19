#!/usr/bin/env python3
import json, os, urllib.request, urllib.error
BASE = "http://127.0.0.1:8181"
def call(method, path, body=None, token=None):
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body else None, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()[:200] or "{}")
s, d = call("POST", "/api/tokens", {"identity": os.environ["NPM_EMAIL"], "secret": os.environ["NPM_PASS"]})
if s != 200:
    print("NPM LOGIN FAIL", s, d); raise SystemExit(1)
token = d["token"]
s, d = call("POST", "/api/nginx/proxy-hosts", {
    "domain_names": ["chat.nuratech.ai"], "forward_scheme": "http",
    "forward_host": "127.0.0.1", "forward_port": 32777,
    "certificate_id": None, "ssl_forced": False, "http2_support": False,
    "block_exploits": True, "caching_enabled": False, "allow_websocket_upgrade": True,
    "advanced_config": "", "access_list_id": 0,
    "meta": {"letsencrypt_agree": False, "dns_challenge": False}, "enabled": True}, token)
print("chat.nuratech.ai proxy ->", s, d.get("id", d.get("error", d)))
