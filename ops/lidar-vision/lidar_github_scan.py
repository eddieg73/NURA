#!/usr/bin/env python3
"""Search GitHub for LiDAR-based vision/perception projects, filtered by license and traction."""
import json
import os
import re
import urllib.parse
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

QUERIES = [
    "lidar obstacle avoidance real-time",
    "lidar camera fusion perception",
    "lidar slam navigation ROS2",
    "lidar depth estimation neural network",
    "3d gaussian splatting lidar reconstruction",
    "lidar point cloud segmentation",
]

# permissive-only by default: MIT / Apache-2.0 / BSD
PERMISSIVE = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "mpl-2.0", "isc"}


def gh(path, **params):
    url = "https://api.github.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nura-lidar-scan/1.0"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


seen = {}
for q in QUERIES:
    data = gh("/search/repositories", q=q, sort="stars", order="desc", per_page=12)
    items = data.get("items") or []
    if not items and "_error" in data:
        print(f"  [{q}] ERROR {data['_error'][:100]}")
        continue
    for it in items:
        name = it["full_name"]
        if name in seen:
            continue
        lic = ((it.get("license") or {}).get("spdx_id") or "NONE")
        seen[name] = {
            "stars": it["stargazers_count"],
            "license": lic,
            "lang": it.get("language"),
            "desc": (it.get("description") or "")[:150],
            "pushed": (it.get("pushed_at") or "")[:10],
            "url": it["html_url"],
            "topics": it.get("topics") or [],
        }

rows = sorted(seen.items(), key=lambda kv: -kv[1]["stars"])
print(f"scanned {len(rows)} unique repos\n")
print(f"{'STARS':>7}  {'LICENSE':<14} {'PUSHED':<11} REPO")
print("-" * 104)
for name, d in rows[:40]:
    flag = "" if d["license"].lower() in PERMISSIVE else "  <-- license check"
    print(f"{d['stars']:>7}  {d['license']:<14} {d['pushed']:<11} {name}{flag}")

print("\n\n=== TOP PERMISSIVE CANDIDATES (commercially usable) ===")
for name, d in rows:
    if d["license"].lower() in PERMISSIVE and d["stars"] >= 300:
        print(f"\n  {name}  ({d['stars']} stars, {d['license']}, {d['lang']})")
        print(f"    {d['desc']}")
        print(f"    pushed {d['pushed']}   {d['url']}")
        if d["topics"]:
            print(f"    topics: {', '.join(d['topics'][:10])}")

json.dump({k: v for k, v in rows}, open("/opt/data/lidar_repos.json", "w"), indent=1)
print("\n-> /opt/data/lidar_repos.json")
