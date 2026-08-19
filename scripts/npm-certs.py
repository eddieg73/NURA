#!/usr/bin/env python3
"""Issue LE certs for chat + chatwoot and attach to the proxy hosts (ids 3, 4)."""
import json, os, urllib.request, urllib.error, time

BASE = "http://127.0.0.1:8181"

def call(method, path, body=None, token=None):
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body else None, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode()[:300] or "{}")
        except Exception:
            return e.code, {"error": str(e)}

s, d = call("POST", "/api/tokens", {"identity": os.environ["NPM_EMAIL"], "secret": os.environ["NPM_PASS"]})
if s != 200:
    print("LOGIN FAIL", s, d); raise SystemExit(1)
tok = d["token"]

for host_id, domain in [(3, "chat.nuratech.ai"), (4, "chatwoot.nuratech.ai")]:
    s, cert = call("POST", "/api/nginx/certificates", {
        "domain_names": [domain],
        "meta": {"letsencrypt_agree": True},
        "provider": "letsencrypt"}, tok)
    cert_id = cert.get("id")
    print(f"[{domain}] cert create -> {s} id={cert_id} {cert.get('error', '')}")
    if not cert_id:
        continue
    for attempt in range(6):
        time.sleep(5)
        s2, c2 = call("GET", f"/api/nginx/certificates/{cert_id}", token=tok)
        if c2.get("status") == "issued" or (c2.get("certificate") and not c2.get("error")):
            print(f"[{domain}] cert status: issued")
            break
        print(f"[{domain}] waiting... ({c2.get('status', 'unknown')})")
    s3, h3 = call("GET", f"/api/nginx/proxy-hosts/{host_id}", token=tok)
    if s3 == 200:
        h3["certificate_id"] = cert_id
        h3["ssl_forced"] = True
        h3["http2_support"] = True
        s4, up = call("PUT", f"/api/nginx/proxy-hosts/{host_id}", h3, tok)
        print(f"[{domain}] host attach -> {s4} {up.get('error', '')}")
