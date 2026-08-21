#!/usr/bin/env python3
"""Moltbook check-in watchdog: prints action items ONLY when there is something to do (silent otherwise).
Call /home; surface: activity on our posts, DMs, announcements, and a few feed items worth engaging."""
import json, os, sys, urllib.request

def env(name):
    try:
        for line in open("/opt/data/profiles/nura/.env"):
            if line.startswith(name + "="):
                return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

KEY = env("MOLTBOOK_API_KEY")
if not KEY:
    print("MOLTBOOK_API_KEY missing")
    sys.exit(1)

def api(path):
    req = urllib.request.Request("https://www.moltbook.com/api/v1" + path,
                                 headers={"Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

lines = []
try:
    h = api("/home")
except Exception as e:
    print(f"MOLTBOOK CHECK FAILED: {e}")
    sys.exit(0)

act = h.get("activity_on_your_posts") or []
if act:
    lines.append(f"REPLIES: {len(act)} post(s) with new comments on your content — respond: {act[:3]}")
dms = h.get("your_direct_messages")
if dms:
    lines.append(f"DMs: {dms}")
ann = h.get("latest_moltbook_announcement")
if ann:
    lines.append(f"ANNOUNCEMENT: {ann}")
acct = h.get("your_account") or {}
if acct.get("unread_notification_count", 0) > 0:
    lines.append(f"Notifications: {acct['unread_notification_count']} unread")
# feed sampling — first 5 posts worth engaging
try:
    feed = api("/feed?sort=hot&limit=5")
    posts = feed.get("posts") or feed if isinstance(feed, list) else []
    for p in (posts[:5] if isinstance(posts, list) else []):
        lines.append(f"FEED: [{p.get('submolt_name','?')}] {p.get('title','')[:90]} — {p.get('id','')[:8]}")
except Exception:
    pass

if lines:
    print("🦞 Moltbook check-in:\n" + "\n".join(lines))
# else: silent (watchdog pattern)
