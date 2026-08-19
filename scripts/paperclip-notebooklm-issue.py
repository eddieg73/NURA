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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

issue = {
    "title": "NUR-72: TO DO LATER — Playwright + VNC browser automation for Gemini Notebook (NotebookLM)",
    "description": ("QUEUED (founder 2026-08-02, do later — not urgent): set up RPA access to Gemini Notebook "
                    "(NotebookLM).\n\n"
                    "CONTEXT: NotebookLM = Gemini Notebook (rebranded July 2026). NO public API (verified); "
                    "Enterprise API = paid GCP (not used). Human layer on iPad works today. This task = Path A: "
                    "automate the browser so Hermes operates NotebookLM (upload vault docs, trigger Audio "
                    "Overviews, download outputs).\n"
                    "STEPS (when scheduled): 1) Chromium install (playwright, backgrounded — verify completion); "
                    "2) Playwright persistent profile + xvfb/VNC tunnel on this box (visible session for ONE-TIME "
                    "interactive login by founder — he types credentials himself, never Hermes); 3) session-cookie "
                    "persistence; 4) NotebookLM automation script (upload /opt/data/Obsidian Vault manuals, "
                    "generate Audio Overview, save output to media engine folder); 5) verify + evidence.\n"
                    "SECURITY: founder's Google password/2FA NEVER handled by Hermes; cookies stay in the "
                    "profile dir 0600; no PHI into NotebookLM.\n"
                    "OWNER: Orion (CTO) schedules; Bridge (MCP Integrations Dev) implements; Hermes holds the "
                    "context + install state (proc_9a82b6c8aa7e)."),
    "assigneeAgentId": CTO, "priority": "medium", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-72 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
