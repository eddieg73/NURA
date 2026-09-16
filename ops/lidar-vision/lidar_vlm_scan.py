#!/usr/bin/env python3
"""Search the modern category: point-cloud / LiDAR + language & multimodal models (spatial understanding)."""
import json
import re
import urllib.parse
import urllib.request
from collections import OrderedDict

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
    "point cloud large language model 3d understanding",
    "lidar vision language model spatial reasoning",
    "3d scene graph llm robotics",
    "point cloud question answering",
    "depth anything monocular metric depth",
    "spatial intelligence vision language model embodied",
    "lidar to text scene description",
    "open vocabulary 3d point cloud detection",
]

PERMISSIVE = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "mpl-2.0", "isc",
              "cc0-1.0", "unlicense", "agpl-3.0"}


def gh(path, **params):
    url = "https://api.github.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    h = {"Accept": "application/vnd.github+json", "User-Agent": "nura-lidar-scan/1.0"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


seen = OrderedDict()
for q in QUERIES:
    d = gh("/search/repositories", q=q, sort="stars", order="desc", per_page=10)
    if "_error" in d:
        print(f"  [{q}] ERR {d['_error'][:90]}")
        continue
    for it in d.get("items") or []:
        n = it["full_name"]
        if n in seen:
            continue
        seen[n] = {
            "stars": it["stargazers_count"], "license": ((it.get("license") or {}).get("spdx_id") or "NONE"),
            "lang": it.get("language"), "desc": (it.get("description") or "")[:160],
            "pushed": (it.get("pushed_at") or "")[:10], "url": it["html_url"],
            "topics": it.get("topics") or [],
        }

rows = sorted(seen.items(), key=lambda kv: -kv[1]["stars"])
print(f"scanned {len(rows)} unique repos\n")
print(f"{'STARS':>7}  {'LICENSE':<14} {'PUSHED':<11} REPO")
print("-" * 106)
for n, d in rows[:45]:
    mark = "" if d["license"].lower() in PERMISSIVE else "  <-- CHECK"
    print(f"{d['stars']:>7}  {d['license']:<14} {d['pushed']:<11} {n}{mark}")

print("\n\n=== CANDIDATES: permissive + recent (pushed 2025+) + meaningful traction ===")
for n, d in rows:
    if d["license"].lower() in PERMISSIVE and d["stars"] >= 250 and d["pushed"] >= "2025-01-01":
        print(f"\n  {n}   ({d['stars']}★  {d['license']}  {d['lang']})")
        print(f"    {d['desc']}")
        print(f"    last push {d['pushed']}   {d['url']}")

json.dump(dict(rows), open("/opt/data/lidar_vlm_repos.json", "w"), indent=1)
print("\n-> /opt/data/lidar_vlm_repos.json")
