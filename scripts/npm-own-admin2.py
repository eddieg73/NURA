#!/usr/bin/env python3
import sys
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
import bcrypt
import json
import os
import re
import secrets
import subprocess
import urllib.request

CLINIC = "72.61.71.211"
KEY = os.path.expanduser("~/.ssh/id_nura_clean")
ENV = "/opt/data/profiles/nura/.env"

def ssh(cmd, input_data=None):
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-i", KEY, f"root@{CLINIC}", cmd],
                       capture_output=True, text=True, timeout=120, input=input_data)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def envval(name):
    try:
        env = open(ENV).read()
        m = re.search(rf"^{name}=(.+)$", env, re.M)
        return m.group(1).strip().strip('"').strip("'") if m else ""
    except Exception:
        return ""

def setenv(name, value):
    env = open(ENV).read()
    env = re.sub(rf"^{name}=.*$", f"{name}={value}", env, flags=re.M) if re.search(rf"^{name}=", env, re.M) else env + f"\n{name}={value}\n"
    open(ENV, "w").write(env)
    os.chmod(ENV, 0o600)

# 1. Inspect auth table + get DB password (visible errors)
out, err, rc = ssh("docker inspect nginx-proxy-manager-db-1 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep MYSQL_PASSWORD | cut -d= -f2")
dbpass = out.strip()
print("dbpass len:", len(dbpass))
out, err, rc = ssh("docker exec nginx-proxy-manager-db-1 mysql -unpm -p'" + dbpass + "' npm -e 'SHOW COLUMNS FROM auth;' 2>&1 | head -12")
print("AUTH TABLE:", out[:400] if out else err[:200])

# 2. Write SQL via stdin (no shell quoting)
EMAIL = "hermes@nuratech.ai"
PASS = "NPM-" + secrets.token_urlsafe(18)
HASH = bcrypt.hashpw(PASS.encode(), bcrypt.gensalt(rounds=12)).decode()
sql = f"UPDATE auth SET email='{EMAIL}', password='{HASH}' WHERE id=1;\n"
out, err, rc = ssh(f"docker exec -i nginx-proxy-manager-db-1 mysql -unpm -p'{dbpass}' npm", input_data=sql)
print("UPDATE rc:", rc, (out + err)[:300])

# 3. Verify via API login (print error body)
try:
    req = urllib.request.Request(f"http://{CLINIC}:8181/api/tokens",
                                 data=json.dumps({"identity": EMAIL, "secret": PASS}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        token = json.loads(r.read()).get("token")
        print("NPM ADMIN OWNED + VERIFIED")
except urllib.error.HTTPError as e:
    print("LOGIN FAIL:", e.code, e.read().decode()[:300])
    raise SystemExit(1)

setenv("NPM_ADMIN_EMAIL", EMAIL)
setenv("NPM_ADMIN_PASS", PASS)
print("Sealed in .env (0600)")
