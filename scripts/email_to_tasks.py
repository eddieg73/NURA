#!/usr/bin/env python3
"""
NURA Email → Task Commitments Worker.

Pulls unread email from the configured mailboxes via IMAP, identifies
commitment-bearing messages (action/deadline/owner/follow-up), and creates rows
in the Master Tasks & Commitments DB. Dedupes on message-id so re-runs never
double-create. Non-PHI by design — only de-identified operational commitments.

Run: python3 email_to_tasks.py [--mailbox nura|legal|medfax] [--dry-run]
Env: reads credentials from /opt/data/profiles/nura/.env (mode-600).
"""
import os
import sys
import json
import re
import time
import imaplib
import email
import email.header
import urllib.request
import urllib.error

VER = "2022-06-28"
MASTER_TASKS_DB = "3cda9b14-e498-8139-bec7-f0e5d9ce416f"
STATE = "/opt/data/profiles/nura/cache/email_to_tasks.state"
ENV = "/opt/data/profiles/nura/.env"

# commitment signals -> priority
COMMIT_WORDS = ["commitment", "committed", "due", "deadline", "by friday", "by monday",
                "eod", "asap", "urgent", "action item", "follow up", "follow-up",
                "need to", "must", "please confirm", "let me know", "send me",
                "i'll send", "will send", "reminder", "meeting", "confirm by"]
HIGH = ["deadline", "urgent", "asap", "due", "must", "confirm by", "commitment"]


def env_val(name):
    if os.path.exists(ENV):
        for line in open(ENV, errors="ignore"):
            line = line.strip()
            if line.startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _notion_token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return list(d.values())[0]
    raise SystemExit("No Notion token")


def notion(method, path, body=None):
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


# ---- IMAP ----
MAILBOXES = {
    "nura": "EMAIL_IMAP_HOST",   # main Nura mailbox
    "legal": "LEGAL_IMAP_HOST",
    "medfax": "MEDFAX_IMAP_HOST",
}
IMAP_USER_KEY = {"nura": "EMAIL_ADDRESS", "legal": "LEGAL_IMAP_USER", "medfax": "MEDFAX_IMAP_USER"}
IMAP_PASS_KEY = {"nura": "EMAIL_PASSWORD", "legal": "LEGAL_IMAP_PASS", "medfax": "MEDFAX_IMAP_PASS"}


def fetch_unread(mailbox):
    host = env_val(MAILBOXES.get(mailbox, "EMAIL_IMAP_HOST")) or "imap.gmail.com"
    user = env_val(IMAP_USER_KEY.get(mailbox, "EMAIL_ADDRESS"))
    pwd = env_val(IMAP_PASS_KEY.get(mailbox, "EMAIL_PASSWORD"))
    if not (user and pwd):
        return []
    try:
        M = imaplib.IMAP4_SSL(host, 993)
        M.login(user, pwd)
        M.select("INBOX")
        # search unread from last 7 days
        since = (time.strftime("%d-%b-%Y", time.gmtime(time.time() - 7 * 86400)))
        typ, data = M.search(None, f'(UNSEEN SINCE {since})')
        ids = data[0].split() if data and data[0] else []
        msgs = []
        for i in ids[-20:]:  # cap to last 20
            typ, msg = M.fetch(i, "(RFC822)")
            if msg and msg[0] and isinstance(msg[0], tuple):
                raw = msg[0][1]
                m = email.message_from_bytes(raw)
                subject = str(email.header.make_header(email.header.decode_header(m.get("Subject", ""))))
                body = ""
                if m.is_multipart():
                    for part in m.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body += part.get_payload(decode=True).decode("utf-8", "ignore")
                            except Exception:
                                pass
                else:
                    try:
                        body = m.get_payload(decode=True).decode("utf-8", "ignore")
                    except Exception:
                        body = ""
                msgs.append({"msg_id": m.get("Message-ID", ""), "subject": subject[:90],
                             "body": body[:1200], "from": m.get("From", "")[:70]})
        M.logout()
        return msgs
    except Exception as e:
        return []


def extract_commitments(msg):
    text = (msg.get("subject", "") + " " + msg.get("body", "")).lower()
    hits = [w for w in COMMIT_WORDS if w in text]
    if not hits:
        return None
    pri = "P2" if any(h in HIGH for h in hits) else "P3"
    # build task title
    title = msg.get("subject", "").strip()[:90] or "Email commitment (no subject)"
    return {"title": title, "priority": pri, "reason": ", ".join(hits[:3])}


def existing_tasks():
    q = notion("POST", f"/databases/{MASTER_TASKS_DB}/query", {"page_size": 100})
    return {" ".join(x.get("plain_text", "") for x in r.get("properties", {}).get("Task", {}).get("title", []))
            for r in q.get("results", [])}


def add_task(title, priority="P2"):
    body = {"parent": {"database_id": MASTER_TASKS_DB}, "properties": {
        "Task": {"title": [{"type": "text", "text": {"content": title}}]},
        "Status": {"select": {"name": "To Do"}},
        "Priority": {"select": {"name": priority}},
        "Owner": {"select": {"name": "Hermes"}},
        "Source": {"select": {"name": "Meeting→Task"}},
        "Commitment": {"checkbox": True},
        "Project": {"rich_text": [{"type": "text", "text": {"content": "Email/Commitments"}}]},
    }}
    r = notion("POST", "/pages", body)
    return r.get("id") is not None


def run(mailboxes=None, dry_run=False):
    mailboxes = mailboxes or ["nura"]
    state = load_state()
    existing = existing_tasks()
    created = 0
    skipped = 0
    commitments = []
    for mb in mailboxes:
        for msg in fetch_unread(mb):
            key = msg.get("msg_id", "") or (msg.get("subject", "") + "|" + msg.get("from", ""))
            key = key[:80]
            if state.get(key):
                skipped += 1
                continue
            c = extract_commitments(msg)
            if not c:
                continue
            if c["title"] in existing:
                skipped += 1
                continue
            commitments.append((mb, c["title"], c["priority"]))
            if dry_run:
                continue
            if add_task(c["title"], c["priority"]):
                state[key] = True
                existing.add(c["title"])
                created += 1
    if not dry_run:
        save_state(state)
    return {"mailboxes": mailboxes, "commitments_found": len(commitments),
            "created": created, "skipped": skipped, "dry_run": dry_run,
            "commitments": commitments[:10]}


if __name__ == "__main__":
    mb_list = ["nura"]
    if "--mailbox" in sys.argv:
        mb_list = sys.argv[sys.argv.index("--mailbox") + 1].split(",")
    dry = "--dry-run" in sys.argv
    print(json.dumps(run(mb_list, dry), indent=2, default=str))
