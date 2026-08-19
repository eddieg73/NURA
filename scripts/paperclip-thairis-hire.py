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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

ADAPTER = {
    "adapter": "hermes_gateway",
    "adapterConfig": {"apiBaseUrl": "http://127.0.0.1:8642/v1"},
    "apiKey": env_file("/opt/data/profiles/nura/.env", ["API_SERVER_KEY"]),
}

roles = [
    {"name": "ThaiRIS Developer", "role": "engineer", "description": (
        "RIS (ThaiRIS) developer for the NURA imaging bundle. Owns: ThaiRIS local image build + DB schema "
        "(db-init/01-thairis.sql), MWL from Mirth ORM, reporting workflow, RIS config for the North Miami X-ray "
        "go-live (client #1). Coordinates with Frame (PACS admin) + Meridian (Mirth channels). Runbook: "
        "docs/manuals/MEDISUN-RIS-PACS-SETUP.md. Reports to CTO.")},
    {"name": "ThaiRIS Administrator", "role": "general", "description": (
        "RIS (ThaiRIS) administrator — daily ops of the RIS: worklist integrity, exam status, report queues, "
        "user/RBAC in ThaiRIS, modality worklist failures, backup of RIS DB. Supports the ThaiRIS Developer + "
        "Frame (PACS admin). North Miami = first site. Reports to CTO.")},
]

created = []
for r in roles:
    try:
        req = urllib.request.Request(base + f"/api/companies/{CID}/agents",
                                     data=json.dumps({**r, "apiKey": ADAPTER["apiKey"]}).encode(),
                                     headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read())
            aid = d.get("id") or d.get("agentId")
            created.append((r["name"], aid))
            print("HIRED:", r["name"], "->", aid)
    except urllib.error.HTTPError as e:
        print("ERR hiring", r["name"], e.code, e.read().decode()[:120])

if created:
    dev_id = created[0][1]
    issue = {
        "title": "NUR-75: THAIRIS — install + configure RIS with PACS and viewer (North Miami client #1)",
        "description": ("Founder 2026-08-02: install ThaiRIS (not yet installed — needs local image build + DB "
                        "secrets) and configure it WITH the PACS (Orthanc) and the viewer (OHIF).\n"
                        "STACK FILES: imaging-stack/docker-compose.pacs.yml (Orthanc + OHIF defined; ThaiRIS "
                        "service to add) · modules/orthanc/orthanc.json (CHANGE_ME password before first start) · "
                        "modules/ohif/app-config.js · db-init/01-thairis.sql.\n"
                        "BUILD: 1) host-side on 1441409: add ThaiRIS service (local image build per runbook §2), "
                        "DB secrets via env 0600; 2) configure ThaiRIS <-> Orthanc (DICOMweb/query-retrieve; "
                        "NURAORTHANC AE) + OHIF viewer -> Orthanc DICOMweb (viewer.nuratech.ai + clinic-local per "
                        "site); 3) MWL: OpenEMR/eMedical order -> Mirth ORM -> ThaiRIS worklist; 4) X-ray-first "
                        "go-live (GE unit, AE NURA_NM_XRAY): C-STORE -> Orthanc, viewer link in chart (SOP-3), "
                        "report -> ORU back; 5) verify curls :8042/:3000/:8085 + evidence.\n"
                        "OWNERS: ThaiRIS Developer (build/config) + ThaiRIS Administrator (ops) + Frame (PACS). "
                        "Sequence after Docker access ruling (NUR-68)."),
        "assigneeAgentId": dev_id, "priority": "high", "status": "todo",
    }
    try:
        req = urllib.request.Request(base + f"/api/companies/{CID}/issues",
                                     data=json.dumps(issue).encode(), headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read())
            print("NUR-75 ->", resp.status, d.get("id", d.get("issueId", "?")))
    except urllib.error.HTTPError as e:
        print("ERR NUR-75", e.code, e.read().decode()[:150])
