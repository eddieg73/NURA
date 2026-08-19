#!/usr/bin/env python3
"""GEMMA-4 MCP SERVER — the sovereign-Gemma lane via the Lab's Ollama (the mesh-private!).
The MCP-tools: generate (the chat!) · list-models · status — the FastMCP-stdio-lane."""
import os, json, sys, urllib.request

OLLAMA = os.environ.get("GEMMA_OLLAMA_URL", "http://10.10.0.2:11434")
MODEL = os.environ.get("GEMMA_MODEL", "gemma4:e2b")

def llm(prompt, model=MODEL, max_tokens=500):
    body = {"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": max_tokens}}
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read()).get("response", "")
    except Exception as e:
        return f"ERR: {str(e)[:80]}"

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("gemma4")

    @mcp.tool()
    def generate(prompt: str, max_tokens: int = 500, model: str = "") -> str:
        """Generate a response from the sovereign models (the default Gemma-4; the GLM-5.2 or qwen via the model-param!)."""
        return llm(prompt, model=model or MODEL, max_tokens=max_tokens)

    @mcp.tool()
    def list_models() -> str:
        """List the Ollama models available on the sovereign lane."""
        try:
            with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
                d = json.loads(r.read())
                return ", ".join(m["name"] for m in d.get("models", []))
        except Exception as e:
            return f"ERR: {str(e)[:60]}"

    @mcp.tool()
    def status() -> str:
        """The sovereign-lane status."""
        try:
            with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10) as r:
                return f"Ollama reachable at {OLLAMA} (model: {MODEL})"
        except Exception as e:
            return f"Ollama unreachable: {str(e)[:60]}"

    mcp.run(transport="stdio")
except ImportError:
    # the fallback: the plain-stdio JSONRPC-minimal!
    for line in sys.stdin:
        try:
            req = json.loads(line)
            if req.get("method") == "tools/list":
                print(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), "result": {"tools": [
                    {"name": "generate", "description": "Generate from the sovereign Gemma-4", "inputSchema": {"type": "object", "properties": {"prompt": {"type": "string"}}}},
                    {"name": "status", "description": "The sovereign-lane status", "inputSchema": {"type": "object"}}
                ]}}), flush=True)
            elif req.get("method") == "tools/call" and req.get("params", {}).get("name") == "generate":
                args = req["params"].get("arguments", {})
                print(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), "result": {"content": [{"type": "text", "text": llm(args.get("prompt", ""))}]}}), flush=True)
            elif req.get("method") == "tools/call" and req.get("params", {}).get("name") == "status":
                print(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), "result": {"content": [{"type": "text", "text": f"Gemma-4 lane ready ({OLLAMA}/{MODEL})"}]}}), flush=True)
        except Exception:
            pass
