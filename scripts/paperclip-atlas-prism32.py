import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"

req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
aid = atlas["id"] if atlas else None
if not aid:
    print("ATLAS NOT FOUND"); raise SystemExit(1)

issue = {
    "title": "CEO DIRECTIVE (founder): PRISM32 TEAM — harness-absorption orchestrator (verified installed) — edge deployment + delegation lanes",
    "description": ("FOUNDER 2026-08-02: setup a team for Prism32 (MegaDyneSystems, pypi v6.9.0 — VERIFIED: single "
                    "447KB stdlib file installed at python-packages/prism32.py; /harness scan + quantum context + "
                    "fenced-block architecture confirmed in source).\n"
                    "WHAT IT IS: ultra-light agentic harness — orchestrates OTHER AI CLIs (harness absorption: "
                    "Hermes, Claude Code, Aider, Gemini CLI, Goose, Cursor) as super-subagents, shares state via "
                    "in-memory 'quantum context', writes/loads its own plugins on the fly, runs on 6MB+ RAM — "
                    "routers, 3D printers, comma.ai devices, truck Jetsons.\n"
                    "TEAM (Atlas hires/assigns):\n"
                    "1) PRISM32 HARNESS ENGINEER - deploy + operate the harness: local sandbox install, "
                    "plugin authoring, fenced-block workflow\n"
                    "2) HARNESS-ABSORPTION INTEGRATOR - wire /harness scan to detect our stack (Hermes, Codex, "
                    "Claude lanes) + delegation patterns (heavy reasoning -> Hermes, code refactor -> "
                    "Codex/Claude) + quantum-context state sharing between subagents\n"
                    "3) EDGE DEPLOYMENT ENGINEER - target devices: truck Jetson (OBD2/vehicle lanes), comma "
                    "device (openpilot lane, POST-DRIVE only), clinic edge nodes\n"
                    "4) SAFETY REVIEWER - the execute-block model = LLM-written shell commands that RUN: "
                    "sandbox/container, no secrets, no vehicle bus until gated, black box every action\n"
                    "DELIVERABLES: local sandbox + /harness scan of our stack by 2026-08-06 · delegation PoC "
                    "(Prism32 -> Hermes subagent task) by 2026-08-12 · edge deployment plan (truck Jetson + "
                    "comma post-drive) by 2026-08-20 · safety review of execute-block policy by 2026-08-08.\n"
                    "DOCTRINE: Prism32 = EXPERIMENTAL orchestrator - sandboxed, never trusted with production "
                    "secrets or live vehicle control; Hermes remains the canonical brain (one brain, one "
                    "writer); Prism32 is a tool of the org, not a second brain."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Prism32 team directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
