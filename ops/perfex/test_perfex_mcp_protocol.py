#!/usr/bin/env python3
"""Live MCP protocol test — drive perfex-mcp-server.py exactly as a real MCP client does."""
import json
import subprocess

SERVER = ["/opt/hermes/.venv/bin/python3", "/opt/data/scripts/perfex-mcp-server.py"]

REQS = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "hermes-cto-test", "version": "1.0"}}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
     "params": {"name": "perfex_status", "arguments": {}}},
    {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
     "params": {"name": "perfex_summary", "arguments": {}}},
    {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
     "params": {"name": "perfex_clients", "arguments": {"limit": 5}}},
    # NEGATIVE TESTS — these MUST be refused
    {"jsonrpc": "2.0", "id": 6, "method": "tools/call",
     "params": {"name": "perfex_query",
                "arguments": {"sql": "SELECT * FROM tblvault LIMIT 5"}}},
    {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
     "params": {"name": "perfex_query",
                "arguments": {"sql": "DELETE FROM tblclients WHERE userid=1"}}},
    {"jsonrpc": "2.0", "id": 8, "method": "tools/call",
     "params": {"name": "perfex_query",
                "arguments": {"sql": "SELECT * FROM tblform_results LIMIT 5"}}},
]

payload = "".join(json.dumps(r) + "\n" for r in REQS)
print(f"  sending {len(REQS)} JSON-RPC messages...\n")

p = subprocess.run(SERVER, input=payload, capture_output=True, text=True, timeout=280)

if p.stderr.strip():
    print("  STDERR:", p.stderr.strip()[:500], "\n")

counts = {"ok": 0, "err": 0, "noreply": 0}
for line in p.stdout.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        resp = json.loads(line)
    except Exception:
        print("  [unparseable]", line[:120])
        continue
    rid = resp.get("id")
    if "error" in resp:
        print(f"  [id={rid}] JSONRPC ERROR: {resp['error']}")
        counts["err"] += 1
        continue
    res = resp.get("result", {})
    if rid == 1:
        si = res.get("serverInfo", {})
        print(f"  [id=1] initialize OK -> {si.get('name')} v{si.get('version')} "
              f"proto={res.get('protocolVersion')}")
        counts["ok"] += 1
    elif rid == 2:
        tools = res.get("tools", [])
        print(f"  [id=2] tools/list OK -> {len(tools)} tools")
        for t in tools:
            print(f"           · {t['name']}")
        counts["ok"] += 1
    else:
        text = ""
        for c in res.get("content", []):
            if c.get("type") == "text":
                text = c.get("text", "")
        is_err = res.get("isError", False)
        label = "REFUSED" if is_err else "OK"
        counts["ok" if not is_err else "err"] += 1
        first = text.splitlines()[0][:110] if text else "(empty)"
        print(f"  [id={rid}] {label}: {first}")
        if rid in (4, 5, 6, 7, 8):
            for extra in text.splitlines()[1:6]:
                print(f"           {extra[:110]}")

print(f"\n  replies: ok={counts['ok']} refused/err={counts['err']}")

# Hard assertions
def find(rid):
    for line in p.stdout.splitlines():
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("id") == rid:
            return r.get("result", {})
    return {}

ok = True
if find(1).get("serverInfo", {}).get("name") != "perfex":
    print("  FAIL: initialize did not return serverInfo"); ok = False
if len(find(2).get("tools", [])) != 6:
    print("  FAIL: expected 6 tools"); ok = False
for rid in (6, 7, 8):
    if not find(rid).get("isError"):
        print(f"  FAIL: request {rid} was NOT refused — SECURITY HOLE"); ok = False
if not find(3).get("content"):
    print("  FAIL: perfex_status returned nothing"); ok = False

print("\n  " + ("ALL PROTOCOL + SECURITY ASSERTIONS PASS" if ok else "FAILURES ABOVE"))
