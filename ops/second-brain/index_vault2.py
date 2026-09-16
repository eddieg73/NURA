#!/usr/bin/env python3
"""
VAULT INDEX v2 — resumable, incremental, bounded memory.

WHY v1 WAS SCRAPPED (measured, not guessed):
  v1 embedded 64 chunks in 181s = 2.83 s/chunk -> 6,466 chunks = 5.1 HOURS.
  Its design accumulated every vector in a Python list and upserted once at the end,
  so an interruption at hour 5 would have lost ALL of it. That is unacceptable on a
  contended host (swap was 4092/4095 MB = full, load avg 3+).

  Note: v1 was ALSO misdiagnosed. The background wrapper reported "exit code 0" while the
  python job was still running -- the shell returned immediately because of `nohup ... &`.
  A wrapper's exit code is not the job's status. Same class of error as everything else
  documented this session: the instrument, not the work, was lying.

v2 CHANGES:
  1. UPSERT PER BATCH -- progress is durable the moment each batch is embedded. No end-of-run
     cliff, no accumulating memory.
  2. CHECKPOINT FILE -- already-indexed chunk ids are skipped on resume. Ctrl-C, OOM, or a
     5-hour runtime all become harmless; just re-run.
  3. SMALLER BATCH -- 24 instead of 64, to keep peak memory down given a full swap.
  4. PROGRESS TO DISK every batch, so `tail` shows real movement (v1 buffered stdout).
  5. --limit and --folder flags for incremental/targeted runs.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import uuid

sys.path.insert(0, "/opt/data/lazy-packages")
os.environ.setdefault("PYTHONPATH", "/opt/data/lazy-packages:/opt/data/fastembed-pkgs")

VAULT = "/opt/data/Obsidian Vault"
COLL = "nura-vault"
QDRANT = "http://localhost:6333"
DIM = 768
STATE = "/opt/data/vault_index_state.json"
SKIP_DIRS = {"_trash", ".obsidian", ".git", "node_modules", ".smart-env"}

ap = argparse.ArgumentParser()
ap.add_argument("--limit", type=int, default=0, help="max chunks this run (0 = all)")
ap.add_argument("--folder", default="", help="only this top-level folder")
ap.add_argument("--batch", type=int, default=24)
ap.add_argument("--reset", action="store_true", help="ignore checkpoint")
args = ap.parse_args()


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open("/opt/data/vault_index_state.log", "a") as fh:
        fh.write(line + "\n")


import requests  # noqa: E402

# ---- checkpoint ------------------------------------------------------------
state = {"done": [], "started": time.time()}
if os.path.exists(STATE) and not args.reset:
    try:
        state = json.load(open(STATE))
    except Exception:
        pass
done = set(state.get("done", []))

log("=" * 72)
log(f"VAULT INDEX v2 — resumable. already indexed: {len(done)} chunks")
log("=" * 72)

# ---- 1. discover + chunk (deterministic ids) ------------------------------
def is_playbook(rel):
    return rel.startswith("NURA-OS/Atlas-Playbook")


def chunk_md(text):
    lines = text.split("\n")
    fm = ""
    if lines and lines[0].strip() == "---":
        for i in range(1, min(len(lines), 40)):
            if lines[i].strip() == "---":
                fm = "\n".join(lines[: i + 1])
                lines = lines[i + 1:]
                break
    body = "\n".join(lines)
    if len(body) <= 1400:
        s = (fm + "\n" + body).strip()
        return [s] if s else []
    out, cur, curlen = [], [], 0
    for ln in lines:
        if ln.startswith("#") and curlen > 900:
            out.append("\n".join(cur).strip())
            cur, curlen = [ln], len(ln)
            continue
        cur.append(ln)
        curlen += len(ln) + 1
        if curlen > 1800:
            out.append("\n".join(cur).strip())
            cur, curlen = [], 0
    if cur:
        out.append("\n".join(cur).strip())
    return [c for c in out if len(c) > 60]


points = []
for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith(".md"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, VAULT)
        if args.folder and not rel.startswith(args.folder):
            continue
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if len(txt.strip()) < 40:
            continue
        for i, c in enumerate(chunk_md(txt)):
            h = hashlib.sha256(f"{rel}:{i}:{c}".encode()).hexdigest()[:16]
            pid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"nura-vault:{h}"))
            if pid in done:
                continue
            points.append({
                "id": pid, "text": c, "rel": rel,
                "title": rel.split("/")[-1].replace(".md", ""),
                "chunk": i,
                "folder": rel.split("/")[0] if "/" in rel else "(root)",
                "playbook": is_playbook(rel),
            })

log(f"remaining to index: {len(points)} chunks")
if args.limit:
    points = points[: args.limit]
    log(f"limited this run to: {len(points)}")
if not points:
    log("nothing to do — index is current")
    sys.exit(0)

# ---- 2. collection --------------------------------------------------------
r = requests.get(f"{QDRANT}/collections/{COLL}", timeout=15)
if r.status_code != 200:
    rc = requests.put(f"{QDRANT}/collections/{COLL}", timeout=30,
                      json={"vectors": {"size": DIM, "distance": "Cosine"}})
    log(f"created collection {COLL}: HTTP {rc.status_code}")
else:
    log(f"collection {COLL} exists")

# ---- 3. embed + upsert PER BATCH (the v2 fix) ----------------------------
log("loading fastembed (BAAI/bge-base-en-v1.5)...")
from fastembed import TextEmbedding  # noqa: E402

model = TextEmbedding(model_name="BAAI/bge-base-en-v1.5")
log("model loaded")

ok = fail = 0
t0 = time.time()
for i in range(0, len(points), args.batch):
    batch = points[i:i + args.batch]
    try:
        vecs = [v.tolist() for v in model.embed([b["text"] for b in batch])]
    except Exception as e:
        log(f"  embed FAILED at {i}: {e}")
        fail += len(batch)
        continue

    payload = {"points": [
        {"id": b["id"], "vector": vecs[j],
         "payload": {k: v for k, v in b.items() if k != "id"}}
        for j, b in enumerate(batch)]}
    try:
        rr = requests.put(f"{QDRANT}/collections/{COLL}/points?wait=true",
                          json=payload, timeout=180)
        if rr.status_code >= 300:
            log(f"  upsert FAILED at {i}: HTTP {rr.status_code} {rr.text[:120]}")
            fail += len(batch)
            continue
    except Exception as e:
        log(f"  upsert exception at {i}: {e}")
        fail += len(batch)
        continue

    ok += len(batch)
    done.update(b["id"] for b in batch)
    # CHECKPOINT AFTER EVERY BATCH -- this is what makes the run survivable
    json.dump({"done": list(done), "started": state.get("started", time.time())},
              open(STATE, "w"))
    if (i // args.batch) % 5 == 0 or i + args.batch >= len(points):
        el = time.time() - t0
        rate = ok / el if el else 0
        remaining = len(points) - ok
        eta = remaining / rate / 60 if rate else 0
        log(f"  {ok}/{len(points)} this run  |  {rate:.1f} chunks/s  |  "
            f"ETA {eta:.0f} min  |  total indexed {len(done)}")

# ---- 4. verify by re-read -------------------------------------------------
time.sleep(2)
info = requests.get(f"{QDRANT}/collections/{COLL}", timeout=20).json().get("result", {})
cnt = info.get("points_count", 0)
log("")
log(f"RESULT this run: upserted {ok}, failed {fail}")
log(f"CHECKPOINT total indexed: {len(done)}")
log(f"QDRANT nura-vault points: {cnt}")
log(f"remaining after this run: {len(points) - ok}")
log(f"{'PASS' if ok else 'NOTHING WRITTEN'} — run again to continue")
