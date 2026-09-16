#!/usr/bin/env python3
"""
LANE STATE WATCHDOG — the missing consumer for gateway_state.json.

THE FAILURE THIS PREVENTS
  The gateway writes `needs_attention: true` and a `state` for every platform lane into
  gateway_state.json. Nothing read that file. No script referenced it; no script referenced
  `needs_attention`. The a2a lane sat in state=retrying / error_code=bind_failed from
  2026-09-07 05:18 until 2026-09-13 — SIX DAYS — and was only discovered by accident while
  looking for something else.

  A self-reported status flag with no consumer is not monitoring. It is a diary.

WHY DURATION IS THE WHOLE POINT
  A lane retrying for 40 seconds is normal boot behaviour. A lane retrying for six days is an
  outage. Counting lanes is useless; TRACKING HOW LONG each has been degraded is what turns noise
  into signal. This script keeps first-seen timestamps so it can say "degraded 6d 14h", not just
  "degraded".

WHY IT DOES NOT TRUST THE FLAG ALONE
  `needs_attention` is a CLAIM. After the a2a fix it still read True while the lane was demonstrably
  connected and accepting sockets. So this script classifies on `state` (the state field, backed by
  an independent socket probe for the lanes where one is possible) and treats needs_attention as
  corroboration only. Verify the thing, not the flag about the thing.

SILENT LANE PROBLEM — THE WATCHDOG MUST PROVE ITS OWN LIVENESS
  A watchdog that dies silently looks exactly like a healthy system. So every run writes a heartbeat
  with a monotonically increasing run counter, and `--check-heartbeat` fails if the heartbeat is
  stale. Without that, this script becomes the next invisible lane.

USAGE
  lane-state-watchdog.py            # report (exit 1 if anything is over threshold)
  lane-state-watchdog.py --state    # deterministic one-line state for cron monitor-gating
  lane-state-watchdog.py --check-heartbeat
  lane-state-watchdog.py --json
"""
import argparse
import json
import os
import socket
import sys
import time

STATE_FILE = "/opt/data/profiles/nura/gateway_state.json"
SEEN_FILE = "/opt/data/lane_degradation_state.json"
HEARTBEAT = "/opt/data/lane_state_watchdog.heartbeat"

# A lane must be degraded at least this long before it is worth reporting.
# Boot blips and reconnect churn sit well under this; real outages blow through it.
THRESHOLD_SECONDS = int(os.environ.get("LANE_WATCH_THRESHOLD", 3600))     # 1 hour
HEARTBEAT_MAX_AGE = int(os.environ.get("LANE_WATCH_HB_MAX_AGE", 26 * 3600))  # 26h = daily cron + slack

# Lanes where a socket probe can independently confirm or refute the reported state.
# A lane absent from this map is judged on its reported state alone (and said so).
PROBES = {
    "a2a": ("127.0.0.1", 8643),
}

# Lanes that are EXPECTED to be unhealthy because they are unconfigured.
# These are config gaps, not incidents, and must not cry wolf.
EXPECTED_DOWN = {
    "whatsapp": "not paired (by design)",
    "whatsapp_cloud": "unconfigured (by design)",
    "slack": "no bot token (by design)",
    "discord": "no credentials (by design)",
}


def load(path, default):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return default


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=1)
    os.replace(tmp, path)


def probe(host, port, timeout=4):
    """True if the port accepts a connection right now."""
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True, "socket accepted"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
    finally:
        try:
            s.close()
        except Exception:
            pass


def human(sec):
    if sec < 60:
        return f"{int(sec)}s"
    if sec < 3600:
        return f"{int(sec//60)}m"
    if sec < 86400:
        return f"{sec/3600:.1f}h"
    return f"{sec/86400:.1f}d"


def gateway_start_time(gs):
    """Absolute epoch when the gateway process started, used to seed degradation clocks.

    Read from /proc/<pid>/stat field 22 (starttime in clock ticks since boot) + /proc/uptime.
    Falls back to None; callers must handle that.
    """
    try:
        pid = gs.get("pid")
        if not pid:
            return None
        with open(f"/proc/{pid}/stat") as fh:
            fields = fh.read().rsplit(")", 1)[1].split()
        starttime_ticks = int(fields[19])            # field 22 overall, 20th after the comm split
        hz = os.sysconf("SC_CLK_TCK")
        with open("/proc/uptime") as fh:
            uptime = float(fh.read().split()[0])
        boot = time.time() - uptime
        return boot + (starttime_ticks / hz)
    except Exception:
        return None


