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
    "title": "NUR-71: CTO PRIORITY — NURA Agent OS Mission Control dashboard build",
    "description": ("Founder 2026-08-02 PRIORITY: build the NURA Agent OS Mission Control — the company operating "
                    "screen (modeled on Julian Goldie's Agent OS pattern, verified: one surface, live status, "
                    "click-to-inspect control rooms, shared memory, goals + analytics, model switcher).\n\n"
                    "ZONES (map to LIVE data sources — no fake data):\n"
                    "1) REACTOR CORE: Hermes gateway + Paperclip board health (http://127.0.0.1:3101/api/health).\n"
                    "2) ORBITING AGENTS: 57 board agents w/ status (board API :3101) — Atlas, Orion, Iris, Midas, "
                    "Tally, Florence, Meridian, Frame, Reel, Echo, Ink, Nexus... click-to-inspect = role, current "
                    "task, activity log.\n"
                    "3) TASK TICKER: live feed of issue updates + cron runs + delegation transcripts.\n"
                    "4) LANE HEALTH STRIP: model router free lanes (5/5), MCP lanes (openFDA/PubMed/CDC/Mirth/"
                    "OpenEMR/BioPortal/Redis/Qdrant), SLA ledger, docker-health.\n"
                    "5) MEMORY PANEL: mem0 + RAG nura-docs (379) + self-model summary.\n"
                    "6) APPROVALS QUEUE: human-in-the-loop items (gate doctrine visible).\n"
                    "7) GOALS + ANALYTICS: scrum metrics, deployment gates, funnel, doc-time targets.\n"
                    "8) MODEL SWITCHER: DeepSeek/Gemini/Gemma/free lanes — flip live.\n\n"
                    "BUILD: zero-dep HTML first pass (dark theme, like docs/diagrams/rcm-architecture-pack.html) "
                    "with real endpoint probes; then Next.js+Tailwind if approved. Deploy on :9119 (env-gated) or "
                    "new host. GATES: live probes only (no fabricated status); verification evidence on this "
                    "issue; Hermes holds the endpoint registry + verify-all.py for wiring.\n"
                    "Owner: Orion (CTO) — priority over lower-priority backlog."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-71 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
