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
CEO = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"

issue = {
    "title": "NUR-62: CEO SET-IT-ALL-UP — full board ownership + weekly scrum reports",
    "description": ("Founder directive 2026-08-02: CEO (Atlas) takes FULL ownership of the build. "
                    "Board truth found by scrum pull (paperclip-scrum-report.py): 57 issues, ALL attributed to the "
                    "API-key owner (Canvas) and status blocked — assignments/statuses are not real.\n\n"
                    "CEO MUST:\n"
                    "1) REASSIGN every NUR-41..61 + DIV-1 to its real owner (Orion CTO, Midas, Tally, Florence, "
                    "Loom, Frame, Bridge, Meridian, Echo, Ink, Nexus, Reel, Iris, Vigil, Canvas/Pixel/Forge/Beacon) "
                    "and set correct statuses (todo/in_progress/in_review/done/blocked).\n"
                    "2) Drive the build: unblock via Hermes (lanes/creds/scripts); escalate credential drops to "
                    "founder weekly.\n"
                    "3) WEEKLY SCRUM REPORT: every Monday 09:00 via the NURA Weekly Scrum ceremony — Hermes pulls "
                    "the board (paperclip-scrum-report.py), CEO annotates: progress per workstream, blockers, "
                    "next-week plan, founder actions needed. Report delivered to founder in Telegram.\n"
                    "4) No issue stays unowned or misassigned for more than one week."),
    "assigneeAgentId": CEO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-62 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
