#!/usr/bin/env python3
"""The open workstreams, grouped — input for the Hermes-native rebuild."""
import collections
import json

D = "/opt/data/paperclip_recovery"
issues = json.load(open(f"{D}/issues.json"))
agents = json.load(open(f"{D}/agents.json"))
by_id = {a["id"]: a for a in agents}

print("=" * 100)
print("ALL OPEN ISSUES — critical first, then high")
print("=" * 100)
rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
opens = [i for i in issues if (i.get("status") or "").lower() not in
         {"done", "completed", "cancelled", "closed", "archived"}]
for i in sorted(opens, key=lambda x: rank.get((x.get("priority") or "").lower(), 9)):
    if (i.get("priority") or "").lower() != "critical":
        continue
    a = by_id.get(i.get("assignee_agent_id", ""), {}).get("name", "?")
    print(f"  [{i.get('identifier') or '?':<8}] {i.get('priority','')[:8]:<9} {a[:22]:<23} "
          f"{i.get('title','')[:72]}")

print("\n" + "=" * 100)
print("OPEN WORK GROUPED BY ASSIGNEE (top 15) — who actually has work")
print("=" * 100)
cnt = collections.Counter(i.get("assignee_agent_id", "") for i in opens)
for aid, n in cnt.most_common(15):
    a = by_id.get(aid, {})
    print(f"  {n:>4}  {a.get('name','(unassigned)'):<34} {(a.get('title') or '')[:44]}")

print("\n" + "=" * 100)
print("OUTPUT: full issue list -> /opt/data/paperclip_recovery/issues.json")
print("=" * 100)
print(f"  total issues: {len(issues)}   open: {len(opens)}")
# distribution of first words in titles = natural workstreams
first = collections.Counter((i.get("title") or "").split(":")[0].strip()[:38] for i in opens)
print("\n  natural workstream prefixes (title before ':'):")
for k, v in first.most_common(16):
    if k:
        print(f"    {v:>4}  {k}")
