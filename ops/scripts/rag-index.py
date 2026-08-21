#!/usr/bin/env python3
"""NURA self-knowledge RAG indexer — docs/lessons/notes → Qdrant (nura-docs).
Reversible, idempotent (upsert by content hash), PHI-safe (source allowlist only).
"""
import hashlib, json, os, re, sys, time
from pathlib import Path
sys.path.insert(0, "/opt/data/lazy-packages")  # qdrant-client lives here (plugin lazy install)

QDRANT_URL = os.environ.get("QDRANT_URL", "http://127.0.0.1:6333")
COLLECTION = "nura-docs"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"   # fastembed local ONNX — no API credits
DIM = 384
CHUNK = 1200
SOURCES = [
    "/opt/data/home/nura-clinical-platform/docs",      # manuals, projects, strategy, clinical
    "/opt/data/home/nura-clinical-platform/data/lessons",  # failure ledger
]

from fastembed import TextEmbedding
embedder = TextEmbedding(model_name=EMBED_MODEL)  # local, free, offline after first fetch
from qdrant_client import QdrantClient
qc = QdrantClient(url=QDRANT_URL)

def chunks(text: str, size: int = CHUNK):
    words = text.split()
    for i in range(0, len(words), size // 8):
        yield " ".join(words[i:i + size // 8])

def index():
    if not qc.collection_exists(COLLECTION):
        qc.create_collection(collection_name=COLLECTION,
                             vectors_config={"size": DIM, "distance": "Cosine"})
    docs, skipped = [], 0
    for root in SOURCES:
        if not Path(root).exists():
            continue
        for p in sorted(Path(root).rglob("*.md")):
            txt = p.read_text(errors="replace")
            if re.search(r"\b(patient|MRN|SSN|DOB)\b", txt, re.I) and "PHI" in str(p):
                skipped += 1
                continue
            for c in chunks(txt):
                c = c.strip()
                if len(c) < 80:
                    continue
                pid = hashlib.md5(f"{p}:{c}".encode()).hexdigest()
                docs.append({"id": pid, "text": c, "file": str(p)})
    if not docs:
        print("NO DOCS TO INDEX")
        return
    batch = 64
    for i in range(0, len(docs), batch):
        part = docs[i:i + batch]
        vecs = list(embedder.embed([d["text"] for d in part]))  # local embeddings
        pts = [{"id": d["id"], "vector": vecs[j].tolist(),
                "payload": {"text": d["text"][:2000], "file": d["file"]}}
               for j, d in enumerate(part)]
        qc.upsert(collection_name=COLLECTION, points=pts)
        time.sleep(0.2)
    print(f"INDEXED {len(docs)} chunks into {COLLECTION} (skipped {skipped})")

if __name__ == "__main__":
    index()
