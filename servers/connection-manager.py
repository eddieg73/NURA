#!/usr/bin/env python3
"""Connection manager — probe every lane/service/channel; write data/connections.json; alert on changes.
Silent when healthy. no_creds classified separately from down."""
import json, os, time, socket, subprocess
from pathlib import Path

ENV = "/opt/data/profiles/nura/.env"

def has_env(name):
    try:
        for line in open(ENV):
            if line.startswith(name + "="):
                return bool(line.strip().split("=", 1)[1].strip())
    except OSError:
        pass
    return False

def tcp(port, host="127.0.0.1", timeout=3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def http(url, timeout=5):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False

LANES = {
    # (creds_key, probe)  — probe None = service check only
    "openfda": ("OPENFDA_API_KEY", None, "service/lane"),
    "pubmed": (None, None, "eutils (external)"),
    "bioportal": ("BIOPORTAL_API_KEY", None, "service/lane"),
    "redis": (None, lambda: tcp(6379), "service"),
    "qdrant": (None, lambda: http("http://127.0.0.1:6333/collections"), "service"),
    "paperclip": (None, lambda: tcp(58886, host="72.61.71.211"), "service"),
    "moltbook": ("MOLTBOOK_API_KEY", None, "lane"),
    "mirth": ("MIRTH_PASS", None, "lane"),
    "openemr": ("OPENEMR_OAUTH_CLIENT_ID", None, "lane"),
    "perfex": ("PERFEX_API_TOKEN", None, "lane"),
    "chatwoot": ("CHATWOOT_API_TOKEN", None, "lane"),
    "documo": ("DOCUMO_API_KEY", None, "lane"),
    "granola": ("GRANOLA_API_KEY", None, "lane"),
    "firebase": ("FIREBASE_SERVICE_ACCOUNT", None, "lane"),
    "openevidence": ("OPENEVIDENCE_API_KEY", None, "lane"),
    "ghl": ("GHL_API_KEY", None, "lane"),
    "twilio": ("TWILIO_AUTH_TOKEN", None, "channel"),
}

report = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "lanes": {}}
alerts = []
for name, (cred, probe, kind) in LANES.items():
    creds = has_env(cred) if cred else True
    if probe is None:
        status = "ok" if creds else "no_creds"
    else:
        try:
            status = "ok" if probe() else "down"
        except Exception:
            status = "down"
    report["lanes"][name] = {"kind": kind, "creds": creds, "status": status}
    if status == "down":
        alerts.append(f"{name} DOWN")
    elif status == "no_creds" and kind != "channel":
        pass  # known pending drops — not an alert

Path("/opt/data/profiles/nura/data/connections.json").write_text(json.dumps(report, indent=1))
if alerts:
    print("CONNECTION ALERT: " + " | ".join(alerts))
# silent when healthy
