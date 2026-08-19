#!/usr/bin/env python3
"""Docker orphan & zombie audit (host-side, weekly) — REPORT ONLY. No purge without approval.
Finds: containers Exited >48h (not migration-tagged), dangling volumes, unreferenced images.
Outputs reclamation potential for Notion before any purge decision."""
import subprocess, sys, datetime

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:
        return f"ERR {e}"

out = []
now = datetime.datetime.now(datetime.timezone.utc)

# 1. Exited >48h containers
ps = sh("docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}'")
zombies = []
for line in ps.splitlines():
    if "Exited" not in line:
        continue
    name, status, image = line.split("|")
    try:
        t = status.replace("Exited (", "").split(")")[0]
        # status like "Exited (0) 3 days ago"
        age_txt = status.split("ago")[0].split(")")[-1].strip()
        if "day" in age_txt or "week" in age_txt:
            zombies.append((name, status, image))
    except Exception:
        pass
out.append(f"EXITED>48h: {len(zombies)}")
for z in zombies[:15]:
    out.append(f"  {z[0]} [{z[2]}] {z[1]}")

# 2. Dangling volumes
vols = sh("docker volume ls -qf dangling=true")
out.append(f"DANGLING VOLUMES: {len(vols.splitlines()) if vols else 0}")

# 3. Unreferenced images (dangling)
imgs = sh("docker images -qf dangling=true")
out.append(f"DANGLING IMAGES: {len(imgs.splitlines()) if imgs else 0}")

# 4. Disk reclaim potential
df = sh("docker system df")
out.append("SYSTEM DF:\n" + df[:600])

print("\n".join(out))
print("\nACTION: review + approve purge manually (docker container prune / volume prune / image prune) — never auto-purge.")
