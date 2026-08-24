import os
#!/usr/bin/env python3
"""DOCSGPT CORPUS INGESTOR — chunk the textbook JSONLs -> DocsGPT sources via the API."""
import json, os, sys, time, urllib.request

BASE = "http://72.61.71.211:7091"
KEY = os.environ.get("DOCSGPT_API_KEY", "")
CORPUS = "/opt/nura-corpora/textbooks/chunk"
BATCH = 50

def post(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)[:200]}

def main():
    files = sorted(f for f in os.listdir(CORPUS) if f.endswith(".jsonl"))
    print(f"corpus files: {len(files)}", flush=True)
    total = 0
    for fname in files:
        path = os.path.join(CORPUS, fname)
        chunks = []
        with open(path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    d = json.loads(line)
                    content = d.get("content") or d.get("text") or ""
                    if len(content) > 50:
                        chunks.append(content[:2000])
                except Exception:
                    continue
        print(f"{fname}: {len(chunks)} chunks", flush=True)
        # find the docs upload endpoint
        r = post("/api/docs", {"api_key": KEY, "source": fname, "docs": chunks[:BATCH]})
        print(f"  api/docs -> {r if isinstance(r, dict) else r}", flush=True)
        total += len(chunks)
        break  # one file as the proof-of-pipeline
    print(f"TOTAL chunks seen: {total} — pipeline proven, batch-mode next", flush=True)

if __name__ == "__main__":
    main()
