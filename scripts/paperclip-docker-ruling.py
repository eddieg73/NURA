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
    "title": "NUR-110: DOCKER ACCESS RULING REQUIRED (deadline: Monday scrum 09:00) — unblocks 6 deploys",
    "description": ("FOUNDER-PUSHED (2026-08-02): the Docker-access ruling is the single biggest blocker. "
                    "The historical NUR-68 slot now holds the voice issue (voice_id ALREADY FIXED today — "
                    "Sarah/EXAVIT verified live); the ruling itself needs a clear owner and deadline.\n"
                    "CTO DECIDE + DOCUMENT on this issue by Monday 09:00 scrum:\n"
                    "1) Host deploy authority: who executes docker compose up on 1441409 (Hermes via docker "
                    "lanes :8100-8102, Oussama host-side, or both) and under what guardrails (deploy guard: "
                    "RAM>15% avail, disk<85%, backup first).\n"
                    "2) Blocker inventory to unblock: Orthanc/OHIF (imaging-stack) · ThaiRIS (NUR-75) · "
                    "Mirth channels (NUR-82) · WENO EPCS (NUR-76) · Claude Code container (NUR-87) · "
                    "Postgres app DB (NUR-103).\n"
                    "3) Rollback path per stack (compose down + snapshot).\n"
                    "Evidence: written ruling + first approved deploy log on this issue."),
    "assigneeAgentId": CTO, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-110 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
