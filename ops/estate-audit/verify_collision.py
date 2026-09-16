#!/usr/bin/env python3
"""
Confirm the TERMINAL_CWD collision hypothesis for `evolution review`, and check whether the
current schedule still collides.

FAILURE (2026-09-01 08:11):  TimeoutError waiting for the TERMINAL_CWD read lock after 660s.

HYPOTHESIS
Only 4 jobs declare a workdir, ALL of them `/opt/data/Obsidian Vault`. `obsidian-morning` runs
`0 8 * * *` — 08:00 daily. `evolution review` ran `0 8 1 * *` — 08:00 on the 1st. Same minute, one
holds the vault lock, the other waits 660s and dies. It only fails on the 1st of the month, which is
exactly why it broke once and then looked quiet for 30 days.

TEST: does the workdir holder's minute overlap the broken job's minute? And does the CURRENT
schedule still overlap?
"""
import json

PROFILE = "/opt/data/profiles/nura"
j = json.load(open(f"{PROFILE}/cron/jobs.json"))
jobs = j if isinstance(j, list) else j.get("jobs", [])

holders = [(x.get("name"), (x.get("schedule") or {}).get("expr", ""), x.get("workdir"))
           for x in jobs if x.get("workdir")]
er = next(x for x in jobs if x.get("name") == "evolution review")
expr = (er.get("schedule") or {}).get("expr", "")
print(f"  evolution review CURRENT schedule: {expr}   (was 0 8 1 * * at failure time)")
print()
print(f"  {'workdir holder':<26}{'expr':<16}{'runs at :08?':<14}")
print("  " + "-" * 62)
collide_old = collide_new = False
for name, e, wd in holders:
    f = e.split()
    if len(f) != 5:
        continue
    min_, hour = f[0], f[1]
    runs_08 = (min_ == "0" and hour == "8")
    if runs_08:
        collide_old = True
    print(f"  {name:<26}{e:<16}{('YES' if runs_08 else 'no'):<14}")
print()
print("  ── VERDICT ──")
print(f"  OLD schedule 0 8 1 * * overlapped a vault-workdir holder at 08:00 : "
      f"{'CONFIRMED — this is the lock collision' if collide_old else 'no'}")
f = expr.split()
if len(f) == 5:
    print(f"  CURRENT schedule {expr} fires at {f[1]}:{f[0].zfill(2)}; "
          f"vault holders run at 08:00 / 18:00 / 21:00 / 22:00")
    new_hour = f[1]
    collide_new = new_hour in ("8", "18", "21", "22")
    print(f"  CURRENT schedule still collides: {'YES — still broken' if collide_new else 'NO — collision avoided'}")

print()
print("  ── CONSEQUENCE FOR last_status ──")
print("  A MONTHLY job that errored on 09-01 keeps last_status=error until 2026-10-01, even if the")
print("  cause is already fixed. So an error flag on an infrequent job is a claim about the LAST RUN,")
print("  not about the CURRENT configuration. The estate watchdog prints the error date for exactly")
print("  this reason — a stale monthly error and a live daily error must be distinguishable, or the")
print("  report trains the reader to ignore it.")
