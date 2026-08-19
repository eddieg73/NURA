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
MERIDIAN = "b2c4d576-cc8c-4f45-bcdd-83b16055975d"

issue = {
    "title": "NUR-69: MERIDIAN — Mirth Connect ↔ eMedical EMR for Medisun (RIS/PACS client #1)",
    "description": ("Founder 2026-08-02: build the NextGen Mirth Connect connection to eMedical EMR for Medisun — "
                    "client #1 of the RIS/PACS SaaS division (DIV-1). This is the division's first integration "
                    "delivery; the reference case.\n\n"
                    "BUILD (per hermes-mirth-connect + hermes-hl7-simulator skills):\n"
                    "1) INTERFACE DISCOVERY FIRST (never invent): obtain the eMedical integration spec — HL7 v2 "
                    "(MLLP) vs FHIR R4 vs proprietary; supported message types (ADT/ORM/ORU/DFT); endpoint "
                    "host/port/creds. Founder/Oussama supply.\n"
                    "2) CHANNELS (mirth-docker-stack seeds exist — channel_adt.json/channel_orm.json): "
                    "ADT^A04/A08 demographics eMedical->ThaiRIS; ORM^O01 imaging orders -> ThaiRIS MWL (CPTs "
                    "71045/74176/74181/76700/77067/77080); ORU^R01 results -> eMedical; DFT^P03 fee sheets -> "
                    "Perfex (sanitized, external_ref idempotency).\n"
                    "3) VALIDATE with synthetic HL7 (hermes-hl7-simulator) BEFORE live; channel XML .bak; "
                    "dead-letter + retries.\n"
                    "4) DELIVER: North Miami X-ray-first loop via eMedical (order -> MWL -> study -> viewer link "
                    "-> report -> ORU).\n"
                    "GATES: provider review on mappings; PHI never to Perfex; eMedical interface spec is the "
                    "first milestone — post it on this issue. Meridian 2 (EMR integrations) supports; Hermes "
                    "holds skills + runbook (MEDISUN-RIS-PACS-SETUP.md)."),
    "assigneeAgentId": MERIDIAN, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-69 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
