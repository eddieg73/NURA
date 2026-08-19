#!/usr/bin/env python3
"""Life-organization inventory pass 1 — map drives, count, hash-dedupe buckets."""
import os, hashlib, json, collections

ROOTS = ["/opt/data", "/opt/data/Obsidian Vault"]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".cache", ".playwright", "datasets"}
EXT_MAP = collections.Counter()
TOTAL = {"files": 0, "bytes": 0, "dirs": 0}
HASHES = collections.defaultdict(list)
sample = []

for root in ROOTS:
    if not os.path.isdir(root):
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        TOTAL["dirs"] += len(dirnames)
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            try:
                st = os.stat(fp)
                if st.st_size == 0:
                    continue
                TOTAL["files"] += 1
                TOTAL["bytes"] += st.st_size
                ext = os.path.splitext(fn)[1].lower() or "(none)"
                EXT_MAP[ext] += 1
                if st.st_size < 2_000_000:
                    h = hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16]
                    HASHES[h].append(fp)
            except OSError:
                pass

dups = {h: paths for h, paths in HASHES.items() if len(paths) > 1}
print(f"FILES: {TOTAL['files']}  BYTES: {TOTAL['bytes']/1e9:.2f} GB  DIRS: {TOTAL['dirs']}")
print("TOP EXTENSIONS:", ", ".join(f"{k}:{v}" for k, v in EXT_MAP.most_common(12)))
print(f"EXACT-DUP BUCKETS: {len(dups)}  (files involved: {sum(len(v) for v in dups.values())})")
for h, paths in sorted(dups.items(), key=lambda x: -len(x[1]))[:8]:
    print("  DUP:", len(paths), "->", paths[0][:90], "|", paths[1][:90])