def collect():
    gs = load(STATE_FILE, {})
    platforms = gs.get("platforms") or {}
    if not platforms:
        return None, "gateway_state.json has no 'platforms' map — cannot assess lanes"

    now = time.time()
    gw_start = gateway_start_time(gs)
    seen = load(SEEN_FILE, {})
    verdicts = []

    for name, info in sorted(platforms.items()):
        if not isinstance(info, dict):
            continue
        state = info.get("state")
        err = info.get("error_code")
        flag = info.get("needs_attention")

        healthy = (state == "connected")

        # independent corroboration where possible
        probe_note = ""
        if name in PROBES:
            ok, detail = probe(*PROBES[name])
            probe_note = f"probe={'UP' if ok else 'DOWN'} ({detail})"
            if ok and not healthy:
                # the flag says broken, reality says fine -> trust reality, and say so
                healthy = True
                probe_note += " -> state field is STALE"
            elif not ok and healthy:
                healthy = False
                probe_note += " -> state field is WRONG"

        expected = name in EXPECTED_DOWN

        if healthy or expected:
            seen.pop(name, None)
            verdicts.append({
                "lane": name, "state": state, "healthy": True,
                "expected_down": expected, "reason": EXPECTED_DOWN.get(name, ""),
                "degraded_for": 0, "probe": probe_note, "flag": flag, "error": err,
            })
            continue

        # degraded — track since when
        entry = seen.get(name) or {}
        first = entry.get("first_seen")
        last_state = entry.get("state")
        if last_state != state:
            first = None          # state changed -> restart the clock
        if not first:
            # SEEDING: a lane degraded on FIRST observation has no history, so starting the clock
            # at "now" would grant a fresh grace period to something that may have been broken for
            # days -- exactly how a2a hid for six. The gateway's own start time is a sound floor:
            # the lane cannot have been judged healthy before the process that judges it existed.
            # If the gateway has been up longer than the threshold, we flag immediately.
            first = entry.get("gateway_start") or gw_start or now
        seen[name] = {"first_seen": first, "state": state,
                      "error": err, "last_healthy": entry.get("last_healthy"),
                      "gateway_start": gw_start}
        verdicts.append({
            "lane": name, "state": state, "healthy": False,
            "expected_down": False, "reason": "",
            "degraded_for": now - first, "probe": probe_note,
            "flag": flag, "error": err,
        })

    save(SEEN_FILE, seen)

    # heartbeat — proof this watchdog itself ran
    hb = load(HEARTBEAT, {"runs": 0})
    hb["runs"] = int(hb.get("runs", 0)) + 1
    hb["last_run"] = time.time()
    hb["last_run_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save(HEARTBEAT, hb)

    return verdicts, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="store_true", help="deterministic one-line state (cron monitor)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check-heartbeat", action="store_true")
    ap.add_argument("--threshold", type=int, default=THRESHOLD_SECONDS)
    args = ap.parse_args()

    if args.check_heartbeat:
        hb = load(HEARTBEAT, None)
        if not hb:
            print("FAIL: no heartbeat — the lane watchdog has never run")
            return 1
        age = time.time() - hb.get("last_run", 0)
        if age > HEARTBEAT_MAX_AGE:
            print(f"FAIL: heartbeat stale by {human(age)} — the lane watchdog is dead "
                  f"(last run {hb.get('last_run_iso')}, runs={hb.get('runs')})")
            return 1
        print(f"OK: heartbeat fresh ({human(age)} old, runs={hb.get('runs')})")
        return 0

    verdicts, err = collect()
    if err:
        print(f"ERROR: {err}")
        return 2

    over = [v for v in verdicts if not v["healthy"] and v["degraded_for"] >= args.threshold]
    down = [v for v in verdicts if not v["healthy"]]

    if args.state:
        # deterministic: only over-threshold lanes affect the string, so it is stable run to run
        key = "|".join(sorted(f"{v['lane']}:{v['state']}" for v in over)) or "CLEAN"
        print(key)
        return 1 if over else 0

    if args.json:
        print(json.dumps({"degraded": down, "over_threshold": over,
                          "threshold_s": args.threshold}, indent=1))
        return 1 if over else 0

    print("=" * 88)
    print("LANE STATE WATCHDOG — gateway_state.json")
    print(f"threshold: {human(args.threshold)}   lanes: {len(verdicts)}")
    print("=" * 88)
    if not down:
        print("  ALL LANES HEALTHY.")
    for v in down:
        tag = "OVER THRESHOLD" if v["degraded_for"] >= args.threshold else "within grace"
        print(f"\n  [{tag}] {v['lane']}")
        print(f"      state         : {v['state']}")
        print(f"      degraded for  : {human(v['degraded_for'])}")
        if v["error"]:
            print(f"      error_code    : {v['error']}")
        if v["flag"] is not None:
            print(f"      needs_attention flag : {v['flag']}")
        if v["probe"]:
            print(f"      independent probe    : {v['probe']}")
    exp = [v for v in verdicts if v.get("expected_down")]
    if exp:
        print("\n  expected-down (config gaps, not incidents): "
              + ", ".join(v["lane"] for v in exp))
    print()
    print(f"  VERDICT: {len(over)} over threshold, {len(down)} degraded, "
          f"{len(verdicts)-len(down)} healthy")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
