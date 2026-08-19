#!/usr/bin/env python3
"""NURA feasibility sweep — live probes across every lane. Evidence only."""
import json, re, socket, subprocess, time, urllib.request, urllib.error
from pathlib import Path

def envval(name):
    env = Path("/opt/data/profiles/nura/.env").read_text()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

def http(url, token=None, hdr_extra=None, timeout=15):
    h = {"User-Agent": "NURA-Verify/1.0"}
    if token:
        h["Authorization"] = "Bearer " + token
        h["x-api-key"] = token
    if hdr_extra:
        h.update(hdr_extra)
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()[:400]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:200]
    except Exception as e:
        return 0, str(e)[:120]

results = []

def rec(name, ok, detail=""):
    results.append((name, "OK" if ok else "FAIL", detail))

# 1. n8n
s, b = http("https://n8n.nuratech.ai/healthz")
rec("n8n healthz", s == 200, f"HTTP {s}")
# 2. Paperclip
s, b = http("http://127.0.0.1:3101/api/health", envval("API_SERVER_KEY"))
rec("paperclip :3101", s == 200, f"HTTP {s}")
# 3. Moltbook
s, b = http("https://www.moltbook.com/api/v1/agents/nura_hermes", envval("MOLTBOOK_API_KEY"))
rec("moltbook api", s == 200, f"HTTP {s}")
# 4. ElevenLabs
s, b = http("https://api.elevenlabs.io/v1/voices", envval("ELEVENLABS_API_KEY"),
            {"xi-api-key": envval("ELEVENLABS_API_KEY")})
rec("elevenlabs voices", s == 200, f"HTTP {s}")
# 5. Gemini MCP lane (in-house)
s, b = http("https://generativelanguage.googleapis.com/v1beta/models?key=" + envval("GOOGLE_API_KEY"))
rec("gemini models", s == 200, f"HTTP {s}")
# 6. Qdrant
s, b = http("http://127.0.0.1:6333/collections/nura-docs")
try:
    d = json.loads(b); n = d.get("result", {}).get("points_count", "?")
except Exception:
    n = "?"
rec("qdrant nura-docs", s == 200, f"HTTP {s} points={n}")
# 7. Redis
try:
    out = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True, timeout=10)
    rec("redis ping", "PONG" in out.stdout, out.stdout.strip()[:20])
except Exception as e:
    rec("redis ping", False, str(e)[:60])
# 8. IDC sample on disk
p = Path("/opt/data/datasets/idc-sample.dcm")
rec("IDC sample dcm", p.exists() and p.stat().st_size > 100000, f"{p.stat().st_size if p.exists() else 0} bytes")
# 9. Telemetry engine run
try:
    out = subprocess.run(["python3", "/opt/data/profiles/nura/scripts/telemetry-cds-engine.py"],
                         capture_output=True, text=True, timeout=30)
    d = json.loads(out.stdout); rec("telemetry NEWS2 engine", d.get("news2") == 13, f"NEWS2 {d.get('news2')} provider_gate={d.get('provider_gate')}")
except Exception as e:
    rec("telemetry NEWS2 engine", False, str(e)[:80])
# 10. Mission control regen
try:
    out = subprocess.run(["python3", "/opt/data/profiles/nura/scripts/mission-control-gen.py"],
                         capture_output=True, text=True, timeout=60)
    idx = Path("/opt/data/profiles/nura/mission-control/index.html")
    ok = idx.exists() and "EDT" in idx.read_text()
    rec("mission-control regen", ok, f"html {'updated' if ok else 'stale'}")
except Exception as e:
    rec("mission-control regen", False, str(e)[:80])
# 11. Patent watch (trimmed quick run)
try:
    out = subprocess.run(["python3", "/opt/data/profiles/nura/scripts/uspto-ai-watch.py"],
                         capture_output=True, text=True, timeout=120)
    n = re.search(r"patents found: (\d+)", out.stdout)
    rec("uspto patent watch", bool(n), f"{n.group(1) if n else 0} patents")
except Exception as e:
    rec("uspto patent watch", False, str(e)[:80])
# 12. Provider-labs lane
s, b = http("http://127.0.0.1:8642/v1", envval("API_SERVER_KEY"))
rec("hermes gateway :8642", s == 200, f"HTTP {s}")

print(f"{'LANE':28} {'STATUS':5} DETAIL")
print("-" * 80)
for name, status, detail in results:
    print(f"{name:28} {status:5} {detail}")
ok = sum(1 for _, s, _ in results if s == "OK")
print("-" * 80)
print(f"TOTAL: {ok}/{len(results)} lanes verified")
