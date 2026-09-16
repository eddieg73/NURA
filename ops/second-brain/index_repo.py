#!/usr/bin/env python3
"""
CLOSE THE RETRIEVAL GAP: the engineering artifacts are not in the brain.

FOUND BY THE VERIFICATION PROBE. Asking the index "DARPA ARES oxygen metrology validation" returned
an imported template file -- because the ARES work lives in the git repo at /opt/data/NURA/ops/ares/,
NOT in the Obsidian vault. The vault index therefore cannot see it.

That is a real hole. The vault is 92 MB dominated by an imported playbook tree, while the actual
engineering output of this operation (ARES rev-A.1 artifacts, workforce runbook, drone sensing audit,
URL reviews, Notion workspace tooling) sits outside the brain entirely.

FIX: index the repo's ops/ and key docs into the SAME collection with source="repo" so retrieval
spans both the vault and the engineering record. Idempotent, resumable, same checkpoint file.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, "/opt/data/lazy-packages")
os.environ.setdefault("PYTHONPATH", "/opt/data/lazy-packages:/opt/data/fastembed-pkgs")

COLL = "nura-vault"
QDRANT = "http://localhost:6333"
STATE = "/opt/data/vault_index_state.json"

# Engineering sources outside the vault
ROOTS = [
    ("/opt/data/NURA/ops", "repo"),
    ("/opt/data/NURA/README.md", "repo"),
    ("/opt/data/NURA/scripts", "repo"),
]
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "output"}


def log(m):
    print(m, flush=True)


log("=" * 84)
log("INDEXING THE ENGINEERING RECORD (repo -> nura-vault, source=repo)")
log("=" * 84)

state = json.load(open(STATE)) if os.path.exists(STATE) else {"done": []}
done = set(state.get("done", []))
log(f"  existing checkpoint: {len(done)} chunks")

points = []
files = 0
for root, src in ROOTS:
    if os.path.isfile(root):
        walk = [(os.path.dirname(root), [], [os.path.basename(root)])]
    else:
        walk = os.walk(root)
    for dirpath, dirs, fnames in walk:
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in fnames:
            if not f.endswith((".md", ".py", ".json", ".txt", ".yml", ".yaml")):
                continue
            p = os.path.join(dirpath, f)
            rel = "REPO/" + os.path.relpath(p, "/opt/data/NURA")
            try:
                txt = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if len(txt.strip()) < 60:
                continue
            files += 1
            # chunk: engineering files are code-heavy, keep them compact
            size = 1600
            chunks = [txt[i:i + size] for i in range(0, len(txt), size)]
            for i, c in enumerate(chunks):
                if len(c.strip()) < 60:
                    continue
                h = hashlib.sha256(f"{rel}:{i}:{c}".encode()).hexdigest()[:16]
                pid = hashlib.md5(f"nura-vault:{h}".encode()).hexdigest()
                pid = f"{pid[:8]}-{pid[8:12]}-{pid[12:16]}-{pid[16:20]}-{pid[20:32]}"
                if pid in done:
                    continue
                points.append({
                    "id": pid, "text": c, "rel": rel,
                    "title": os.path.basename(rel),
                    "chunk": i, "folder": "REPO",
                    "playbook": False, "source": src,
                })

log(f"  files scanned : {files}")
log(f"  new chunks    : {len(points)}")

if not points:
    log("  nothing new — already current")
    sys.exit(0)

import requests  # noqa: E402
from fastembed import TextEmbedding  # noqa: E402

model = TextEmbedding(model_name="BAAI/bge-base-en-v1.5")
log("  model loaded")

ok = fail = 0
BATCH = 24
import time  # noqa: E402
t0 = time.time()
for i in range(0, len(points), BATCH):
    batch = points[i:i + BATCH]
    try:
        vecs = [v.tolist() for v in model.embed([b["text"] for b in batch])]
        rr = requests.put(f"{QDRANT}/collections/{COLL}/points?wait=true", timeout=180,
                          json={"points": [
                              {"id": b["id"], "vector": vecs[j],
                               "payload": {k: v for k, v in b.items() if k != "id"}}
                              for j, b in enumerate(batch)]})
        if rr.status_code >= 300:
            log(f"    upsert failed at {i}: HTTP {rr.status_code}")
            fail += len(batch)
            continue
    except Exception as e:
        log(f"    exception at {i}: {e}")
        fail += len(batch)
        continue
    ok += len(batch)
    done.update(b["id"] for b in batch)
    json.dump({"done": list(done)}, open(STATE, "w"))
    if (i // BATCH) % 5 == 0 or i + BATCH >= len(points):
        el = time.time() - t0
        rate = ok / el if el else 0
        eta = (len(points) - ok) / rate / 60 if rate else 0
        log(f"    {ok}/{len(points)}  {rate:.1f} ch/s  ETA {eta:.0f} min  total {len(done)}")

time.sleep(2)
info = requests.get(f"{QDRANT}/collections/{COLL}", timeout=20).json().get("result", {})
log("")
log(f"  upserted {ok}, failed {fail}")
log(f"  collection total: {info.get('points_count')}")

# ---- prove the gap is closed ---------------------------------------------
log("\n  RETEST — 'DARPA ARES oxygen metrology validation':")
v = list(model.embed(["DARPA ARES oxygen metrology validation requirements"]))[0].tolist()
res = requests.post(f"{QDRANT}/collections/{COLL}/points/search", timeout=90,
                    json={"vector": v, "limit": 5, "with_payload": True}).json().get("result", [])
for h in res:
    log(f"    {h['score']:.3f}  {h['payload']['rel'][:74]}")

log("\n  RETEST — 'drone LiDAR sensing gap audit':")
v = list(model.embed(["drone LiDAR sensing gap audit downward rangefinder"]))[0].tolist()
res = requests.post(f"{QDRANT}/collections/{COLL}/points/search", timeout=90,
                    json={"vector": v, "limit": 5, "with_payload": True}).json().get("result", [])
for h in res:
    log(f"    {h['score']:.3f}  {h['payload']['rel'][:74]}")
