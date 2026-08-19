#!/usr/bin/env python3
"""DOCSGPT INGESTOR v3 — the internal-key upload lane (the real source-creation path!)."""
import json, os, sys, time, urllib.request, subprocess

BASE = "http://72.61.71.211:7091"
KEY = "REDACTED"
LOCAL_DIR = "/opt/data/nura-corpora-local"

def sh(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR: {e}"

def post(path, data, key=None, timeout=180):
    headers = {"Content-Type": "application/json"}
    if key: headers["x-api-key"] = key
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": r.status, "body": r.read().decode()[:300]}
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()[:250]}
    except Exception as e:
        return {"error": str(e)[:200]}

def main():
    # fetch the internal key (sealed on the Clinic — the value stays remote!)
    ikey = sh("ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 \"grep '^INTERNAL_KEY=' /docker/docsgpt/.env | cut -d= -f2\"")
    if not ikey or "ERR" in ikey:
        print("internal-key fetch failed", flush=True)
        return
    print(f"internal key: {ikey[:4]}... ({len(ikey)} chars)", flush=True)
    target = sys.argv[1] if len(sys.argv) > 1 else "Pathoma_Husain.jsonl"
    local = os.path.join(LOCAL_DIR, target)
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
    print(f"{target}: {len(chunks)} chunks", flush=True)
    # probe the upload-index with the internal key
    r = post("/api/upload_index", {"api_key": KEY, "source": target, "docs": chunks[:3]}, key=ikey)
    print(f"/api/upload_index -> {r}", flush=True)

if __name__ == "__main__":
    main()
