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
    "title": "NUR-59: PROJECT — RATCHET (embodied AI for EMS/field ops) + xAI proposal tracking",
    "description": ("New project (founder 2026-08-02): RATCHET — human-supervised clinical autonomy platform "
                    "(commercial humanoids -> EMS/field-medicine teammates). Proposal doc: "
                    "docs/projects/RATCHET-XAI-PROPOSAL.md + skill ratchet-embodied-clinical-autonomy.\n\n"
                    "STATUS: confidential draft signed (May 2026) — xAI exploratory collaboration; 3-unit Mobile "
                    "Integrated Healthcare pilot South Florida; FDA-aligned SaMD planning; OpenEMR+PACS interop; "
                    "edge-AI humanoid workflows; hardware-agnostic.\n"
                    "CEO TASKS: 1) hold project on the board (milestones: proposal dispatch (founder-authorized), "
                    "partnership pipeline, MIH pilot plan, SaMD roadmap); 2) coordinate Orion (tech due diligence), "
                    "Vigil (compliance/SaMD), Midas (pilot economics); 3) no external outreach without founder "
                    "authorization. Hermes holds the skills/docs.\n"
                    "GUARDRAILS: human-supervised clinical autonomy (L0 doctrine) · claims gate · Phoenix SOG "
                    "protocols = controlled IP."),
    "assigneeAgentId": CEO,
    "priority": "medium",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-59 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
