import os
#!/usr/bin/env python3
"""DOCSGPT INGESTOR v5 — the FULL pipeline: chunks → embeddings → FAISS-index → the X-Internal-Key upload!"""
import json, os, sys, subprocess, tempfile, uuid, urllib.request, io

os.environ["HF_TOKEN"] = os.environ.get("HF_TOKEN", "")
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
LOCAL_DIR = "/opt/data/nura-corpora-local"
KEY = os.environ.get("DOCSGPT_API_KEY", "")
BASE = "http://72.61.71.211:7091"

def sh(cmd, timeout=300):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()[-200:]
    except Exception as e:
        return f"ERR: {e}"

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "Pathoma_Husain.jsonl"
    local = os.path.join(LOCAL_DIR, target)
    if not os.path.exists(local):
        print(f"pulling {target}...", flush=True)
        print(sh(f"scp -o BatchMode=yes -i ~/.ssh/id_nura_clean root@72.60.163.140:/opt/nura-corpora/textbooks/chunk/{target} {local}"))
    chunks = []
    with open(local, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                d = json.loads(line)
                c = d.get("content") or d.get("text") or ""
                if len(c) > 80:
                    chunks.append(c[:3000])
            except Exception:
                continue
    print(f"{target}: {len(chunks)} chunks", flush=True)
    # the embeddings + the FAISS-index (the langchain-format the app reads!)
    from sentence_transformers import SentenceTransformer
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_core.documents import Document
    print("loading the embedder...", flush=True)
    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2", encode_kwargs={"normalize_embeddings": True})
    docs = [Document(page_content=c, metadata={"source": target}) for c in chunks[:200]]
    print("embedding + indexing (200-chunk sample for the proof)...", flush=True)
    vs = FAISS.from_documents(docs, emb)
    with tempfile.TemporaryDirectory() as td:
        vs.save_local(td)
        faiss_path = os.path.join(td, "index.faiss")
        pkl_path = os.path.join(td, "index.pkl")
        ikey = sh("ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 \"grep '^INTERNAL_KEY=' /docker/docsgpt/.env | cut -d= -f2\"")
        print(f"uploading the index ({os.path.getsize(faiss_path)}B + {os.path.getsize(pkl_path)}B)...", flush=True)
        boundary = "----nura" + uuid.uuid4().hex[:12]
        fields = [("user", "nura"), ("name", target.replace(".jsonl", "")), ("tokens", "200"),
                  ("retriever", "faiss"), ("id", str(uuid.uuid4())), ("type", "docs")]
        parts = []
        for k, v in fields:
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
        for fn, path in (("file_faiss", faiss_path), ("file_pkl", pkl_path)):
            with open(path, "rb") as fh:
                data = fh.read()
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{fn}\"; filename=\"{os.path.basename(path)}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + data + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        req = urllib.request.Request(BASE + "/api/upload_index", data=b"".join(parts), method="POST", headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}", "X-Internal-Key": ikey})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                print(f"UPLOAD: {r.status} | {r.read().decode()[:150]}", flush=True)
        except urllib.error.HTTPError as e:
            print(f"UPLOAD: {e.code} | {e.read().decode()[:150]}", flush=True)
        except Exception as e:
            print(f"UPLOAD-ERR: {str(e)[:120]}", flush=True)
    print("=== INGESTION-RUN COMPLETE ===", flush=True)

if __name__ == "__main__":
    main()
