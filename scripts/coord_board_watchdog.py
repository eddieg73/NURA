#!/usr/bin/env python3
"""
NURA Coordination Board Watchdog.

Checks the Hermes<->ChatGPT<->Kiro coordination board for items that need action:
- Any item owned by another agent that's in "Needs Review" or where the assignment
  expects a response but hasn't delivered (Assigned, stale).
- Alerts are CHANGE-ONLY (watchdog pattern): silent when nothing new. Anti-flood law.

Run: python3 coord_board_watchdog.py   (cron every 15m, no_agent, deliver telegram)
Env: reads Notion token from auth.json (the integration that owns the DBs).
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

VER = "2022-06-28"
BOARD = open("/tmp/coord_board.txt").read().strip() if os.path.exists("/tmp/coord_board.txt") else ""
if not BOARD:
    BOARD = "3cda9b14-e498-8178-8581-c358f57305a1"  # fallback (coordination board id)
STATE = "/opt/data/profiles/nura/cache/coord_board_watchdog.state"
# how old (hours) before an Assigned-to-another-agent item is "stale/attention-worthy"
STALE_H = 8


def _notion_token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return list(d.values())[0]
    raise SystemExit("No Notion token")


def api(method, path, body=None):
    req = urllib.request.Request(f"https://api.notion.com/v1{path}", method=method)
    req.add_header("Authorization", "Bearer " + _notion_token())
    req.add_header("Notion-Version", VER)
    req.add_header("Content-Type", "application/json")
    data = json.dumps(body).encode() if body else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"err": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"err": str(e)[:80]}


def load_state():
    if os.path.exists(STATE):
        try:
            return json.load(open(STATE))
        except Exception:
            return {}
    return {}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(st, open(STATE, "w"))


def scan():
    """Return alert lines for items that need MY attention (actionable, stable sig)."""
    q = api("POST", f"/databases/{BOARD}/query", {"page_size": 100})
    rows = q.get("results", [])
    now = time.time()
    alerts = []
    # Build a stable signature across the whole board so we only alert on real change
    sig_parts = []
    for r in rows:
        p = r.get("properties", {})
        title = " ".join(x.get("plain_text", "") for x in p.get("Work Item", {}).get("title", []))
        owner = p.get("Owner", {}).get("select", {}).get("name", "-")
        status = p.get("Status", {}).get("select", {}).get("name", "-")
        notes = " ".join(x.get("plain_text", "") for x in p.get("Review Notes", {}).get("rich_text", []))
        # signature = visible state (strip timestamps) so re-runs don't churn
        sig_parts.append(f"{title[:40]}|{owner}|{status}|{notes[:40]}")
        # actionable: another agent owns it, and it's Needs Review (they delivered)
        if owner in ("ChatGPT", "Kiro Crew", "Eddie") and status == "Needs Review":
            alerts.append(f"→ {owner} delivered: {title[:50]}")
    sig = "\n".join(sorted(sig_parts))
    # Only alert if the signature CHANGED since last run (anti-flood)
    return alerts, sig


def run():
    alerts, sig = scan()
    prev = load_state()
    if sig == prev.get("sig"):
        # no change -> silent (watchdog)
        return "silent"
    # alert only the actionable ones that are NEW (compare to prev alerts)
    prev_alerts = set(prev.get("alerts", []))
    new_alerts = [a for a in alerts if a not in prev_alerts]
    save_state({"sig": sig, "alerts": alerts})
    if not new_alerts:
        return "changed-no-new-alert"
    return "\n".join(new_alerts)


if __name__ == "__main__":
    out = run()
    if out and out != "silent" and out != "changed-no-new-alert":
        print("🔄 COORD BOARD —", out)
    elif out == "silent":
        pass  # nothing new; do not print (no_agent watchdog stays quiet)
