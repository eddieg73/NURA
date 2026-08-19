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
    "title": "NUR-97: GRANT — Claude Code access for Atlas + dev team (wrapper live; verify + train)",
    "description": ("Founder 2026-08-02: did we give Atlas and the team Claude Code access? PARTIAL — the CLI + "
                    "wrapper exist on the Hermes box (claude-code-run.sh, DeepSeek lane VERIFIED with real "
                    "completions); agents with gateway terminal access CAN invoke it, but no explicit grant/"
                    "training was issued.\n"
                    "CTO EXECUTE:\n"
                    "1) GRANT: document in the org (skill claude-code Agent Grant section) that dev agents use "
                    "`bash /opt/data/profiles/nura/scripts/claude-code-run.sh deepseek -p \"<task>\" "
                    "--max-turns 10` for heavy coding; Hermes stays orchestrator.\n"
                    "2) VERIFY: have ONE dev agent (e.g., Canvas/Florence) run the wrapper via the gateway and "
                    "post the output on this issue as evidence (claude --version + one tiny task).\n"
                    "3) COST: DeepSeek lane billed to existing keys (no new spend); cap per task "
                    "--max-budget-usd 2.\n"
                    "4) DOCKER: container variant remains queued behind NUR-68 (NUR-87)."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-97 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
