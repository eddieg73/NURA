#!/usr/bin/env python3
"""Emergency escalation dispatcher — builds the canonical CRITICAL payload and
delivers out-of-band. Cron/watchdog: prints payload (delivered to Telegram+email).
Optional webhook: WEBHOOK_URL in .env (Discord/Slack generic). Ledger: data/uptime/escalations.log"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

def env(name):
    try:
        for line in open("/opt/data/profiles/nura/.env"):
            if line.startswith(name + "="):
                return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

def main():
    service = sys.argv[1] if len(sys.argv) > 1 else "unknown-service"
    signature = sys.argv[2] if len(sys.argv) > 2 else "unclassified"
    attempts = sys.argv[3] if len(sys.argv) > 3 else "5"
    payload = {
        "severity": "CRITICAL",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "service": service,
        "error_signature": signature,
        "circuit_breaker_attempts": attempts,
        "notion_incident_id": "pending-notion-link",
        "action_required": "Manual human intervention required. Autonomous mutation halted to prevent data corruption.",
    }
    # Ledger (append-only)
    os.makedirs("/opt/data/profiles/nura/data/uptime", exist_ok=True)
    with open("/opt/data/profiles/nura/data/uptime/escalations.log", "a") as f:
        f.write(json.dumps(payload) + "\n")
    # Optional generic webhook (Discord/Slack)
    url = env("WEBHOOK_URL")
    if url:
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10):
                pass
        except Exception as e:
            print(f"webhook-fail: {str(e)[:80]}")
    # Print for cron delivery (Telegram + email OOB)
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    main()
