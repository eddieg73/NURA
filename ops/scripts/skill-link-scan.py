#!/usr/bin/env python3
"""Scan skill library for broken related_skills refs + pruned markers."""
import os, re, glob

SKILLS_ROOT = "/opt/data/profiles/nura/skills"
names = {}
for path in glob.glob(f"{SKILLS_ROOT}/**/SKILL.md", recursive=True):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
        m = re.search(r"^name:\s*(.+)$", text, re.M)
        if m:
            names[m.group(1).strip()] = path
    except Exception:
        pass

print(f"skills indexed: {len(names)}")

broken = []
for name, path in names.items():
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r"^related_skills:\s*\[(.*?)\]", text, re.M | re.S):
            refs = [r.strip().strip('"\'') for r in m.group(1).split(",") if r.strip()]
            for ref in refs:
                base = ref.split(":")[-1].strip()
                if base and base not in names:
                    broken.append((name, ref))
    except Exception:
        pass

print(f"broken related_skills refs: {len(broken)}")
for src, ref in broken[:30]:
    print(f"  {src} -> {ref}")

pruned = []
for path in glob.glob(f"{SKILLS_ROOT}/**/SKILL.md", recursive=True):
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
        if "[SKILL_PRUNED]" in text:
            pruned.append(path.replace(SKILLS_ROOT, "~"))
    except Exception:
        pass
print(f"files with [SKILL_PRUNED] markers: {len(pruned)}")
for p in pruned[:10]:
    print("  ", p)
