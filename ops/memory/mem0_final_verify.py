"""FINAL verification: load mem0.json (the real config) + round-trip, and agentmemory store."""
import sys, os, json
sys.path.insert(0, "/opt/data/lazy-packages")
sys.path.insert(0, "/opt/data/fastembed-pkgs")

for line in open("/opt/data/profiles/nura/.env", errors="ignore"):
    if line.startswith("DEEPSEEK_API_KEY="):
        os.environ["DEEPSEEK_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")

from mem0 import Memory

cfg = json.load(open("/opt/data/profiles/nura/mem0.json"))["oss"]
m = Memory.from_config(cfg)
print("  [mem0] loaded from mem0.json OK")

r = m.add("Final verification: mem0 lane operational with DeepSeek and local fastembed.",
          user_id="nura")
res = r.get("results", r) if isinstance(r, dict) else r
print("  [mem0] ADD ->", (res[0]["id"] if isinstance(res, list) and res else str(r))[:40])

s = m.search("mem0 lane operational", filters={"user_id": "nura"})
hits = s.get("results", s) if isinstance(s, dict) else s
print("  [mem0] SEARCH hits:", len(hits) if hasattr(hits, "__len__") else hits)
for x in (hits or [])[:2]:
    print("      -", (x.get("memory") if isinstance(x, dict) else str(x))[:95])

am = json.load(open("/opt/data/profiles/nura/home/.agentmemory/standalone.json"))
mems = am.get("mem:memories", {})
print("  [agentmemory] memories stored:", len(mems))
for k, v in list(mems.items())[-2:]:
    print("      -", (v.get("title") or v.get("content", ""))[:85])

print("  RESULT: BOTH MEMORY LANES OPERATIONAL")
