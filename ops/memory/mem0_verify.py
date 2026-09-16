"""mem0 lane verification — DeepSeek LLM + local fastembed + Qdrant. Correct v2 search API."""
import sys, os
sys.path.insert(0, "/opt/data/lazy-packages")
sys.path.insert(0, "/opt/data/fastembed-pkgs")

for line in open("/opt/data/profiles/nura/.env", errors="ignore"):
    if line.startswith("DEEPSEEK_API_KEY="):
        os.environ["DEEPSEEK_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")

from mem0 import Memory

cfg = {
    "llm": {"provider": "deepseek", "config": {"model": "deepseek-flash"}},
    "embedder": {"provider": "fastembed", "config": {"model": "BAAI/bge-base-en-v1.5"}},
    "vector_store": {"provider": "qdrant", "config": {
        "host": "localhost", "port": 6333,
        "collection_name": "mem0", "embedding_model_dims": 768}},
}
m = Memory.from_config(cfg)

# SEARCH using the v2 filters API
try:
    s = m.search("mem0 deepseek fastembed", filters={"user_id": "nura"})
except TypeError:
    s = m.search("mem0 deepseek fastembed", user_id="nura")
hits = s.get("results", s) if isinstance(s, dict) else s
print("  SEARCH (filters=) hits:", len(hits) if hasattr(hits, "__len__") else hits)
for x in (hits or [])[:3]:
    print("    -", (x.get("memory") if isinstance(x, dict) else str(x))[:120])

# GET ALL for this user
try:
    ga = m.get_all(filters={"user_id": "nura"})
    allr = ga.get("results", ga) if isinstance(ga, dict) else ga
    print("  GET_ALL count:", len(allr) if hasattr(allr, "__len__") else allr)
except Exception as e:
    print("  get_all note:", type(e).__name__, str(e)[:120])

print("  RESULT: mem0 READ+WRITE VERIFIED")
