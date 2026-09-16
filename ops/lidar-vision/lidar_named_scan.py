#!/usr/bin/env python3
"""Look up the notable 3D/LiDAR vision projects by name, plus check NURA's own hardware context."""
import json
import re
import subprocess
import urllib.request

ENV_FILE = "/opt/data/profiles/nura/home/.secrets/github-nuratech-coder.env"
TOKEN = None
try:
    raw = open(ENV_FILE, encoding="utf-8", errors="replace").read()
    m = re.search(r"GITHUB_PAT_NURATECH_CODER=(\S+)", raw)
    if m:
        TOKEN = m.group(1).strip().strip("'\"")
except OSError:
    pass

NAMED = [
    "manycore-research/SpatialLM",
    "depth-anything/Depth-Anything-V2",
    "ByteDance-Seed/Depth-Anything-3",
    "facebookresearch/vggt",
    "naver/mast3r",
    "OpenRobotLab/PointLLM",
    "RUN2024/LEO",
    "embodied-generalist/embodied-generalist",
    "Pointcept/Pointcept",
    "isl-org/Open3D",
    "autowarefoundation/autoware",
    "koide3/direct_lidar_inertial_odometry",
    "AnyLoc/AnyLoc",
    "lmb-freiburg/3d-scene-graph",
    "OpenGVLab/InternVL",
]

PERMISSIVE = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "mpl-2.0", "isc",
              "cc0-1.0", "unlicense", "cc-by-4.0", "cc-by-sa-4.0", "agpl-3.0"}


def gh(path):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "nura-scan/1.0"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(
                "https://api.github.com" + path, headers=h), timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


print("=" * 100)
print("NAMED PROJECTS — 3D / LiDAR / spatial vision")
print("=" * 100)
found = {}
for full in NAMED:
    d = gh(f"/repos/{full}")
    if "_error" in d or d.get("message") == "Not Found":
        print(f"  ?  {full:<52} not found")
        continue
    lic = (d.get("license") or {}).get("spdx_id") or "NONE"
    found[full] = {"stars": d["stargazers_count"], "license": lic,
                   "pushed": (d.get("pushed_at") or "")[:10],
                   "desc": (d.get("description") or "")[:120],
                   "url": d["html_url"], "lang": d.get("language")}
    ok = "OK " if lic.lower() in PERMISSIVE else "LIC"
    print(f"  {ok} {d['stargazers_count']:>7}★  {lic:<14} {found[full]['pushed']:<11} {full}")
    print(f"        {found[full]['desc']}")

json.dump(found, open("/opt/data/lidar_named_repos.json", "w"), indent=1)

print("\n" + "=" * 100)
print("NURA HARDWARE / ROBOTICS CONTEXT — do we already have a LiDAR lane?")
print("=" * 100)
p = subprocess.run(
    ["grep", "-rli", "-E", "lidar|livox|ouster|velodyne|realsense|depth.?camera|rplidar",
     "/opt/data/NURA", "/opt/data/Obsidian Vault/NURA-OS", "/opt/data/profiles/nura/skills"],
    capture_output=True, text=True)
hits = [l for l in p.stdout.strip().split("\n") if l]
print(f"  files mentioning LiDAR/depth hardware: {len(hits)}")
for h in hits[:15]:
    print(f"    {h}")

p2 = subprocess.run(
    ["grep", "-rhoiE", "(livox|ouster|velodyne|rplidar|realsense|oak-d|hesai)[a-z0-9 \\-]{0,20}",
     "/opt/data/NURA", "/opt/data/Obsidian Vault/NURA-OS"],
    capture_output=True, text=True)
from collections import Counter
c = Counter(l.strip().lower() for l in p2.stdout.strip().split("\n") if l.strip())
print("\n  hardware named in NURA docs:")
for k, v in c.most_common(12):
    print(f"    {v:>3}x  {k}")
