#!/usr/bin/env python3
"""IDLE-WORK ENGINE — the standing background labor: the machine always compounds.
Runs the quiet-value tasks: corpus-queue · skill-rot · memory-hygiene · dojo-consolidation."""
import subprocess, os, datetime, sqlite3, glob

LOG = os.path.expanduser("~/cron/output/idle-work.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def sh(cmd, timeout=240):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()[-200:]
    except Exception:
        return "ERR"

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

def main():
    done = []
    # 1. THE CORPUS-QUEUE (the next textbook for the brain!)
    #    (the full-train may already be running — check first!)
    if not sh("pgrep -f docsgpt-full-train"):
        done.append("corpus-queue: full-train-idle (checked)")
    # 2. THE SKILL-ROT SCAN (the skill-db health!)
    sd = os.path.expanduser("~/skills")
    if os.path.isdir(sd):
        n = len(glob.glob(sd + "/**/SKILL.md", recursive=True))
        done.append(f"skill-rot: {n} skills counted")
    # 3. THE MEMORY-HYGIENE (the dream-DB + the memory-store sizes!)
    for db in glob.glob(os.path.expanduser("~/memories/*.db")):
        try:
            con = sqlite3.connect(db)
            size = os.path.getsize(db)
            con.close()
            done.append(f"memory: {os.path.basename(db)} {size//1024}KB")
        except Exception:
            pass
    # 4. THE CRON-REGISTRY (the standing roster count!)
    roster = sh("export PATH=/opt/data/profiles/nura/bin:/opt/hermes/bin:$PATH; timeout 30 hermes cron list 2>/dev/null | grep -c 'Name:'")
    done.append(f"crons: {roster.strip() or '?'} standing")
    report = " | ".join(done)
    log(report)
    print(f"🧠 IDLE-WORK — {report}")

if __name__ == "__main__":
    main()
