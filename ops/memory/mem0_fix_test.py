"""mem0 lane test — DeepSeek LLM + local fastembed + Qdrant (no paid embedding credits)."""
import sys, os, time
sys.path.insert(0, "/opt/data/lazy-packages")
sys.path.insert(0, "/opt/data/fastembed-pkgs")

# load DeepSeek key from profile env
for line in open("/opt/data/profiles/nura/.env", errors="ignore"):
    if line.startswith("DEEPSEEK_API_KEY="):
        os.environ["DEEPSEEK_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")

from mem0 import Memory

cfg = {
    "llm": {"provider": "deepseek", "config": {"model": "deepseek-flash"}},
    "embedder": {"provider": "fastembed", "config": {"model": "BAAI/bge-base-en-v1.5"}},
    "vector_store": {"provider": "qdrant", "config": {
        "host": "localhost", "port": 6333,
        "collection_name": "mem0", "embedding_model_dims": 384}},
}
try:
    m = Memory.from_config(cfg)
    print("  init OK (deepseek + fastembed + qdrant)")
    tag = "nura-mem-verify-" + time.strftime("%H%M%S")
    r = m.add(f"Memory lane restored {tag}: mem0 now runs DeepSeek LLM with local fastembed embeddings.",
              user_id="nura")
    print("  ADD result:", str(r)[:200])
    s = m.search("memory lane restored", user_id="nura")
    hits = s.get("results", s) if isinstance(s, dict) else s
    print("  SEARCH hits:", len(hits) if hasattr(hits, "__len__") else hits)
    for x in (hits or [])[:3]:
        print("    -", (x.get("memory") if isinstance(x, dict) else str(x))[:110])
    print("  RESULT: mem0 LANE WORKING")
except Exception as e:
    print("  FAIL:", type(e).__name__, str(e)[:300])
