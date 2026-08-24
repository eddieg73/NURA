import os
#!/usr/bin/env python3
"""DOCSGPT INGESTOR v4 — the X-Internal-Key auth probe + the form-field upload test."""
import json, os, sys, urllib.request, subprocess, uuid

BASE = "http://72.61.71.211:7091"
KEY = os.environ.get("DOCSGPT_API_KEY", "")
def sh(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR: {e}"

def main():
    ikey = sh("ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 \"grep '^INTERNAL_KEY=' /docker/docsgpt/.env | cut -d= -f2\"")
    print(f"internal key: {ikey[:4]}... ({len(ikey)})", flush=True)
    # the multipart probe with the correct header + the minimal fields
    boundary = "----nura" + uuid.uuid4().hex[:12]
    fields = [
        ("user", "nura"), ("name", "pathoma-probe"), ("tokens", "0"),
        ("retriever", "faiss"), ("id", str(uuid.uuid4())), ("type", "docs"),
    ]
    parts = []
    for k, v in fields:
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    # a tiny fake index file (the auth-test only)
    fake = b"x" * 64
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file_faiss\"; filename=\"index.faiss\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + fake + b"\r\n")
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file_pkl\"; filename=\"index.pkl\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + fake + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(BASE + "/api/upload_index", data=body, method="POST", headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "X-Internal-Key": ikey,
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            print(f"AUTH-PASS: {r.status} | {r.read().decode()[:200]}")
    except urllib.error.HTTPError as e:
        print(f"AUTH: {e.code} | {e.read().decode()[:200]}")
    except Exception as e:
        print(f"ERR: {str(e)[:150]}")

if __name__ == "__main__":
    main()
