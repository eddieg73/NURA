"""Empirically determine how the runpod provider base_url is resolved at runtime."""
import os, sys, json, subprocess

sys.path.insert(0, "/opt/hermes")

findings = {}

# 1. Is there a generic <PROVIDER>_BASE_URL override in the LLM runtime?
p = subprocess.run(
    ["grep", "-rn", "RUNPOD_BASE_URL", "/opt/hermes/"],
    capture_output=True, text=True)
findings["RUNPOD_BASE_URL_mentions"] = p.stdout.strip().split("\n")[:5] if p.stdout.strip() else []

# 2. Generic provider base_url env pattern in the agent runtime
p2 = subprocess.run(
    ["grep", "-rn", "-E", r'f"\{[a-z_.]*name[a-z_.]*\.upper\(\)\}_BASE_URL"', "/opt/hermes/agent/", "/opt/hermes/hermes_cli/"],
    capture_output=True, text=True)
findings["generic_provider_base_url_env"] = p2.stdout.strip().split("\n")[:8] if p2.stdout.strip() else []

# 3. Where does the runtime read providers.<name>.base_url?
p3 = subprocess.run(
    ["grep", "-rn", "--include=*.py", "-E", r'providers.*\.get\(.*base_url|provider_cfg.*base_url|_provider_entry.*base_url',
     "/opt/hermes/agent/"],
    capture_output=True, text=True)
findings["provider_base_url_reads"] = p3.stdout.strip().split("\n")[:8] if p3.stdout.strip() else []

for k, v in findings.items():
    print(f"=== {k} ===")
    for line in v or ["  (none)"]:
        print("  " + line[:180])
    print()
