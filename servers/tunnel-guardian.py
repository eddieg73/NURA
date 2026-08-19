#!/usr/bin/env python3
"""TUNNEL GUARDIAN — the persistent-tunnel manager: keeps BOTH tunnels alive, auto-rebinds, logs.
The fix for the recurring tunnel-deaths (the background-processes die with the session!)."""
import subprocess, os, sys, time, datetime

LOG = "/opt/data/profiles/nura/cron/output/tunnel-guardian.log"
os.makedirs(os.path.dirname(LOG), exist_ok=True)
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ExitOnForwardFailure=yes", "-o", "ServerAliveInterval=30",
       "-i", os.path.expanduser("~/.ssh/id_nura_clean")]
TUNNELS = [
    {"name": "11434-ollama", "args": ["-N", "-L", "11434:127.0.0.1:11434", "root@72.60.163.140"], "port": 11434},
    {"name": "1080-socks",   "args": ["-N", "-D", "1080", "root@72.60.163.140"], "port": 1080},
]

def log(msg):
    with open(LOG, "a") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

def port_open(port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except Exception:
        return False
    finally:
        s.close()

def main():
    changed = []
    for t in TUNNELS:
        if port_open(t["port"]):
            continue  # alive — silent!
        # rebind
        proc = subprocess.Popen(SSH + t["args"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        time.sleep(2)
        if port_open(t["port"]):
            log(f"REBOUND {t['name']} (pid {proc.pid})")
            changed.append(t["name"])
        else:
            log(f"FAILED {t['name']}")
            changed.append(f"{t['name']}-FAIL")
    if changed:
        print(f"🔧 TUNNEL-GUARDIAN: rebound {', '.join(changed)}")
    # else: silent-when-healthy

if __name__ == "__main__":
    main()
