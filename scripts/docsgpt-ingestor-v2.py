#!/usr/bin/env python3
"""DOCSGPT INGESTOR v2 — stream the Lab corpus into the DocsGPT sources (chunked, keyed, verified)."""
import json, os, sys, time, urllib.request

BASE = "http://72.61.71.211:7091"
KEY = "REDACTED"
REMOTE = "root@72.60.163.140"
CORPUS_DIR = "/opt/nura-corpora/textbooks/chunk"
LOCAL_DIR = "/opt/data/nura-corpora-local"

def sh(cmd, timeout=120):
    import subprocess
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR: {e}"

def post(path, data, timeout=120):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"error": str(e)[:200]}

def main():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    target = sys.argv[1] if len(sys.argv) > 1 else "Pathoma_Husain.jsonl"
    local = os.path.join(LOCAL_DIR, target)
    if not os.path.exists(local):
        print(f"pulling {target} from the Lab...", flush=True)
        print(sh(f"scp -o BatchMode=yes -i ~/.ssh/id_nura_clean {REMOTE}:{CORPUS_DIR}/{target} {local}"))
    chunks = []
    with open(local, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                d = json.loads(line)
                content = d.get("content") or d.get("text") or ""
                if len(content) > 80:
                    chunks.append(content[:3000])
            except Exception:
                continue
    print(f"{target}: {len(chunks)} chunks loaded", flush=True)
    # the DocsGPT upload-lane probe: what does /api/docs expect?
    r = post("/api/docs", {"api_key": KEY, "source": target, "docs": chunks[:5]})
    print(f"/api/docs -> {r}", flush=True)
    # fallback: the /api/upload_index probe
    if isinstance(r, dict) and r.get("error"):
        r2 = post("/api/upload_index", {"api_key": KEY, "source": target, "docs": chunks[:5]})
        print(f"/api/upload_index -> {r2}", flush=True)

if __name__ == "__main__":
    main()
