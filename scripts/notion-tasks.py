#!/usr/bin/env python3
"""Create the Founder Manual Tasks page in Notion (channel unlocks, 2026-08-15)."""
import os, re, json, urllib.request

ENV = "/opt/data/profiles/nura/.env"
KEY = None
with open(ENV) as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
if not KEY:
    print("NO TOKEN"); raise SystemExit(1)

HDR = {"Authorization": f"Bearer {KEY}", "Notion-Version": "2022-06-28",
       "Content-Type": "application/json"}

def api(path, method="GET", body=None):
    req = urllib.request.Request(f"https://api.notion.com/v1{path}", method=method, headers=HDR)
    data = json.dumps(body).encode() if body else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:300]}

# 1. sanity + find parent page
me = api("/users/me")
print("ME:", me.get("name") or me.get("error"))

search = api("/search", "POST", {"query": "NURA-Work-Update", "filter": {"value": "page", "property": "object"}})
results = search.get("results", [])
parent_id = None
for r in results:
    if r.get("object") == "page":
        parent_id = r["id"]
        print("PARENT:", json.dumps(r.get("properties", {}))[:200])
        break
if not parent_id:
    # fallback: any shared page
    anypage = api("/search", "POST", {"filter": {"value": "page", "property": "object"}})
    for r in anypage.get("results", [])[:1]:
        parent_id = r["id"]
        print("FALLBACK PARENT:", json.dumps(r.get("properties", {}))[:200])
if not parent_id:
    print("NO PARENT PAGE FOUND — share-gate likely"); raise SystemExit(1)

TASKS = [
    ("🐦 X/Twitter — register developer app + OAuth (5 min)", [
        "Go to https://developer.x.com/en/portal/dashboard → create an app (type: Web app, automated app or bot)",
        "Set redirect URI to http://localhost:8080/callback",
        "In Termius/Blink SSH, run: xurl auth apps add my-app --client-id ... --client-secret ...",
        "Then: xurl auth oauth2 --app my-app YOUR_USERNAME  (opens a URL — open it on iPad, authorize, paste the redirect back)",
        "Then: xurl auth default my-app",
    ]),
    ("🎥 YouTube — drop cookies.txt (2 min)", [
        "Chrome/Firefox: install 'Get cookies.txt LOCALLY' extension, log into YouTube, export cookies.txt",
        "Upload to the VPS: /opt/data/cookies/cookies.txt (see /opt/data/cookies/README.md)",
        "The sentinel auto-arms yt-dlp + the transcript lane and messages you.",
    ]),
    ("👽 Reddit — drop reddit-cookies.txt (2 min)", [
        "Same cookie extension, export while logged into reddit.com → reddit-cookies.txt",
        "Upload to /opt/data/cookies/reddit-cookies.txt",
    ]),
    ("💼 LinkedIn — drop linkedin-cookies.txt (2 min)", [
        "Export while logged into linkedin.com → linkedin-cookies.txt",
        "Upload to /opt/data/cookies/linkedin-cookies.txt",
    ]),
    ("📓 NotebookLM — Google re-auth + one share-link (3 min)", [
        "Message Hermes 'setup notebooklm' → complete the Google login flow",
        "Open any notebook at notebooklm.google.com → Share → Anyone with the link → copy URL",
        "Send the share-link to Hermes (this registers it for YouTube-source ingestion).",
    ]),
    ("✅ Moltbook verification — X handle claim (2 min)", [
        "Moltbook verification is stalled: the claim-tweet must come from an X account with followers.",
        "Log into @nuratechai (or your main X), post the Moltbook claim-link it gives you (dashboard → verification).",
    ]),
    ("🗓️ Google Calendar OAuth (2 min)", [
        "The pending calendar OAuth step — complete via 'setup google calendar' message to Hermes.",
    ]),
]

blocks = [
    {"object": "block", "type": "heading_1",
     "heading_1": {"rich_text": [{"type": "text", "text": {"content": "Founder Manual Tasks — Channel Unlocks"}}]}},
    {"object": "block", "type": "paragraph",
     "paragraph": {"rich_text": [{"type": "text", "text": {"content": "One-time manual items for Eddie (2026-08-15). Each is ~2–5 min. Hermes auto-detects completion via the cookie sentinel / auth probes."}}]}},
]
for title, steps in TASKS:
    blocks.append({"object": "block", "type": "to_do",
                   "to_do": {"rich_text": [{"type": "text", "text": {"content": title}}]}})
    for s in steps:
        blocks.append({"object": "block", "type": "bulleted_list_item",
                       "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": s}}]}})

body = {
    "parent": {"page_id": parent_id},
    "properties": {"title": {"title": [{"text": {"content": "Founder Manual Tasks — Channel Unlocks"}}]}},
    "children": blocks,
}
created = api("/pages", "POST", body)
if created.get("error"):
    print("CREATE FAILED:", created); raise SystemExit(1)
print("CREATED PAGE ID:", created["id"])
print("URL:", created.get("url", f"https://notion.so/{created['id'].replace('-', '')}"))
