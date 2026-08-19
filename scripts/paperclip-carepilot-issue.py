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
    "title": "NUR-55: CEO DIRECTIVE — CarePilot Phase 2 build (Work Queue first) + Medisun coding tables",
    "description": ("CarePilot Phase 2 (founder 2026-08-02, for Oussama/Amrit; spec encoded in skill "
                    "carepilot-phase2-work-queue). Do NOT rebuild existing reports (RAF/HCC/Financial/MLR/Pharmacy/"
                    "Cohorts/Post-Discharge/Solis/eMedical). Goal: turn reports into work — Work Queue FIRST "
                    "(Generate Work buttons -> Call/Schedule/Medication tasks, assigned, due, priority, status), "
                    "then Task Assignment, Provider My-Work dashboard, Care Management tracking (TCM/RPM/CCM/Community "
                    "Paramedic), Twilio + email comms with records, LLM suggestion-only service, MCP API for future "
                    "agents, Hermes communication layer, Mirth framework (Epic/Cerner/eCW/Athena), Patient Profile "
                    "tabs. Also build Medisun ICD bucket tables (medisun-coding-population-health skill): "
                    "icd_bucket_mapping + patient_tag_history (append-only) + manual_review_queue + GHL tagging.\n"
                    "Coordinating: Hermes holds both skills; assign build to Workflow Automation Dev (Loom) + MCP "
                    "Integrations Dev (Bridge) as needed; report per step on this issue."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-55 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
