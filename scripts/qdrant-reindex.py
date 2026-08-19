#!/usr/bin/env python3
"""NURA Qdrant reindex — vault docs -> local embeddings -> nura-os collection (background)."""
import os, json, sys, time, glob

VAULT = "/opt/data/Obsidian Vault/NURA-OS"
QDRANT_URL = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
COLLECTION = "nura-os"
CHUNK = 900
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
sys.path.insert(0, "/opt/data/lazy-packages")

from fastembed import TextEmbedding

def main():
    # gather docs
    docs = []
    for root, _, files in os.walk(VAULT):
        for f in files:
            if f.endswith(".md"):
                p = os.path.join(root, f)
                try:
                    t = open(p, encoding="utf-8", errors="ignore").read()
                except Exception:
                    continue
                if len(t.strip()) < 40:
                    continue
                rel = os.path.relpath(p, VAULT)
                docs.append((rel, t))
    print(f"docs found: {len(docs)}", flush=True)

    # chunk
    chunks = []
    for rel, t in docs:
        words = t.split()
        for i in range(0, len(words), CHUNK):
            c = " ".join(words[i:i+CHUNK])
            chunks.append({"text": c, "meta": {"source": rel, "chunk": i // CHUNK}})
    print(f"chunks: {len(chunks)}", flush=True)

    # embed
    emb = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    batch = []
    for idx, c in enumerate(chunks):
        batch.append(c)
        if len(batch) >= 32:
            _flush(emb, batch, idx)
            batch = []
    if batch:
        _flush(emb, batch, len(chunks) - 1)
    print("reindex COMPLETE", flush=True)

def _flush(emb, batch, idx):
    import urllib.request, uuid
    vectors = list(emb.embed([c["text"] for c in batch]))
    payload = {"points": [
        {"id": str(uuid.uuid4()), "vector": {"fast-all-minilm-l6-v2": v.tolist()}, "payload": c["meta"]}
        for i, (c, v) in enumerate(zip(batch, vectors))
    ]}
    req = urllib.request.Request(
        f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=false",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"},
        method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read()
        print(f"  upserted {len(batch)} (total so far: {idx+1})", flush=True)
    except Exception as e:
        print(f"  upsert FAIL: {e}", flush=True)

if __name__ == "__main__":
    main()
