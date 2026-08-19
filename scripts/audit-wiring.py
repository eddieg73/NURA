import json, os, re, urllib.request, urllib.error
from pathlib import Path

env = Path("/opt/data/profiles/nura/.env").read_text() if Path("/opt/data/profiles/nura/.env").exists() else ""
envnames = set(re.findall(r"^([A-Z0-9_]+)=", env, re.M))

# 1. MCP lanes registered in config
cfg = Path("/opt/data/profiles/nura/config.yaml").read_text()
idx = cfg.find("mcp_servers:")
block = cfg[idx:idx + 9000]
servers = re.findall(r"^  ([a-zA-Z0-9_]+):", block, re.M)
print("== MCP registered:", len(servers))

# 2. Key scripts exist
scripts = ["telemetry-cds-engine.py", "medical-imaging-vision.py", "uspto-ai-watch.py",
           "provider-labs-ingest.py", "dataset-provisioner.py", "mission-control-gen.py",
           "agent-cost-tracker.py", "travel-risk-engine.py"]
print("\n== scripts:")
for s in scripts:
    p = Path("/opt/data/profiles/nura/scripts") / s
    print(f"  {s}: {'OK' if p.exists() else 'MISSING'}")

# 3. Credential env names (names only, values never printed)
needed = {"DOCUMO_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GHL_API_KEY",
          "N8N_API_KEY", "ELEVENLABS_API_KEY", "HF_TOKEN", "GOOGLE_API_KEY",
          "TWILIO_ACCOUNT_SID", "MOLTBOOK_API_KEY", "NOTION_API_TOKEN", "API_SERVER_KEY"}
print("\n== env key presence (names only):")
for n in sorted(needed):
    print(f"  {n}: {'set' if n in envnames else 'absent'}")

# 4. Board NUR-112 + agent counts
def envval(name):
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""
key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Audit/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
try:
    req = urllib.request.Request(base + "/api/companies?limit=1", headers=hdr)
    with urllib.request.urlopen(req, timeout=10) as r:
        print("\n== paperclip API: HTTP", r.status)
except Exception as e:
    print("\n== paperclip API ERR:", str(e)[:100])
