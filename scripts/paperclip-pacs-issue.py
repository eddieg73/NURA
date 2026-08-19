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

agent = {
    "name": "RIS/PACS Administrator",
    "role": "general",
    "title": "RIS/PACS Administrator — Orthanc, OHIF, THAIRIS, DICOM equipment config",
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "reportsTo": CTO,
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", data=json.dumps(agent).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        pacs_id = d.get("id")
        print("AGENT ->", r.status, pacs_id, d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("AGENT ERR", e.code, e.read().decode()[:250])
    raise SystemExit

issue = {
    "title": "NUR-47: CEO DIRECTIVE — hire RIS/PACS Administrator (done by Hermes on CEO behalf) + DICOM equipment build",
    "description": ("CEO confirmed hire: RIS/PACS Administrator agent (created, hermes_gateway). Scope (founder 2026-08-02):\n\n"
                    "1) DEPLOY: Orthanc + OHIF (imaging-stack pacs compose, KVM4), THAIRIS RIS (:8085), NPM hosts "
                    "pacs./viewer./ris.nuratech.ai. SET ORTHANC PASSWORD (CHANGE_ME) BEFORE FIRST START.\n"
                    "2) DICOM EQUIPMENT CONFIG: AE-title registry (name, IP, port 104/11112/4242, modality type, "
                    "location — static IPs only), modality firewall rules (C-STORE :4242 private, per NIST SP 1800-24 "
                    "zoning), transfer-syntax verification (test study per modality), DICOM TLS where supported.\n"
                    "3) MWL: OpenEMR orders -> Mirth HL7 ORM -> THAIRIS -> modality worklist; verify MWL per modality "
                    "(>99.5% success target).\n"
                    "4) VIEWER: OHIF app-config.js -> DICOMweb (orthanc:8042), tokenized viewer links for OpenEMR charts "
                    "(SOP-3).\n"
                    "5) OPS: orthanc-db + DICOM storage backups (db-snapshot + R2), storage tiering (cache 30-90d SSD -> "
                    "near-line -> archive), 99.9% PACS uptime, DR test within 90d of go-live.\n"
                    "GATES: PHI stays KVM4 (research imaging on KVM8 only) · no public DICOM ports · provider-approved "
                    "worklists · report per milestone on this issue."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-47 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
