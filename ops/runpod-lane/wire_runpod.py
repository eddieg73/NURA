"""
Wire the RunPod lane correctly.

Findings this acts on:
  * providers.runpod.base_url was 'https://api.runpod.ai/v2' — the serverless JOB-queue host.
    That path has no OpenAI-compatible surface, so the provider slot could never work.
    Correct shape: https://api.runpod.ai/v2/<ENDPOINT_ID>/openai/v1
  * Nothing references providers.runpod (checked: model, model_aliases, fallback_providers,
    auxiliary, moa, vision, delegation) — so fixing it cannot break the running stack.
  * The MCP server now defaults to REST v2; pin it explicitly instead of relying on a default.
"""
import re
import shutil
import time

CFG = "/opt/data/profiles/nura/config.yaml"
WRAPPER = "/opt/data/scripts/runpod-mcp-wrapper.sh"

CORRECT_BASE = "https://api.runpod.ai/v2/ENDPOINT_ID_NOT_SET/openai/v1"

stamp = time.strftime("%Y%m%d_%H%M%S")
shutil.copy(CFG, f"{CFG}.bak.{stamp}")
print(f"  backup: {CFG}.bak.{stamp}")

# ---- 1. correct the provider base_url -------------------------------------
s = open(CFG, encoding="utf-8").read()
old = re.search(
    r"^  runpod:\n    api_key_env: RUNPOD_API_KEY\n    base_url: \S+\n",
    s, re.M)
if not old:
    print("  !! runpod provider block not found"); raise SystemExit(1)

new = (
    "  runpod:\n"
    "    api_key_env: RUNPOD_API_KEY\n"
    f"    base_url: {CORRECT_BASE}\n"
)
s2 = s.replace(old.group(0), new, 1)
open(CFG, "w", encoding="utf-8").write(s2)
print("  providers.runpod.base_url corrected to the OpenAI-compatible shape")
print(f"    was: https://api.runpod.ai/v2   (serverless job queue - no /chat/completions)")
print(f"    now: {CORRECT_BASE}")
print("    NOTE: ENDPOINT_ID_NOT_SET is deliberate - it cannot work without a deployed")
print("          serverless endpoint, and the placeholder makes that obvious rather than silent.")

# ---- 2. pin the MCP to REST v2 explicitly ---------------------------------
w = open(WRAPPER, encoding="utf-8").read()
if "RUNPOD_REST_VERSION" not in w:
    w = w.replace(
        'export RUNPOD_API_KEY="$KEY"',
        'export RUNPOD_API_KEY="$KEY"\n'
        '# Pin the REST generation. The MCP server defaults to v2; pinning means a future\n'
        '# upstream default change cannot silently move this lane between API generations.\n'
        'export RUNPOD_REST_VERSION="${RUNPOD_REST_VERSION:-v2}"'
    )
    open(WRAPPER, "w", encoding="utf-8").write(w)
    print("  wrapper: RUNPOD_REST_VERSION pinned to v2 (explicit, not inherited default)")
else:
    print("  wrapper: RUNPOD_REST_VERSION already present")

# ---- 3. verify ------------------------------------------------------------
import yaml
d = yaml.safe_load(open(CFG, encoding="utf-8"))
print("\n  YAML parses:", "OK" if d else "FAILED")
print("  providers.runpod =", d["providers"]["runpod"])
print("  mcp_servers.runpod =", d["mcp_servers"]["runpod"])
print("\n  wrapper now reads:")
for i, line in enumerate(open(WRAPPER, encoding="utf-8").read().split("\n")[:14], 1):
    if "RUNPOD" in line or "exec" in line:
        print(f"    {i}: {line[:96]}")
