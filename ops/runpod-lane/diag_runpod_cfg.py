"""Locate the runpod provider block in config.yaml and check env resolution."""
import yaml, os, re, json

CFG = "/opt/data/profiles/nura/config.yaml"
ENV = "/opt/data/profiles/nura/.env"

d = yaml.safe_load(open(CFG, encoding="utf-8"))


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else k
            if k == "runpod":
                print(f"  runpod block at: {p}")
                print(f"    {v}")
            walk(v, p)


print("=== runpod provider location ===")
walk(d)
print("\n  top-level keys:", list(d.keys()))

print("\n=== env resolution ===")
v = os.getenv("RUNPOD_API_KEY")
print("  os.getenv RUNPOD_API_KEY:", "present" if v else "MISSING")
env = open(ENV, encoding="utf-8", errors="replace").read()
print("  .env has RUNPOD_API_KEY:", bool(re.search(r"^RUNPOD_API_KEY=.+$", env, re.M)))

print("\n=== every provider block with a key env or inline key ===")
for section in ("llm", "providers", "model_providers", "models"):
    blk = d.get(section)
    if isinstance(blk, dict):
        for name, cfg in blk.items():
            if isinstance(cfg, dict) and any(
                k in cfg for k in ("api_key", "api_key_env", "key_env", "base_url")
            ):
                keys = {k: ("<set>" if k in ("api_key",) else cfg.get(k))
                        for k in ("api_key", "api_key_env", "key_env", "base_url")
                        if k in cfg}
                print(f"  {section}.{name}: {keys}")
