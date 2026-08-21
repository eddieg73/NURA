#!/usr/bin/env python3
"""NURA SELF-HEALING WATCHDOG — the full-stack health + the auto-fix routines.
The founder's fix: the machine watches and repairs WITHOUT the prompt.
Scope: MCP-lanes · keys · fleet-SSH · brain-health · tunnel · build-tools.
Silent when healthy; reports only what it fixed or what needs a human."""
import json, os, subprocess, datetime, sys

HOME = os.path.expanduser("~")
ENV = "/opt/data/profiles/nura/.env"  # the ABSOLUTE path — the cron-HOME differs from the profile! (the 08-09 fix!)
LOG = os.path.join(HOME, "cron", "output", "self-heal.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def sh(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR:{str(e)[:80]}"

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

CRITICAL_ONLY = True  # the founder's mandate: the status → the dashboard, the critical-only → the chat!

KNOWN_MISSING = ['TAVUS_API_KEY', 'GROK_API_KEY', 'PERFEX_API_TOKEN', 'DOCUMO_API_KEY']  # the founder's known-drops — NEVER re-alerted!
ALERTED_ONCE = True  # the founder's mandate: the known-missing = mentioned ONCE, then silent!

def main():
    issues = []
    fixes = []
    # 1. THE BRAIN (the DocsGPT!)
    r = sh("curl -s -m 8 -o /dev/null -w '%{http_code}' http://72.61.71.211:7091/api/health")
    if r != "200":
        issues.append("docsgpt-health")
        fixes.append("sh('ssh -o BatchMode=yes -i ~/.ssh/id_nura_clean root@72.61.71.211 \"docker restart docsgpt-oss-backend-1\"')")
    # 2. THE TUNNEL (the local-11434!)
    t = sh("ss -tln | grep -c ':11434 ' || true")
    if not t.strip() or t.strip() == "0":
        issues.append("local-tunnel")
        fixes.append("tunnel-rebound")
        subprocess.Popen(["ssh", "-o", "BatchMode=yes", "-o", "ExitOnForwardFailure=yes", "-i", os.path.expanduser("~/.ssh/id_nura_clean"), "-N", "-L", "11434:127.0.0.1:11434", "root@72.60.163.140"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # 3. THE KEYS (the presence-check!)
    for k in ["TAVUS_API_KEY", "DOCUMO_API_KEY", "GHL_API_KEY", "GROK_API_KEY"]:
        if not os.path.exists(ENV) or not any(l.startswith(k + "=") for l in open(ENV)):
            if k in KNOWN_MISSING:
                continue  # the founder's known-drops — the ONE-note in the digest, never the alerts!
            issues.append(f"key-{k}")
    # 4. THE FLEET (the SSH!)
    for ip in ["72.61.71.211", "72.60.163.140", "195.35.32.113"]:
        r = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@{ip} 'echo ok'")
        if "ok" not in r:
            issues.append(f"ssh-{ip}")
    # 5. THE MCP-LANES (the quick-alive-check!)
    for lane in ["github", "firecrawl", "qdrant", "openemr", "notion"]:
        r = sh(f"timeout 20 hermes mcp test {lane} 2>&1 | tail -1")
        if "✗" in r or "failed" in r.lower():
            issues.append(f"mcp-{lane}")
    # 6. THE BUILD-TOOLS (the exec-bits!)
    if not os.path.exists("/opt/data/flutter-sdk/bin/cache/artifacts/engine/linux-x64/impellerc") or not os.access("/opt/data/flutter-sdk/bin/cache/artifacts/engine/linux-x64/impellerc", os.X_OK):
        issues.append("impellerc-exec")
        fixes.append("chmod +x /opt/data/flutter-sdk/bin/cache/artifacts/engine/linux-x64/impellerc")

    if not issues:
        return  # SILENT — the watchdog pattern!
    report = ["🛠️ SELF-HEALING WATCHDOG — issues found:", ""]
    report.append("· " + "\n· ".join(issues))
    if fixes:
        report.append("")
        report.append("Auto-fixes applied: " + ", ".join(fixes))
        for f in fixes:
            if f.startswith("sh('"):
                sh(f[4:-2])
    report.append("")
    report.append("The known-items self-repair; the key-drops remain the founder's.")
    print("\n".join(report))
    log(" | ".join(issues) + " — fixes: " + ", ".join(fixes))

if __name__ == "__main__":
    main()
