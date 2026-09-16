#!/usr/bin/env python3
"""
NURA Workforce CLI — check-in / check-out and board status.

This is how EVERY agent (cron worker or subagent) records presence and outcome.
Notion is the system of record; this script is the only writer.

    workforce.py checkin  <agent> <task> [--note "..."]
    workforce.py checkout <agent> <task> --outcome "..." [--evidence "..."]
    workforce.py blocked  <agent> <task> --reason "..."
    workforce.py status                      who is checked in right now
    workforce.py board                       board summary by status/assignee

Exit codes: 0 ok, 1 usage/error.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import sys
import requests

sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers  # noqa: E402

H = headers()
BASE = "https://api.notion.com/v1"
IDS = json.load(open("/opt/data/workforce_ids.json"))
CHECKIN_DB = IDS["checkin_db"]
TASKS_DB = IDS["tasks_db"]
REGISTRY_DB = IDS["registry_db"]


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def log(agent, event, task, outcome="", evidence=""):
    r = requests.post(f"{BASE}/pages", headers=H, timeout=45, json={
        "parent": {"type": "database_id", "database_id": CHECKIN_DB},
        "properties": {
            "Entry": {"title": [{"type": "text", "text": {
                "content": f"{event} — {agent} — {task}"[:180]}}]},
            "Agent": {"rich_text": [{"type": "text", "text": {"content": agent}}]},
            "Event": {"select": {"name": event}},
            "When": {"date": {"start": now_iso()}},
            "Task": {"rich_text": [{"type": "text", "text": {"content": task[:1800]}}]},
            "Outcome": {"rich_text": [{"type": "text", "text": {"content": outcome[:1800]}}]},
            "Evidence": {"rich_text": [{"type": "text", "text": {"content": evidence[:1800]}}]},
        },
    })
    if r.status_code >= 300:
        print(f"  !! log failed {r.status_code}: {r.text[:200]}", file=sys.stderr)
        return False
    return True


def query_all(db):
    out, cur = [], None
    while True:
        b = {"page_size": 100}
        if cur:
            b["start_cursor"] = cur
        r = requests.post(f"{BASE}/databases/{db}/query", headers=H, json=b, timeout=45)
        if r.status_code >= 300:
            break
        d = r.json()
        out += d.get("results", [])
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    return out


def plain(page, field):
    p = (page.get("properties") or {}).get(field) or {}
    t = p.get("type")
    if t == "rich_text":
        return "".join(x.get("plain_text", "") for x in p.get("rich_text", []))
    if t == "title":
        return "".join(x.get("plain_text", "") for x in p.get("title", []))
    if t == "select":
        return (p.get("select") or {}).get("name", "")
    if t == "date":
        return (p.get("date") or {}).get("start", "")
    return ""


def cmd_status(args):
    entries = sorted(query_all(CHECKIN_DB),
                     key=lambda p: plain(p, "When"), reverse=True)
    seen = {}
    for e in entries:
        a = plain(e, "Agent")
        if not a or a in seen:
            continue
        seen[a] = (plain(e, "Event"), plain(e, "When"), plain(e, "Task")[:60])
    if not seen:
        print("  no check-ins recorded")
        return 0
    print(f"  {'AGENT':<26} {'LAST EVENT':<11} {'WHEN':<21} TASK")
    for a, (ev, wh, tk) in sorted(seen.items()):
        print(f"  {a[:25]:<26} {ev:<11} {wh[:19]:<21} {tk}")
    innow = [a for a, (ev, _, _) in seen.items() if ev == "Check-in"]
    print(f"\n  currently checked in: {len(innow)}  {innow if innow else ''}")
    return 0


def cmd_board(args):
    rows = query_all(TASKS_DB)
    by_status = collections.Counter(plain(p, "Status") for p in rows)
    by_assignee = collections.Counter(plain(p, "Assignee") for p in rows)
    by_pri = collections.Counter(plain(p, "Priority") for p in rows)
    print(f"  Agent Tasks: {len(rows)} total")
    print("\n  by status:")
    for k, v in by_status.most_common():
        print(f"    {v:>5}  {k or '(none)'}")
    print("\n  by priority:")
    for k, v in by_pri.most_common():
        print(f"    {v:>5}  {k or '(none)'}")
    print("\n  top assignees:")
    for k, v in by_assignee.most_common(10):
        print(f"    {v:>5}  {k or '(unassigned)'}")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="workforce")
    sub = ap.add_subparsers(dest="cmd")

    for name in ("checkin", "checkout", "blocked"):
        p = sub.add_parser(name)
        p.add_argument("agent")
        p.add_argument("task")
        p.add_argument("--note", default="")
        p.add_argument("--outcome", default="")
        p.add_argument("--reason", default="")
        p.add_argument("--evidence", default="")

    sub.add_parser("status")
    sub.add_parser("board")
    a = ap.parse_args()

    if a.cmd == "checkin":
        ok = log(a.agent, "Check-in", a.task, outcome=a.note)
        print(f"  check-in logged: {a.agent}" if ok else "  FAILED")
        return 0 if ok else 1
    if a.cmd == "checkout":
        if not a.outcome:
            print("  --outcome is required for check-out (no silent carries)", file=sys.stderr)
            return 1
        ok = log(a.agent, "Check-out", a.task, outcome=a.outcome, evidence=a.evidence)
        print(f"  check-out logged: {a.agent}" if ok else "  FAILED")
        return 0 if ok else 1
    if a.cmd == "blocked":
        if not a.reason:
            print("  --reason required for blocked", file=sys.stderr)
            return 1
        ok = log(a.agent, "Blocked", a.task, outcome=a.reason)
        print(f"  blocked logged: {a.agent}" if ok else "  FAILED")
        return 0 if ok else 1
    if a.cmd == "status":
        return cmd_status(a)
    if a.cmd == "board":
        return cmd_board(a)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
