"""Verify agentmemory MCP round-trip (the configured Hermes memory provider)."""
import json, subprocess, time, sys

proc = subprocess.Popen(["npx", "-y", "@agentmemory/mcp"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, text=True, bufsize=1)

def send(obj):
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()

send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                 "clientInfo": {"name": "verify", "version": "1.0"}}})
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
time.sleep(3)

stamp = "verify-" + time.strftime("%Y%m%d-%H%M%S")
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
      "params": {"name": "memory_save",
                 "arguments": {"content": f"agentmemory round-trip test {stamp} — Hermes memory provider verification.",
                               "type": "insight"}}})
time.sleep(6)
send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
      "params": {"name": "memory_recall", "arguments": {"query": "agentmemory round-trip test"}}})
time.sleep(8)
proc.terminate()
try:
    out, err = proc.communicate(timeout=10)
except Exception:
    out = proc.stdout.read() or ""

saved = recalled = False
for line in (out or "").splitlines():
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get("id") == 2:
        txt = json.dumps(d)[:300]
        print("  SAVE:", txt)
        saved = "error" not in txt.lower() or "success" in txt.lower()
    if d.get("id") == 3:
        txt = json.dumps(d)[:400]
        print("  RECALL:", txt)
        recalled = stamp.split("-")[-1][:6] in txt or "agentmemory" in txt
print("  SAVE ok:", saved, "| RECALL ok:", recalled)
