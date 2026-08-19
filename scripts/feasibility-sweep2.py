import json, re, socket, urllib.request, urllib.error
from pathlib import Path

def envval(name):
    env = Path("/opt/data/profiles/nura/.env").read_text()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

def http(url, hdr=None, timeout=15):
    h = {"User-Agent": "NURA-Verify2/1.0"}
    if hdr: h.update(hdr)
    try:
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:150]
    except Exception as e:
        return 0, str(e)[:120]

# env var names actually present (names only)
env = Path("/opt/data/profiles/nura/.env").read_text()
names = sorted(set(re.findall(r"^([A-Z0-9_]+)=", env, re.M)))
print("env names:", [n for n in names if "ELEVEN" in n or "XI_" in n or "MOLT" in n or "REDIS" in n or "GATEWAY" in n or "API_" in n])

# ElevenLabs: try both key names
for k in ("ELEVENLABS_API_KEY", "XI_API_KEY"):
    v = envval(k)
    if v:
        s, b = http("https://api.elevenlabs.io/v1/voices", {"xi-api-key": v})
        print(f"elevenlabs via {k}: HTTP {s}")
        if s == 200: break

# Moltbook: try profile paths
mkey = envval("MOLTBOOK_API_KEY")
for path in ("/api/v1/agents/nura_hermes", "/api/v1/agents/me", "/api/v1/agent/nura_hermes"):
    s, b = http("https://www.moltbook.com" + path, {"Authorization": "Bearer " + mkey})
    print(f"moltbook {path}: HTTP {s} {b[:60]}")
    if s == 200: break

# Redis: raw TCP PING
try:
    sock = socket.create_connection(("127.0.0.1", 6379), timeout=5)
    sock.sendall(b"PING\r\n")
    out = sock.recv(64)
    print("redis TCP PING:", out.strip())
    sock.close()
except Exception as e:
    print("redis TCP:", str(e)[:80])

# Gateway :8642 paths
for path in ("/v1", "/v1/health", "/health", "/v1/models"):
    s, b = http("http://127.0.0.1:8642" + path, {"x-api-key": envval("API_SERVER_KEY")})
    print(f"gateway {path}: HTTP {s} {b[:60]}")
    if s == 200: break

# Patent watch json from earlier run
p = Path("/opt/data/profiles/nura/data/patent-watch.json")
if p.exists():
    d = json.loads(p.read_text())
    print("patent-watch.json:", d.get("count"), "patents @", d.get("updated"))
else:
    print("patent-watch.json: MISSING")
