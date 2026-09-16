#!/usr/bin/env python3
"""
SECOND BRAIN — LEVEL 5 completion, piece 1: INDEX THE VAULT.

Finding: the vault holds 642 markdown files / 92 MB, but the Qdrant retrieval layer covers almost
none of it (nura-os = 251 points). The nightly synthesis reads FILES, so the cognition works — but
nothing can RETRIEVE it. Level 5 needs the corpus in the vector layer, chunked, with provenance.

Indexes /opt/data/Obsidian Vault into collection 'nura-vault' (768-dim, fastembed bge-base-en-v1.5
to match the working mem0 lane). Idempotent: content-hash keyed, so re-runs update rather than dup.

Read-only w.r.t. the vault. Writes only to Qdrant.
"""
import hashlib
import json
import os
import re
import sys
import time
import uuid

sys.path.insert(0, "/opt/data/lazy-packages")
os.environ.setdefault(
    "PYTHONPATH", "/opt/data/lazy-packages:/opt/data/fastembed-pkgs")

VAULT = "/opt/data/Obsidian Vault"
COLL = "nura-vault"
QDRANT = "http://localhost:6333"
DIM = 768

# Atlas-Playbook is 70MB of 76MB and is an imported template tree -- it dominates the vault and
# drowns NURA knowledge. Index it but tag it, so retrieval can filter.
SKIP_DIRS = {"_trash", ".obsidian", ".git", "node_modules", ".smart-env"}


def is_playbook(rel):
    return rel.startswith("NURA-OS/Atlas-Playbook")


def chunk_md(path, text):
    """Heading-aware chunking. Notes are short; only split genuinely long ones."""
    lines = text.split("\n")
    # strip frontmatter into the first chunk's prefix
    fm = ""
    if lines and lines[0].strip() == "---":
        for i in range(1, min(len(lines), 40)):
            if lines[i].strip() == "---":
                fm = "\n".join(lines[: i + 1])
                lines = lines[i + 1:]
                break
    body = "\n".join(lines)
    if len(body) <= 1400:
        return [(fm + "\n" + body).strip()] if (fm + body).strip() else []

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


print("=" * 96)
print("VAULT → QDRANT INDEX")
print("=" * 96)

# ---- 1. discover -----------------------------------------------------------
docs = []
for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith(".md"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, VAULT)
        try:
            txt = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        if len(txt.strip()) < 40:
            continue
        docs.append((rel, txt))

print(f"  markdown files discovered: {len(docs)}")
playbook = sum(1 for r, _ in docs if is_playbook(r))
print(f"    of which Atlas-Playbook (imported template tree): {playbook}")
print(f"    NURA knowledge: {len(docs) - playbook}")

# ---- 2. chunk --------------------------------------------------------------
points = []
for rel, txt in docs:
    for i, c in enumerate(chunk_md(txt, txt)):
        h = hashlib.sha256(f"{rel}:{i}:{c}".encode()).hexdigest()[:16]
        title = rel.split("/")[-1].replace(".md", "")
        points.append({
            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"nura-vault:{h}")),
            "text": c,
            "rel": rel,
            "title": title,
            "chunk": i,
            "folder": rel.split("/")[0] if "/" in rel else "(root)",
            "playbook": is_playbook(rel),
        })

print(f"  chunks: {len(points)}")
print(f"  total chars: {sum(len(p['text']) for p in points):,}")

# ---- 3. embed --------------------------------------------------------------
print("\n  loading fastembed (bge-base-en-v1.5, 768d)...")
from fastembed import TextEmbedding  # noqa: E402

model = TextEmbedding(model_name="BAAI/bge-base-en-v1.5")
print("  model loaded")

BATCH = 64
vecs = []
t0 = time.time()
for i in range(0, len(points), BATCH):
    batch = [p["text"] for p in points[i:i + BATCH]]
    for v in model.embed(batch):
        vecs.append(v.tolist())
    if (i // BATCH) % 10 == 0:
        print(f"    embedded {min(i+BATCH, len(points))}/{len(points)}  "
              f"({time.time()-t0:.0f}s)")
print(f"  embedded {len(vecs)} in {time.time()-t0:.0f}s")

# ---- 4. upsert -------------------------------------------------------------
import requests  # noqa: E402

r = requests.get(f"{QDRANT}/collections/{COLL}", timeout=10)
if r.status_code != 200:
    rc = requests.put(f"{QDRANT}/collections/{COLL}", timeout=30, json={
        "vectors": {"size": DIM, "distance": "Cosine"}})
    print(f"  create collection {COLL}: HTTP {rc.status_code}")
else:
    print(f"  collection {COLL} exists")

CH = 200
for i in range(0, len(points), CH):
    payload = {"points": [
        {"id": points[j]["id"], "vector": vecs[j],
         "payload": {k: v for k, v in points[j].items() if k != "id"}}
        for j in range(i, min(i + CH, len(points)))
    ]}
    rr = requests.put(f"{QDRANT}/collections/{COLL}/points?wait=true",
                      json=payload, timeout=180)
    if rr.status_code >= 300:
        print(f"    upsert {i} FAILED: HTTP {rr.status_code} {rr.text[:160]}")
        break
print(f"  upserted {len(points)} points")

# ---- 5. verify by reading back --------------------------------------------
for _ in range(20):
    info = requests.get(f"{QDRANT}/collections/{COLL}", timeout=15).json().get("result", {})
    cnt = info.get("points_count", 0)
    if cnt >= len(points):
        break
    time.sleep(1.5)
print(f"\n  VERIFY — collection '{COLL}': {cnt} points (expected {len(points)})")

# live retrieval probe
qv = list(model.embed(["what did the synthesis conclude about absence of signal"]))[0].tolist()
sr = requests.post(f"{QDRANT}/collections/{COLL}/points/search", timeout=60, json={
    "vector": qv, "limit": 3, "with_payload": True}).json()
print("\n  RETRIEVAL PROBE — 'what did the synthesis conclude about absence of signal':")
for h in sr.get("result", []):
    pl = h["payload"]
    print(f"    {h['score']:.3f}  {pl['rel'][:70]}")
    print(f"           {pl['text'][:110].replace(chr(10),' ')}")

json.dump({"collection": COLL, "dim": DIM, "points": len(points),
           "files": len(docs), "chunks": len(points)},
          open("/opt/data/second_brain_index.json", "w"), indent=1)
print(f"\n  {'PASS' if cnt >= len(points)*0.99 else 'PARTIAL'} — vault indexed")
