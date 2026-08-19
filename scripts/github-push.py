#!/usr/bin/env python3
"""Push hermes-driver to @Nuratech-ai/hermes-driver (internal)."""
import json
import os
import re
import subprocess
import urllib.request

env = open("/opt/data/profiles/nura/.env").read()
TOKEN = re.search(r"^GITHUB_PERSONAL_ACCESS_TOKEN=(.+)$", env, re.M).group(1).strip().strip('"').strip("'")
H = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json", "User-Agent": "NURA-Hermes/1.0"}

def api(method, path):
    req = urllib.request.Request("https://api.github.com" + path, headers=H, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()[:400] or "{}")

s, d = api("GET", "/repos/Nuratech-ai/hermes-driver")
print("repo access:", s, d.get("full_name", d.get("message", "?")))
if s != 200:
    print("TOKEN NEEDS the repo added (edit token -> repository access -> add hermes-driver)")
    raise SystemExit(1)

repo_dir = "/opt/data/projects/hermes-driver"
subprocess.run(["git", "-C", repo_dir, "init", "-b", "main"], capture_output=True)
subprocess.run(["git", "-C", repo_dir, "add", "-A"], capture_output=True)
subprocess.run(["git", "-C", repo_dir, "-c", "user.name=Hermes (NURA)", "-c", "user.email=hermes@nuratech.ai",
                "commit", "-m", "hermes-driver v0.1 — MIT vehicle control bridge (sim-first, safety manifest)"],
               capture_output=True)
url = f"https://github.com/Nuratech-ai/hermes-driver.git"
r = subprocess.run(["git", "-C", repo_dir, "-c", f"http.extraheader=Authorization: Bearer {TOKEN}",
                    "push", "-u", url, "main"], capture_output=True, text=True, timeout=180)
print("push:", "PUSHED ✅" if r.returncode == 0 else f"rc={r.returncode}: {r.stderr[-250:]}")
