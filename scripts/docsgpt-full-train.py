#!/usr/bin/env python3
"""DOCSGPT FULL-CORPUS TRAINING — every textbook, the proven pipeline, batched.
The 202MB corpus → per-book chunks → embeddings → FAISS index → X-Internal-Key upload."""
import json, os, sys, subprocess, tempfile, uuid, urllib.request

os.environ["HF_TOKEN"] = "hf_REDACTED"
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
LOCAL_DIR = "/opt/data/nura-corpora-local"
BASE = "http://72.61.71.211:7091"
KEY = "REDACTED"
REMOTE = "root@72.60.163.140"
CORPUS = "/opt/nura-corpora/textbooks/chunk"

def sh(cmd, timeout=600):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR: {e}"

def load_chunks(path, cap=400):
    chunks = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                d = json.loads(line)
                c = d.get("content") or d.get("text") or ""
                if len(c) > 80:
                    chunks.append(c[:3000])
            except Exception:
                continue
            if len(chunks) >= cap:
                break
    return chunks

def main():
    # the corpus inventory (remote!)
    files = sh(f"ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean {REMOTE} 'ls {CORPUS}/*.jsonl | xargs -n1 basename'").split()
    print(f"corpus: {len(files)} textbooks", flush=True)
    os.makedirs(LOCAL_DIR, exist_ok=True)
    from sentence_transformers import SentenceTransformer
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_core.documents import Document
    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2", encode_kwargs={"normalize_embeddings": True})
    done = 0
    for fname in sorted(files):
        local = os.path.join(LOCAL_DIR, fname)
        if not os.path.exists(local):
            print(f"pulling {fname}...", flush=True)
            sh(f"scp -o BatchMode=yes -i ~/.ssh/id_nura_clean {REMOTE}:{CORPUS}/{fname} {local}", timeout=900)
        chunks = load_chunks(local)
        if len(chunks) < 10:
            print(f"{fname}: skipped ({len(chunks)} chunks)", flush=True)
            continue
        print(f"{fname}: {len(chunks)} chunks → embedding...", flush=True)
        docs = [Document(page_content=c, metadata={"source": fname}) for c in chunks]
        vs = FAISS.from_documents(docs, emb)
        with tempfile.TemporaryDirectory() as td:
            vs.save_local(td)
            ikey = sh("ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 \"grep '^INTERNAL_KEY=' /docker/docsgpt/.env | cut -d= -f2\"")
            boundary = "----nura" + uuid.uuid4().hex[:12]
            fields = [("user", "nura"), ("name", fname.replace(".jsonl", "")), ("tokens", str(len(chunks))),
                      ("retriever", "faiss"), ("id", str(uuid.uuid4())), ("type", "docs")]
            parts = []
            for k, v in fields:
                parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
            for fn in ("file_faiss", "file_pkl"):
                path = os.path.join(td, "index.faiss" if fn == "file_faiss" else "index.pkl")
                with open(path, "rb") as fh:
                    data = fh.read()
                parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{fn}\"; filename=\"{fn}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + data + b"\r\n")
            parts.append(f"--{boundary}--\r\n".encode())
            req = urllib.request.Request(BASE + "/api/upload_index", data=b"".join(parts), method="POST", headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}", "X-Internal-Key": ikey})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    status = r.read().decode()[:80]
                    print(f"{fname}: UPLOAD {r.status} {status}", flush=True)
                    if r.status == 200:
                        done += 1
            except urllib.error.HTTPError as e:
                print(f"{fname}: UPLOAD-ERR {e.code} {e.read().decode()[:80]}", flush=True)
            except Exception as e:
                print(f"{fname}: UPLOAD-ERR {str(e)[:80]}", flush=True)
    print(f"=== FULL-CORPUS TRAINING COMPLETE: {done}/{len(files)} textbooks indexed ===", flush=True)

if __name__ == "__main__":
    main()
