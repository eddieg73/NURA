#!/usr/bin/env python3
"""Agent cost tracker v3 — per-developer/per-session cost from state.db session_model_usage.
Usage: agent-cost-tracker.py [--days 7] [--top 10]
"""
import sqlite3, sys
from collections import defaultdict
from datetime import datetime, timedelta

DB = "/opt/data/profiles/nura/state.db"

def main():
    days = 7
    top = 10
    args = sys.argv[1:]
    if "--days" in args:
        days = int(args[args.index("--days") + 1])
    if "--top" in args:
        top = int(args[args.index("--top") + 1])
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cutoff = datetime.now() - timedelta(days=days)
    cur.execute("""SELECT session_id, model, billing_provider, api_call_count, input_tokens,
                   output_tokens, estimated_cost_usd, first_seen FROM session_model_usage
                   WHERE first_seen >= ?""", (cutoff.timestamp(),))
    rows = cur.fetchall()
    by_owner = defaultdict(lambda: {"calls": 0, "cost": 0.0, "sessions": set()})
    by_day = defaultdict(float)
    for sid, model, prov, calls, inp, out, cost, seen in rows:
        owner = "cron" if sid.startswith("cron_") else ("agent" if "agent" in sid.lower() or "_" in sid and not sid.startswith(("user", "telegram", "sms")) else "user")
        owner_key = sid.split("_")[0][:24] if not sid.startswith("cron_") else "cron:" + sid.split("_")[1][:8]
        by_owner[owner_key]["calls"] += calls or 0
        by_owner[owner_key]["cost"] += cost or 0.0
        by_owner[owner_key]["sessions"].add(sid)
        if seen:
            day = datetime.fromtimestamp(seen).strftime("%m-%d")
            by_day[day] += cost or 0.0
    total = sum(v["cost"] for v in by_owner.values())
    print(f"=== AGENT COST (LAST {days} DAYS) — ESTIMATED, {len(rows)} sessions ===")
    print(f"TOTAL EST: ${total:.3f}")
    print("\n-- by owner (top %d) --" % top)
    for k, v in sorted(by_owner.items(), key=lambda x: -x[1]["cost"])[:top]:
        print(f"  {k:30} ${v['cost']:.4f}  ({v['calls']} calls, {len(v['sessions'])} sessions)")
    print("\n-- by day --")
    for d in sorted(by_day):
        print(f"  {d}: ${by_day[d]:.4f}")
    print("\nNOTE: estimated from provider rates; billing_provider in DB for exact reconciliation (Midas).")

if __name__ == "__main__":
    main()
