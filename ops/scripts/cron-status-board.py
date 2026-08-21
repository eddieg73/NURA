#!/usr/bin/env python3
"""CRON-STATUS-BOARD — the standing-roster status: every cron + its health + the last-run, rendered as the dashboard text!
The founder's board: ONE place that shows every standing job's state."""
import subprocess, os, datetime, json

def sh(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def main():
    lines = ["📋 CRON-STATUS-BOARD — " + datetime.datetime.now().strftime("%a %b %d, %H:%M EST")]
    lines.append("")
    # the roster via the hermes CLI (the JSON!)
    out = sh("export PATH=/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH; timeout 40 hermes cron list --json 2>/dev/null")
    try:
        jobs = json.loads(out) if out.startswith("[") or out.startswith("{") else []
        if isinstance(jobs, dict):
            jobs = jobs.get("jobs", jobs.get("data", []))
    except Exception:
        jobs = []
    if not jobs:
        # the fallback: the text-parse!
        txt = sh("export PATH=/opt/data/profiles/nura/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH; timeout 40 hermes cron list 2>/dev/null")
        lines.append("(the JSON-parse failed — the text-mode!)")
        lines.append(txt[:600])
    else:
        total = len(jobs)
        ok = sum(1 for j in jobs if str(j.get("enabled", True)).lower() == "true" and j.get("last_status") != "failed")
        fail = [j for j in jobs if j.get("last_status") == "failed"]
        lines.append(f"🟢 {ok}/{total} healthy · 🔴 {len(fail)} failing · ⏱ {total} total")
        lines.append("")
        lines.append("| # | Job | Schedule | Last | Status |")
        lines.append("|---|-----|----------|------|--------|")
        for i, j in enumerate(jobs[:25], 1):
            name = (j.get("name") or j.get("job_id") or "?")[:38]
            sched = (j.get("schedule") or "?")[:14]
            last = (j.get("last_run_at") or "-")[5:16] if j.get("last_run_at") else "-"
            st = "🟢" if j.get("last_status") != "failed" else "🔴"
            lines.append(f"| {i} | {name} | {sched} | {last} | {st} |")
        if len(jobs) > 25:
            lines.append(f"| ... | +{len(jobs)-25} more | | | |")
        if fail:
            lines.append("")
            lines.append("🔴 FAILING:")
            for j in fail[:5]:
                lines.append(f"  · {j.get('name','?')} ({j.get('last_run_at','-')[:16]})")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
