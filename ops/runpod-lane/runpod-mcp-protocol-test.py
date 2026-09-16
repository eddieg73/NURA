#!/usr/bin/env python3
"""
RunPod MCP protocol test — no gateway restart needed.

Per the mcp-lane-wiring skill: pipe JSON-RPC (initialize -> tools/list -> ping) and assert
each response. Config-only changes are effective next session; this proves the server
launches and speaks the protocol today.

Note: the MCP server launches fine even with an invalid API key (it only fails at call
time), so a green protocol test does NOT mean the lane is usable. That is exactly the trap
that hid this outage — which is why runpod-lane.py probes the API surface separately.
"""
import json
import subprocess
import sys

WRAPPER = "/opt/data/scripts/runpod-mcp-wrapper.sh"

FRAMES = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "nura-lane-test", "version": "1.0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    {"jsonrpc": "2.0", "id": 3, "method": "ping", "params": {}},
]

payload = "".join(json.dumps(f) + "\n" for f in FRAMES)

try:
    p = subprocess.run(["bash", WRAPPER], input=payload, capture_output=True,
                       text=True, timeout=180)
except subprocess.TimeoutExpired:
    print("  TIMEOUT — server did not complete the handshake in 180s")
    sys.exit(1)

out = p.stdout.strip()
print(f"  wrapper exit: {p.returncode}")
print(f"  stdout bytes: {len(out)}")

if not out:
    print("  EMPTY STDOUT — the server did not respond")
    print(f"  stderr: {p.stderr.strip()[:600]}")
    sys.exit(1)

results = {}
for line in out.split("\n"):
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        continue
    if msg.get("id") == 1:
        si = (msg.get("result") or {}).get("serverInfo") or {}
        results["initialize"] = f"{si.get('name','?')} {si.get('version','')}".strip()
    elif msg.get("id") == 2:
        tools = (msg.get("result") or {}).get("tools") or []
        results["tools"] = len(tools)
        results["tool_names"] = [t.get("name") for t in tools[:8]]
    elif msg.get("id") == 3:
        results["ping"] = "ok" if "result" in msg else msg.get("error")

ok = "initialize" in results and "tools" in results
print("\n  --- protocol results ---")
for k, v in results.items():
    print(f"    {k}: {v}")

print(f"\n  PROTOCOL: {'PASS' if ok else 'FAIL'}")
if ok:
    print("  NOTE: protocol green != lane usable. Invalid key only surfaces at call time.")
    print("        Run: python3 /opt/data/scripts/runpod-lane.py status")
sys.exit(0 if ok else 1)
