#!/usr/bin/env python3
"""
Is there a PERMISSIVE spatial/3D language model, or is Meta's the only option?

Checks the actual LICENSE file of every notable 3D/spatial LLM, because the GitHub API's
spdx_id is unreliable (it reports NOASSERTION for Llama licences AND for plain MIT with an
odd LICENSE header).
"""
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

NAMED = [
    # spatial / 3D LLMs
    ("manycore-research/SpatialLM", "spatial LLM (the Meta one)"),
    ("SpatialVLM/SpatialVLM", "google spatial VLM"),
    ("microsoft/SpatialVLM", "ms spatial VLM"),
    ("zd11024/Chat-3D", "Chat-3D"),
    ("UCSD-ERL/LL3DA", "LL3DA"),
    ("ZiyuGuo99/LLaVA-3D", "LLaVA-3D"),
    ("ZhenglinZhou/ShapeLLM", "ShapeLLM"),
    ("pku-lmzp/GPT4Point", "GPT4Point"),
    ("UMass-Flora-Lab/3D-LLM", "3D-LLM"),
    ("IndexTeam/SpatialRGPT", "SpatialRGPT"),
    ("dvlab-research/Cube-LLM", "Cube-LLM"),
    ("LaVi-Lab/Video-3D-LLM", "Video-3D-LLM"),
    ("embodied-generalist/embodied-generalist", "LEO (already cleared, MIT)"),
    # permissive VLMs that can BE the spatial layer
    ("QwenLM/Qwen2.5-VL", "Qwen2.5-VL"),
    ("QwenLM/Qwen3-VL", "Qwen3-VL"),
    ("OpenGVLab/InternVL", "InternVL"),
    ("OpenBMB/MiniCPM-V", "MiniCPM-V"),
    ("deepseek-ai/DeepSeek-VL2", "DeepSeek-VL2"),
    # geometry-first (no LLM) but permissive
    ("Pointcept/Pointcept", "Pointcept"),
    ("facebookresearch/dinov2", "DINOv2"),
]

PERMISSIVE = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "mpl-2.0", "isc"}


def gh(path):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "nura-spatial/1.0"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(
                "https://api.github.com" + path, headers=h), timeout=25) as r:
            return json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001
        return {"_error": str(e)}


def license_text(repo):
    for br in ("main", "master"):
        for fn in ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "LICENSE-CODE"):
            try:
                with urllib.request.urlopen(urllib.request.Request(
                        f"https://raw.githubusercontent.com/{repo}/{br}/{fn}",
                        headers={"User-Agent": "nura-spatial/1.0"}), timeout=18) as r:
                    return r.read().decode("utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
    return None


def classify(txt):
    if not txt:
        return "NONE", "no licence file -> all rights reserved"
    low = " ".join(txt.split()).lower()
    if "llama 3" in low or "llama materials" in low or "meta platforms" in low and "community license" in low:
        return "LLAMA-COMMUNITY", "Meta proprietary community licence"
    if "research materials" in low or ("meta" in low and "acceptable use policy" in low):
        return "META-RESEARCH", "Meta research licence + AUP"
    if "apache license" in low and "2.0" in low:
        return "APACHE-2.0", "permissive"
    if "mit license" in low or "permission is hereby granted, free of charge" in low:
        return "MIT", "permissive"
    if "bsd" in low and "redistribution" in low:
        return "BSD", "permissive"
    if "non-commercial" in low or "noncommercial" in low or "academic" in low and "only" in low:
        return "NON-COMMERCIAL", "blocked for product"
    if "gnu general public" in low:
        return "GPL", "copyleft"
    if "creative commons" in low:
        return "CC", "check variant (NC/SA?)"
    return "OTHER", txt[:70].replace("\n", " ")


print("=" * 104)
print("SPATIAL / 3D LANGUAGE MODELS — LICENCE REALITY CHECK (read from the LICENSE file)")
print("=" * 104)
rows = []
for repo, label in NAMED:
    d = gh(f"/repos/{repo}")
    if "_error" in d or d.get("message"):
        print(f"  ?  {repo:<48} not found")
        continue
    kind, why = classify(license_text(repo))
    stars = d.get("stargazers_count", 0)
    rows.append((repo, label, kind, stars, why, (d.get("pushed_at") or "")[:10],
                 (d.get("description") or "")[:90]))

rows.sort(key=lambda r: (r[2] not in ("MIT", "APACHE-2.0", "BSD"), -r[3]))
for repo, label, kind, stars, why, pushed, desc in rows:
    ok = "OK " if kind in ("MIT", "APACHE-2.0", "BSD") else "!! "
    print(f"  {ok}{kind:<16} {stars:>7}★ {pushed}  {repo}")
    print(f"      {label} — {why}")
    if desc:
        print(f"      {desc}")

print("\n" + "=" * 104)
print("PERMISSIVELY LICENSED OPTIONS")
print("=" * 104)
good = [r for r in rows if r[2] in ("MIT", "APACHE-2.0", "BSD")]
if good:
    for repo, label, kind, stars, why, pushed, _ in good:
        print(f"  {kind:<12} {stars:>7}★  {repo:<46} ({label})")
else:
    print("  none found")
json.dump([{"repo": r[0], "label": r[1], "license": r[2], "stars": r[3]} for r in rows],
          open("/opt/data/spatial_lm_licenses.json", "w"), indent=1)
