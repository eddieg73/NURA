#!/usr/bin/env python3
"""Find 3D/spatial LLM repos by SEARCH (not guessed paths) and license-check each."""
import json
import re
import urllib.parse
import urllib.request

ENV = "/opt/data/profiles/nura/home/.secrets/github-nuratech-coder.env"
TOKEN = None
try:
    m = re.search(r"GITHUB_PAT_NURATECH_CODER=(\S+)", open(ENV, encoding="utf-8", errors="replace").read())
    if m:
        TOKEN = m.group(1).strip().strip("'\"")
except OSError:
    pass

QUERIES = [
    "3D LLM point cloud language model",
    "spatial reasoning vision language model 3D",
    "point cloud large language model",
    "3d scene understanding LLM indoor",
    "embodied agent 3D world language model",
    "spatiallm alternative point cloud LLM",
]


def gh(path, **params):
    url = "https://api.github.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    h = {"Accept": "application/vnd.github+json", "User-Agent": "nura-spatial2/1.0"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=28) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def license_text(repo):
    for br in ("main", "master"):
        for fn in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "LICENSE-CODE"):
            try:
                with urllib.request.urlopen(urllib.request.Request(
                        f"https://raw.githubusercontent.com/{repo}/{br}/{fn}",
                        headers={"User-Agent": "nura-spatial2/1.0"}), timeout=15) as r:
                    return r.read().decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
    return None


def classify(txt):
    if not txt:
        return "NONE"
    low = " ".join(txt.split()).lower()
    if "llama 3" in low or "llama materials" in low:
        return "LLAMA-COMMUNITY"
    if "research materials" in low or ("meta" in low and "acceptable use policy" in low):
        return "META-RESEARCH"
    if "apache license" in low and "2.0" in low:
        return "APACHE-2.0"
    if "mit license" in low or "permission is hereby granted, free of charge" in low:
        return "MIT"
    if "bsd" in low and "redistribution" in low:
        return "BSD"
    if "non-commercial" in low or "noncommercial" in low:
        return "NON-COMMERCIAL"
    if "gnu general public" in low:
        return "GPL"
    if "creative commons" in low:
        return "CC"
    return "OTHER"


seen = {}
for q in QUERIES:
    d = gh("/search/repositories", q=q, sort="stars", order="desc", per_page=12)
    if "_error" in d:
        print(f"  [{q}] ERR {d['_error'][:80]}")
        continue
    for it in d.get("items") or []:
        n = it["full_name"]
        if n in seen:
            continue
        seen[n] = {"stars": it["stargazers_count"], "lang": it.get("language"),
                   "desc": (it.get("description") or "")[:110],
                   "pushed": (it.get("pushed_at") or "")[:10],
                   "api_lic": ((it.get("license") or {}).get("spdx_id") or "NONE")}

# license-check the plausible ones (avoid hammering for 100 repos)
cands = [(n, d) for n, d in seen.items()
         if d["stars"] >= 100 and any(k in (d["desc"] + n).lower()
         for k in ("3d", "point cloud", "spatial", "embodied", "scene"))]
cands.sort(key=lambda kv: -kv[1]["stars"])
print(f"search hits: {len(seen)}   licence-checking top {min(len(cands),22)}\n")
print("=" * 100)
print("3D / SPATIAL LANGUAGE MODELS — VERIFIED LICENCE")
print("=" * 100)
out = []
for n, d in cands[:22]:
    kind = classify(license_text(n))
    out.append((n, kind, d))
    flag = "OK " if kind in ("MIT", "APACHE-2.0", "BSD") else "!! "
    print(f"  {flag}{kind:<16} {d['stars']:>6}★ {d['pushed']}  {n}")
    print(f"        {d['desc'][:95]}")
    if kind in ("LLAMA-COMMUNITY", "META-RESEARCH", "NONE", "NON-COMMERCIAL", "OTHER"):
        print(f"        ^^ API said {d['api_lic']} — the FILE says {kind} (files win)")

json.dump([{"repo": n, "license": k, "stars": d["stars"]} for n, k, d in out],
          open("/opt/data/spatial_lm_scan2.json", "w"), indent=1)
