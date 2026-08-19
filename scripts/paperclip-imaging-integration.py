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
    "title": "NUR-61: Medisun RIS/PACS integration build — OpenEMR + Perfex tie-in",
    "description": ("Medisun imaging stack: host block + runbook docs/manuals/MEDISUN-RIS-PACS-SETUP.md (Orthanc + "
                    "OHIF + ThaiRIS on 1441409). After host deploy, build the tie-ins:\n"
                    "1) MIRTH CHANNELS (Meridian): ORM^O01 orders->ThaiRIS MWL (CPTs 71045/74176/74181/76700/77067/"
                    "77080); ORU^R01 results->OpenEMR; ADT^A04/A08 demographics->ThaiRIS; DFT^P03 fee sheets->Perfex.\n"
                    "2) OPENEMR (Florence): tokenized OHIF viewer links on encounters (SOP-3); imaging order "
                    "encounter codes; results documents. Requires OpenEMR API creds (lane mock->api).\n"
                    "3) PERFEX (Tally): imaging fee-sheet->invoice bridge (SOP-2, sanitized generic lines, "
                    "external_ref idempotency); auth/eligibility custom fields; modality P&L for NURA Imaging SaaS "
                    "division (DIV-1).\n"
                    "GATES: provider review on report mapping; PHI never to Perfex; Mirth validated with synthetic "
                    "HL7 before go-live (hermes-hl7-simulator).\n"
                    "CEO: sequence after host deploy verification (paste curls from the runbook)."),
    "assigneeAgentId": CEO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-61 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
