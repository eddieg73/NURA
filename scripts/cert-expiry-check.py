#!/usr/bin/env python3
"""SSL/TLS cert expiry checker — probes public endpoints, alerts when < 14 days to expiry.
Silent when all healthy (watchdog pattern). Exit 0 always."""
import ssl, socket, sys
from datetime import datetime, timezone

ENDPOINTS = ["nuratech.ai", "n8n.nuratech.ai", "pay.nuratech.ai", "carepilot.nuratech.ai",
             "emr.nuratech.ai", "chatwoot.nuratech.ai", "pacs.nuratech.ai", "viewer.nuratech.ai"]
WARN_DAYS = 14

def check(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as tls:
                cert = tls.getpeercert()
        exp = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
        days = (exp - datetime.now(timezone.utc)).days
        return days, cert.get("subject", ((("commonName", host),),))[0][0][1]
    except Exception as e:
        return None, f"ERR {str(e)[:60]}"

alerts = []
for h in ENDPOINTS:
    days, info = check(h)
    if days is None:
        alerts.append(f"CHECK FAIL {h}: {info}")
    elif days < 0:
        alerts.append(f"EXPIRED {h} ({info}) {abs(days)}d ago")
    elif days <= WARN_DAYS:
        alerts.append(f"EXPIRING {h} ({info}): {days}d left")

if alerts:
    print("SSL CERT ALERT\n" + "\n".join(alerts))
