"""Is providers.runpod referenced by any active model / alias / fallback?"""
import yaml

CFG = "/opt/data/profiles/nura/config.yaml"
d = yaml.safe_load(open(CFG, encoding="utf-8"))

print("=== model selection ===")
print("  model:", d.get("model"))
print("  fallback_providers:", d.get("fallback_providers"))

print("\n=== model_aliases referencing runpod ===")
al = d.get("model_aliases") or {}
hits = {k: v for k, v in al.items() if "runpod" in str(v).lower()}
print("  ", hits if hits else "(none)")

print("\n=== any key anywhere referencing runpod (excluding providers/mcp_servers) ===")
def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else k
            if p.startswith(("providers.runpod", "mcp_servers.runpod")):
                walk(v, p); continue
            if "runpod" in str(k).lower() or "runpod" in str(v).lower()[:200]:
                print(f"  {p} = {str(v)[:140]}")
            walk(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if "runpod" in str(v).lower()[:200]:
                print(f"  {path}[{i}] = {str(v)[:140]}")
            walk(v, f"{path}[{i}]")
walk(d)

print("\n=== auxiliary / moa / vision referencing runpod ===")
for sec in ("auxiliary", "moa", "vision", "delegation", "agent"):
    blk = d.get(sec)
    if blk is not None and "runpod" in str(blk).lower():
        print(f"  {sec}: {str(blk)[:220]}")
    else:
        print(f"  {sec}: (no runpod reference)")
