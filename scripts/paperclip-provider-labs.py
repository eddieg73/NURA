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
    "title": "NUR-91: Implement NURA Provider Labs platform (founder's spec image, phases 1-13)",
    "description": ("Founder spec image 2026-08-02 (img_2dedf8556881.jpg) — NURA Provider Labs: "
                    "Clinician-Supervised Clinical Intelligence & Autonomous Workflow Orchestration. Full "
                    "summary archived: /opt/data/Obsidian Vault/NURA-OS/Provider-Labs-Implementation.md.\n"
                    "CORE (hub): Secure Ingestion -> OCR & Doc Processing -> Data Extraction & Normalization -> "
                    "Anomaly & Pattern Detection -> Differential Diagnosis Support -> Clinical Interpretation "
                    "Engine -> Risk Stratification & Red-Flags -> Recommended Actions -> PROVIDER REVIEW gate.\n"
                    "LAYERS: Presentation / Application / Integration / Data / Infrastructure. EVENT BUS = "
                    "HERMES (nura-clinical-operations-event-automation pattern).\n"
                    "CTO EXECUTE:\n"
                    "1) Map the 13 integration phases to concrete modules/skills (hermes-clinical-encounter-"
                    "orchestrator, hermes-clinical-foundation-architecture, hermes-clinical-safety-escalation, "
                    "nlp-clinical-notes, hermes-clinical-lab-review, hermes-diagnostic-reasoning); produce the "
                    "phase-by-phase build plan with owners.\n"
                    "2) PHI/clinical boundary: all pipelines stay on Clinic 1441409; provider review gate "
                    "MANDATORY before any recommended action reaches a chart (clinical doctrine).\n"
                    "3) Success metrics to instrument: Connection Reliability, Provider Coverage, Alert "
                    "Resolution Time.\n"
                    "4) Evidence per phase on this issue. Sequence after NUR-68 (docker ruling)."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-91 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
