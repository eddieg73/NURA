"""Save the memory-lane fix to agentmemory (the live Hermes provider) + verify."""
import json, subprocess, time

proc = subprocess.Popen(["npx", "-y", "@agentmemory/mcp"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, text=True, bufsize=1)

def send(o):
    proc.stdin.write(json.dumps(o) + "\n"); proc.stdin.flush()

send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                 "clientInfo": {"name": "hermes", "version": "1.0"}}})
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
time.sleep(3)

text = ("Memory-lane repair 2026-09-10 (Hermes CTO): "
        "(1) agentmemory is the configured Hermes memory provider — standalone MCP works, iii-engine daemon not required. "
        "(2) mem0 lane was broken by OpenAI credit exhaustion (429); rebuilt as deepseek-flash LLM + local fastembed "
        "BAAI/bge-base-en-v1.5 (768d) + qdrant localhost:6333 collection 'mem0'. Requires PYTHONPATH="
        "/opt/data/lazy-packages:/opt/data/fastembed-pkgs. Read+write verified. "
        "(3) Do NOT use OpenAI embeddings — no credits. Local Ollama lives on lab (:11434) but is often starved (load 99).")

send({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
      "params": {"name": "memory_save",
                 "arguments": {"content": text, "type": "insight",
                               "title": "Memory lanes fixed 2026-09-10"}}})
time.sleep(8)
proc.terminate()
out = proc.stdout.read() or ""
for line in out.splitlines():
    try: d = json.loads(line)
    except Exception: continue
    if d.get("id") == 2:
        print("  SAVED:", json.dumps(d.get("result", {}))[:220])
