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
    "title": "NUR-67: SPECIALTY DOCTOR NETWORK — build a doctor for every specialty + connect their APIs/MCP",
    "description": ("Founder 2026-08-02: Paperclip builds a DOCTOR for every medical specialty — named specialty "
                    "agents (synthetic clinicians), each with its own connected APIs + MCP lanes for that "
                    "specialty's data. Doc: NURA-SYNTHETIC-CLINICIAN.md SPECIALTY DOCTOR NETWORK.\n\n"
                    "MODEL: doctor = agent persona + specialty skill set (the 170+ skill library has the specialty "
                    "playbooks: cardiology-specialty, dermatology-specialty, endocrinology-specialty, "
                    "gastroenterology-specialty, neurology-specialty, ob-gyn-surgical-specialty, "
                    "orthopedic-surgery-specialty, podiatry-surgery-specialty, urology-specialty, wound-care, "
                    "psychiatry, pulmonology/interventional, Mohs, oral-maxillofacial, general surgery, "
                    "dermatologic surgery, internal-medicine-specialty, emergency/tactical...) + evidence/API "
                    "lanes (openFDA/PubMed/BioPortal/CDC/OpenEvidence + specialty registries) + per-specialty "
                    "template library (SOAP/H&P/consult).\n"
                    "ROUTING: medical-specialty-router (MoE) sends cases to the right doctor; frontier escalation "
                    "when needed.\n"
                    "BUILD ORDER (practice value): aesthetics -> endocrinology/HRT/GLP-1 -> primary care -> "
                    "psychiatry (TMS) -> radiology/imaging -> long-tail.\n"
                    "DELIVERY: specialty doctors ship INSIDE the master app; specialty lane connectors = API/MCP "
                    "wiring per doctor; all skills ship with the SaaS.\n"
                    "CEO: create the specialty doctor agents (hermes_gateway), assign each a skill set + lanes, "
                    "sequence by build order, report roster on this issue. Hermes holds the skills + lane "
                    "registry."),
    "assigneeAgentId": CEO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-67 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
