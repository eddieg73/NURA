import json, urllib.request, urllib.error

def env_file(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env_file("/opt/data/paperclip-runtime/mcp.env", ["PAPERCLIP_API_KEY", "API_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-87: Claude Code in Docker, wired to LLM APIs (DeepSeek verified)",
    "description": ("Founder 2026-08-02: install Claude Code on Docker + wire to the LLM API.\n"
                    "VERIFIED LOCALLY (Hermes box): Claude Code 2.1.220 installed "
                    "(node-packages/node_modules/@anthropic-ai/claude-code); wrapper scripts/claude-code-run.sh; "
                    "DeepSeek Anthropic-compat lane WORKS (api.deepseek.com/anthropic -> real completions, "
                    "CC-DEEPSEEK-WIRED-OK). Gemini lane via OpenRouter: google/* model slugs rejected by the "
                    "client (gating under investigation); native Anthropic needs ANTHROPIC_API_KEY drop.\n"
                    "CTO BUILD:\n"
                    "1) DOCKER: claude-code container on 1441409 (node:22 image, npm i -g "
                    "@anthropic-ai/claude-code, entry = cli-wrapper) + compose service; keep the Hermes-side "
                    "CLI as the dev lane.\n"
                    "2) WIRE: env via mounted .env 0600 — ANTHROPIC_BASE_URL/AUTH_TOKEN per provider "
                    "(deepseek primary; openrouter alt; anthropic when key drops); expose MCP servers to "
                    "Claude Code inside the container (mcp config mount) per the claude-code skill.\n"
                    "3) ORG ACCESS: Paperclip dev agents can shell into the container (hermes_gateway lane) "
                    "for coding tasks — document the run command.\n"
                    "4) GEMINI GATING: investigate OpenRouter Anthropic-compat for google/* models; if "
                    "unsupported, use Gemini native OpenAI-compat through a thin proxy for Claude Code.\n"
                    "5) Evidence: container up + one DeepSeek-backed claude run from inside the container on "
                    "this issue. Sequence after NUR-68 (docker access ruling)."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-87 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
