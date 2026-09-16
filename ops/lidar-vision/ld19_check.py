#!/usr/bin/env python3
"""Check licenses + metadata for LD19 LiDAR software, and verify NURA's price/sourcing facts."""
import json
import re
import urllib.request

ENV = "/opt/data/profiles/nura/home/.secrets/github-nuratech-coder.env"
TOKEN = None
try:
    m = re.search(r"GITHUB_PAT_NURATECH_CODER=(\S+)", open(ENV, encoding="utf-8", errors="replace").read())
    if m:
        TOKEN = m.group(1).strip().strip("'\"")
except OSError:
    pass


def gh(path):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "nura-ld19/1.0"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(
                "https://api.github.com" + path, headers=h), timeout=25) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def raw(repo, fname, branches=("main", "master")):
    for br in branches:
        for p in (fname,):
            url = f"https://raw.githubusercontent.com/{repo}/{br}/{p}"
            try:
                with urllib.request.urlopen(urllib.request.Request(
                        url, headers={"User-Agent": "nura-ld19/1.0"}), timeout=20) as r:
                    return r.read().decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
    return None


REPOS = [
    "Myzhar/ldrobot-lidar-ros2",
    "ldrobotSensorTeam/ldlidar_stl_ros2",
    "TheNoobInventor/lidarbot",
    "Myzhar/MyzharBot",
]

print("=" * 92)
print("LD19 SOFTWARE — LICENSE + METADATA")
print("=" * 92)
for repo in REPOS:
    d = gh(f"/repos/{repo}")
    if "_error" in d or d.get("message"):
        print(f"\n  {repo}: not found / {d.get('message') or d.get('_error')}")
        continue
    lic_api = (d.get("license") or {}).get("spdx_id") or "NONE"
    print(f"\n  {repo}")
    print(f"    stars={d.get('stargazers_count')}  lang={d.get('language')}  "
          f"pushed={(d.get('pushed_at') or '')[:10]}")
    print(f"    api license field: {lic_api}")
    print(f"    {(d.get('description') or '')[:130]}")
    txt = None
    for fn in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE"):
        txt = raw(repo, fn)
        if txt:
            break
    if txt:
        head = " ".join(txt.split())[:150]
        print(f"    LICENSE file: {head}")
        low = txt.lower()
        if "apache license" in low and "2.0" in low:
            print("    -> Apache-2.0 (permissive) OK")
        elif "mit license" in low or "permission is hereby granted, free of charge" in low:
            print("    -> MIT (permissive) OK")
        elif "bsd" in low:
            print("    -> BSD (permissive) OK")
        elif "gnu general public" in low:
            print("    -> GPL (COPYLEFT - review before shipping)")
        elif "non-commercial" in low or "noncommercial" in low or "research only" in low:
            print("    -> NON-COMMERCIAL - BLOCKED for product use")
        else:
            print("    -> unrecognised licence text - counsel review")
    else:
        print("    ** NO LICENSE FILE - all rights reserved by default -> cannot use commercially **")

print("\n" + "=" * 92)
print("RELATED: NURA drones already spec'd for ROS2/PX4? (hardware chain check)")
print("=" * 92)
for f in ["/opt/data/Obsidian Vault/NURA-OS/Aero/EMS-Drone-Spec.md"]:
    try:
        t = open(f, encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    for kw in ["ROS", "PX4", "ArduPilot", "MAVLink", "Jetson", "Gazebo", "SITL"]:
        hits = [l.strip()[:150] for l in t.split("\n") if kw.lower() in l.lower()]
        if hits:
            print(f"  [{kw}]")
            for h in hits[:2]:
                print(f"     {h}")
