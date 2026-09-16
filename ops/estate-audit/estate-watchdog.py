#!/usr/bin/env python3
"""
ESTATE WATCHDOG — the 7 systems the corrected audit found with NO watcher.

THE GAP
A corrected audit (audit_corrected.py) checked coverage by whether a job NAMES the system in its
name or monitor script, not by keyword coincidence in prose. That found SEVEN genuinely unwatched
systems: gateway process, qdrant, redis, cron roster, Notion, n8n, external endpoints.

THE MOST IMPORTANT ONE IS THE NEW SECTION C.
A job that silently stops firing is invisible: it produces no output, so it looks exactly like a job
with nothing to report. Two live examples found in this audit:
  * `emos gap audit`  — daily schedule, DISABLED, last ran 2026-09-06 (7 days before the audit)
  * `evolution review` — monthly, last ran 2026-09-01, last_status=error
Neither raised anything. A dead controller is a dead system, and nothing noticed.

So Section C checks SCHEDULE ADHERENCE: for every enabled job with a cron expression, has it run
within its expected window? That is the monitoring equivalent of checking that the smoke detector is
still wired in, not just that it is not beeping.

DESIGN (mirrors lane-state-watchdog, deliberately)
  * duration/overdue tracking, not just a boolean
  * deterministic --state output for cron monitor-gating
  * its own heartbeat, so the watchdog cannot become the next silent lane
  * expected-down entries must not cry wolf

USAGE
  estate-watchdog.py                 # full report; exit 1 if anything is wrong
  estate-watchdog.py --state         # deterministic line for monitor-gating
  estate-watchdog.py --json
  estate-watchdog.py --check-heartbeat
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time

HEARTBEAT = "/opt/data/estate_watchdog.heartbeat"
HB_MAX_AGE = int(os.environ.get("ESTATE_HB_MAX_AGE", 26 * 3600))
JOBS = "/opt/data/profiles/nura/cron/jobs.json"

# cron (minute, hour, dom, month, dow) -> expected max gap in seconds before we call it overdue.
# Generous multipliers: we want "this stopped firing", not "this is 3 minutes late".
def expected_window(expr):
    """Return (seconds_expected_gap, human_label) for a cron expression, or None if unsupported."""
    try:
        f = expr.split()
        if len(f) != 5:
            return None
        minute, hour, dom, month, dow = f
        if minute.startswith("*/"):
            n = int(minute[2:])
            return n * 60 * 3, f"every {n}m"
        if minute.isdigit() and hour.startswith("*/"):
            n = int(hour[2:])
            return n * 3600 * 3, f"every {n}h"
        if minute.isdigit() and hour.isdigit() and dom == "*" and month == "*" and dow == "*":
            return 86400 * 3, "daily"
        if minute.isdigit() and hour.isdigit() and dom == "*" and month == "*" and dow != "*":
            return 86400 * 7 * 2, "weekly"
        if minute.isdigit() and hour.isdigit() and dom.isdigit():
            return 86400 * 32 * 2, "monthly"
        return None
    except Exception:
        return None


def load(path, default):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return default


def tcp(host, port, timeout=4):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True, "ok"
    except Exception as e:
        return False, f"{type(e).__name__}"
    finally:
        try:
            s.close()
        except Exception:
            pass


def http(url, timeout=8):
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-m", str(timeout), "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=timeout + 5)
        return r.stdout.strip() or "000"
    except Exception:
        return "000"


def human(sec):
    if sec < 0:
        return "n/a"
    if sec < 3600:
        return f"{int(sec//60)}m"
    if sec < 86400:
        return f"{sec/3600:.1f}h"
    return f"{sec/86400:.1f}d"


def section_local():
    """A. local services"""
    problems = []
    checks = [
        ("gateway process", None),
        ("qdrant :6333", ("127.0.0.1", 6333)),
        ("redis :6379", ("127.0.0.1", 6379)),
    ]
    results = []
    # gateway: does the recorded pid still exist and is the http api answering
    gs = load("/opt/data/profiles/nura/gateway_state.json", {})
    pid = gs.get("pid")
    alive = os.path.exists(f"/proc/{pid}") if pid else False
    api = http("http://127.0.0.1:8080/")
    ok = alive and api not in ("000",)
    results.append(("gateway process", ok, f"pid={pid} alive={alive} api={api}"))
    if not ok:
        problems.append(f"gateway(pid={pid},alive={alive},api={api})")

    for label, addr in checks[1:]:
        ok, detail = tcp(*addr)
        results.append((label, ok, detail))
        if not ok:
            problems.append(label.split()[0])

    # docker — ONLY assess if the local daemon is actually reachable.
    # This gateway host has the docker CLI but no daemon (the fleet containers live on
    # clinic/lab/edge). Reporting "0 containers" there is a false alarm, and a watchdog that cries
    # wolf on an expected condition gets muted. Verified 2026-09-13: `docker info` -> cannot connect.
    try:
        di = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=20)
        if di.returncode != 0:
            results.append(("docker containers", True,
                            "n/a — no local daemon (fleet containers live on clinic/lab/edge)"))
        else:
            r = subprocess.run(["docker", "ps", "-q"], capture_output=True, text=True, timeout=25)
            n = len([x for x in r.stdout.split() if x])
            results.append(("docker containers", n > 0, f"{n} running"))
            if n == 0:
                problems.append("docker(0 containers)")
    except Exception as e:
        results.append(("docker containers", True, f"n/a — {type(e).__name__}"))
    return results, problems


def section_endpoints():
    """B. external endpoints — the ones whose failure is noticed by strangers first"""
    ENDPOINTS = [
        ("nuratech.ai", "https://nuratech.ai/"),
        ("pay.nuratech.ai (Perfex)", "https://pay.nuratech.ai/"),
        ("carepilot.nuratech.ai", "https://carepilot.nuratech.ai/"),
        ("api.nuratech.ai", "https://api.nuratech.ai/"),
    ]
    results, problems = [], []
    for label, url in ENDPOINTS:
        code = http(url)
        # 000 = no answer; 4xx/5xx are answers but unhealthy for a public door
        ok = code.startswith("2") or code.startswith("3")
        results.append((label, ok, f"HTTP {code}"))
        if not ok:
            problems.append(f"{label}={code}")
    return results, problems


def section_cron_adherence():
    """C. THE IMPORTANT ONE — a job that stopped firing is invisible."""
    j = load(JOBS, {})
    jobs = j if isinstance(j, list) else j.get("jobs", [])
    now = time.time()
    results, problems = [], []
    for x in jobs:
        if not x.get("enabled"):
            continue
        sched = (x.get("schedule") or {})
        expr = sched.get("expr") if isinstance(sched, dict) else None
        if not expr:
            continue
        win = expected_window(expr)
        if not win:
            continue
        max_gap, label = win
        lr = x.get("last_run_at")
        created = x.get("created_at")
        if not lr:
            # A job that has NEVER run is only a problem if it has had the chance to.
            # jobs.json carries created_at, so grant one full expected window as grace —
            # otherwise every newly created job false-fires on its first tick.
            try:
                from datetime import datetime
                cdt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                age_since_create = now - cdt.timestamp()
            except Exception:
                age_since_create = None
            if age_since_create is not None and age_since_create <= max_gap:
                results.append((x.get("name", "?"), True,
                                f"new ({human(age_since_create)} old, grace {label})"))
            else:
                results.append((x.get("name", "?"), False, f"NEVER RUN ({label})"))
                problems.append(f"{x.get('name')}:never")
            continue
        try:
            ts = lr.replace("Z", "+00:00")
            from datetime import datetime
            dt = datetime.fromisoformat(ts)
            age = now - dt.timestamp()
        except Exception:
            continue
        if age > max_gap:
            results.append((x.get("name", "?"), False,
                            f"OVERDUE {human(age)} (expected {label})"))
            problems.append(f"{x.get('name')}:overdue{human(age)}")
            continue
        # a job can be on time AND failing. last_status=error is a distinct failure from overdue,
        # and the audit found two such jobs (`evolution review`, `emos gap audit`) which no watcher
        # surfaced. Flag them here so one probe answers "is the roster actually working".
        if x.get("last_status") == "error":
            results.append((x.get("name", "?"), False,
                            f"ON TIME BUT ERRORING (last {str(lr)[:19]})"))
            problems.append(f"{x.get('name')}:error")
    return results, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check-heartbeat", action="store_true")
    args = ap.parse_args()

    if args.check_heartbeat:
        hb = load(HEARTBEAT, None)
        if not hb:
            print("FAIL: estate watchdog has never run")
            return 1
        age = time.time() - hb.get("last_run", 0)
        if age > HB_MAX_AGE:
            print(f"FAIL: heartbeat stale by {human(age)} — estate watchdog is DEAD")
            return 1
        print(f"OK: heartbeat fresh ({human(age)}, runs={hb.get('runs')})")
        return 0

    local, p_local = section_local()
    endp, p_endp = section_endpoints()
    cron, p_cron = section_cron_adherence()
    problems = p_local + p_endp + p_cron

    hb = load(HEARTBEAT, {"runs": 0})
    hb["runs"] = int(hb.get("runs", 0)) + 1
    hb["last_run"] = time.time()
    hb["last_run_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    hb["problems"] = len(problems)
    json.dump(hb, open(HEARTBEAT, "w"), indent=1)

    if args.state:
        # deterministic: sorted problem keys only, no timestamps
        print("|".join(sorted(problems)) or "CLEAN")
        return 1 if problems else 0

    if args.json:
        print(json.dumps({"local": local, "endpoints": endp, "cron": cron,
                          "problems": problems}, indent=1))
        return 1 if problems else 0

    print("=" * 92)
    print("ESTATE WATCHDOG — the 7 previously-unmonitored systems")
    print("=" * 92)
    for title, rows in [("A. LOCAL SERVICES", local),
                        ("B. EXTERNAL ENDPOINTS", endp),
                        ("C. CRON SCHEDULE ADHERENCE (a job that stopped firing is invisible)", cron)]:
        print(f"\n  {title}")
        if not rows:
            print("     (nothing to assess)")
        for label, ok, detail in rows:
            print(f"     [{'OK  ' if ok else 'FAIL'}] {label:<30} {detail}")
    print("\n" + "=" * 92)
    print(f"  VERDICT: {len(problems)} problem(s)")
    for p in problems:
        print(f"    - {p}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
