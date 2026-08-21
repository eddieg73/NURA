#!/usr/bin/env python3
"""THE CONNECTIVITY-SWEEP — the one-shot full-matrix verifier: every lane ↔ its service ↔ its key!
The CTO-standard: the GREEN-board as the standing state; ONLY the real-gaps reported."""
import os, subprocess, json, datetime

ENV = "/opt/data/profiles/nura/.env"
def has(var):
    try:
        with open(ENV) as f:
            return any(l.startswith(var + "=") for l in f)
    except Exception:
        return False

def sh(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return f"ERR {str(e)[:40]}"

def check(name, ok, detail=""):
    mark = "✅" if ok else "❌"
    print(f"{mark} {name} {detail}")
    return ok

print("=" * 46)
print("NURA CONNECTIVITY-SWEEP — " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
print("=" * 46)
gaps = []

# 1. THE BRAIN-LANE
b = sh("curl -s -m 6 -o /dev/null -w '%{http_code}' http://72.61.71.211:7091/api/health")
check("DocsGPT-brain", b == "200", f"({b})") or gaps.append("brain")

# 2. THE OLLAMA-LANE
o = sh("curl -s -m 6 -o /dev/null -w '%{http_code}' http://72.60.163.140:11434/api/tags")
check("Ollama-sovereign", o == "200", f"({o})") or gaps.append("ollama")

# 3. THE MESH-LANE
m = sh("ssh -o BatchMode=yes -o ConnectTimeout=5 -i ~/.ssh/id_nura_clean root@72.60.163.140 'echo ok' 2>&1 | head -1")
check("WireGuard-mesh", "ok" in m) or gaps.append("mesh")

# 4. THE TUNNELS
import socket
for port in (11434, 1080):
    s = socket.socket(); s.settimeout(2)
    try:
        s.connect(("127.0.0.1", port)); check(f"tunnel-{port}", True) or gaps.append(f"tunnel-{port}")
    except Exception:
        check(f"tunnel-{port}", False) or gaps.append(f"tunnel-{port}")
    finally:
        s.close()

# 5. THE MCP-LANES (the enabled-count!)
n = sh("export PATH=/opt/data/profiles/nura/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH; timeout 40 hermes mcp list 2>/dev/null | grep -c '✓ enabled'")
check("MCP-lanes", n.isdigit() and int(n) >= 40, f"({n} enabled)") or gaps.append("mcp-lanes")

# 6. THE KEYS (the critical-presence!)
for k in ["GHL_API_KEY", "HF_TOKEN", "OPENROUTER_API_KEY", "EXA_API_KEY", "NOTION_MCP_TOKEN", "TWILIO_AUTH_TOKEN", "HOSTINGER_API_TOKEN"]:
    check(f"key-{k}", has(k)) or gaps.append(f"key-{k}")

# 7. THE CRONS
c = sh("export PATH=/opt/data/profiles/nura/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH; timeout 40 hermes cron list 2>/dev/null | grep -c active")
check("cron-roster", c.isdigit() and int(c) >= 40, f"({c} active)") or gaps.append("crons")

# 8. THE LIBRECHAT (probe through the SSH — the external-port may be firewalled from here!)
lc = sh("ssh -o BatchMode=yes -o ConnectTimeout=6 -i ~/.ssh/id_nura_clean root@72.60.163.140 \"curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:3080\" 2>&1 | tail -1")
check("LibreChat", lc == "200", f"({lc})") or gaps.append("librechat")

print()
if gaps:
    print(f"⚠️ REAL-GAPS ({len(gaps)}): {', '.join(gaps)}")
    print("→ the founder-drops: the missing-keys only; everything else self-heals!")
else:
    print("✅ ALL-GREEN — the full-stack connected and communicating!")
