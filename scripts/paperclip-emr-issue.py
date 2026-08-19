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
    "name": "EMR Integrations Developer",
    "role": "general",
    "title": "EMR Integrations Developer — NextGen Connect / Mirth HL7-FHIR bridges",
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "reportsTo": CTO,
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/agents", data=json.dumps(agent).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        dev_id = d.get("id")
        print("AGENT ->", r.status, dev_id, d.get("name", "?"))
except urllib.error.HTTPError as e:
    print("AGENT ERR", e.code, e.read().decode()[:250])
    raise SystemExit

issue = {
    "title": "NUR-49: CEO DIRECTIVE — hire EMR Integrations Developer (done by Hermes on CEO behalf) + Mirth build",
    "description": ("CEO confirmed hire: EMR Integrations Developer (created, hermes_gateway). Scope (founder "
                    "2026-08-02):\n\n"
                    "1) DEPLOY Mirth Connect (mirth-docker-stack :8081, canonical) + channels per manifest IV:\n"
                    "   - ADT channel: HL7 ADT^A04/A08 -> normalize demographics -> update OpenEMR patient + "
                    "create/link Perfex CRM customer (sanitized).\n"
                    "   - MDM channel: NURA AI scribe SOAP/transcript -> HL7 MDM^T02 -> external EHR chart structures.\n"
                    "   - DFT channel: OpenEMR fee sheets -> DFT^P03 -> CPT/ICD + provider -> Perfex invoices + "
                    "patient statements.\n"
                    "2) HL7 v2 / FHIR R4 bridges: lab ORU -> OpenEMR labs, scheduling ORM -> MWL (with RIS/PACS Admin), "
                    "ADT sync, external integration patterns (Epic/Cerner/Athena/Quest per manifest IV).\n"
                    "3) CHANNEL HEALTH: dead-letter queue + retries + idempotency; hermes-hl7-simulator synthetic tests "
                    "BEFORE go-live; channel monitoring in docker-health sweep; targets: C-STORE fail <0.01%, HL7 "
                    "error <0.1%, MWL >99.5%.\n"
                    "4) Mirth REST config via hermes-mirth-connect skill; .bak channel XML before edits; provider "
                    "review for clinical message mapping.\n"
                    "REFERENCE: clinical-operating-sop (medical SOP-1), hermes-mirth-connect, hermes-hl7-simulator, "
                    "openemr-perfex-integration, manifest IV."),
    "assigneeAgentId": CEO,
    "priority": "high",
    "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read())
        print("NUR-49 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ISSUE ERR", e.code, e.read().decode()[:200])
