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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"
issue = {
    "title": "NUR-43: BUILD DIRECTIVE — execute NURATECH.ai master manifest (playbook + manuals + build phases)",
    "description": ("CEO/CTO build directive (founder 2026-08-02). Canonical spec: docs/manuals/NURATECH-MASTER-MANIFEST.md + "
                    "FINAL-SOLUTION-DMAIC.md + OPERATIONS-PLAYBOOK.md + INSTRUCTION-MANUAL.md.\n\n"
                    "PHASE 1 (infra, 1-3d): Launch Pack (launch-kvm4.sh, node-agent.sh), Mirth deploy (:8081) with ADT/MDM/DFT "
                    "channels per manifest IV, PACS deploy (Orthanc/OHIF/THAIRIS on KVM4), Documo fax lane (wired, key pending), "
                    "Twilio lane verification in Perfex.\n"
                    "PHASE 2 (integrations, 3-7d): Perfex-OpenEMR bridge (NUR-41 CLI first), OpenEMR lane live (creds), "
                    "Notion ops DB live, n8n workflows (MCP-enabled), recall/scheduling engine.\n"
                    "PHASE 3 (product, 7-21d): Flutter app scaffold per manifest V (nuratech_ai, lib/ modules dialer/scribe/fax/"
                    "communication/scheduling/rcm_analytics), Doximity suite M1, Weave OS M2, Aesthetic suite M3.\n"
                    "PHASE 4 (AI, 21-45d): ambient scribe pipeline (SOAP → OpenEMR encounter sync), AI voice receptionist "
                    "(ElevenLabs/Twilio), AI copilot (drug/dose/chart), fax OCR + auto-filing.\n\n"
                    "CTO: determine + author any additional playbooks/manuals/runbooks the build needs (repo docs/manuals/). "
                    "Guardrails: operator-charter; PHI never leaves KVM4; approval-gated mutations; report per phase on this issue."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-43 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
