#!/usr/bin/env python3
"""Detail on the recovered agents + the Canvas bottleneck."""
import collections
import json

D = "/opt/data/paperclip_recovery"
agents = json.load(open(f"{D}/agents.json"))
issues = json.load(open(f"{D}/issues.json"))
by_id = {a["id"]: a for a in agents}

print("=" * 100)
print("ALL 72 AGENTS — name / title / status / adapter / reports_to")
print("=" * 100)
for a in sorted(agents, key=lambda x: (x["company_id"], x["name"])):
    mgr = by_id.get(a.get("reports_to") or "", {}).get("name", a.get("reports_to") or "-")
    print(f"  {a['name'][:30]:<31} {(a.get('title') or a.get('role') or '')[:30]:<31} "
          f"{a.get('status',''):<8} {(a.get('adapter_type') or '')[:15]:<16} -> {mgr[:20]}")

print("\n" + "=" * 100)
print("THE CANVAS BOTTLENECK")
print("=" * 100)
canvas = next((a for a in agents if a["name"] == "Canvas"), None)
if canvas:
    for k, v in canvas.items():
        if v and v not in ("\\N", ""):
            print(f"  {k}: {str(v)[:150]}")
    ci = [i for i in issues if i.get("assignee_agent_id") == canvas["id"]]
    print(f"\n  Canvas issues: {len(ci)}")
    print("  sample:")
    for i in ci[:10]:
        print(f"    [{i.get('identifier') or i.get('issue_number')}] "
              f"{i.get('status','')[:9]:<10} {i.get('priority','')[:8]:<9} {i.get('title','')[:74]}")

print("\n" + "=" * 100)
print("AGENTS IN ERROR STATE (22)")
print("=" * 100)
for a in sorted([x for x in agents if x.get("status") == "error"], key=lambda x: x["name"]):
    print(f"  {a['name'][:32]:<33} {(a.get('title') or a.get('role') or '')[:34]:<35} "
          f"err={str(a.get('error_reason'))[:40]}")

print("\n" + "=" * 100)
print("AGENT BUDGETS + SPEND (top 12 by monthly budget)")
print("=" * 100)
def cents(v):
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0
for a in sorted(agents, key=lambda x: -cents(x.get("budget_monthly_cents")))[:12]:
    print(f"  {a['name'][:30]:<31} budget=${cents(a.get('budget_monthly_cents'))/100:>8.2f}  "
          f"spent=${cents(a.get('spent_monthly_cents'))/100:>8.2f}")
