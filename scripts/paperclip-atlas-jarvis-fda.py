import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"

req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
aid = atlas["id"] if atlas else None
if not aid:
    print("ATLAS NOT FOUND"); raise SystemExit(1)

issues = [
    {"title": "CEO DIRECTIVE (founder): PROVISION production.nuratech.ai + configure JARVIS vision cascade (detection · caption · structured report · EHR delivery)",
     "description": ("FOUNDER 2026-08-02: spin up production.nuratech.ai and configure the vision cascade models — "
                     "JARVIS detection, caption, structured report generation with EHR delivery.\n"
                     "CURRENT STATE (verified): production.nuratech.ai DOES NOT RESOLVE (000) — must be provisioned "
                     "(Hostinger project + DNS + TLS via NPM) · Orthanc :8042 UP but placeholder password "
                     "(CHANGE_ME_ORTHANC_PASS — fix owed) · OHIF viewer gated by NUR-110 · imaging-vision script unfinished.\n"
                     "SCOPE: (1) provision production.nuratech.ai (or radiology.nuratech.ai — counsel on naming) (2) "
                     "Orthanc password + TLS (3) OHIF viewer deploy (NUR-110 unblock Monday) (4) JARVIS cascade v0: "
                     "detection model (bounding boxes — CXR nodule/fracture/line-tube), caption model (findings "
                     "semantics), structured report generator (findings/impression/ICD-10 suggestions — ASSISTIVE), "
                     "EHR delivery lane (FHIR DiagnosticReport → OpenEMR; Mirth HL7 ORU to referring MD) (5) provider "
                     "gate + critical-findings escalation (Twilio 727) (6) audit trail (model versions + human edits).\n"
                     "OWNERS: Bridge (cascade + prod deploy) · Meridian (Mirth/EHR lanes) · QA (test suite) · CTO "
                     "oversight. FDA/validation posture = separate directive (de novo team).\n"
                     "EVIDENCE: prod URL live + first real DICOM through cascade → structured report by 2026-08-14.")},
    {"title": "CEO DIRECTIVE (founder): ALEXIS HIRES FDA DE NOVO DOCUMENTATION TEAM — regulatory submission package",
     "description": ("FOUNDER 2026-08-02: 'Put FDA validation and posture in the queue and have Aleyse (Alexis "
                     "Schloeter, corporate partner) hire a team to work on the documentation for FDA approval de "
                     "novo.'\n"
                     "SCOPE — DE NOVO SUBMISSION PACKAGE for JARVIS (radiology decision-support) + NURA clinical "
                     "assist features (per the Reg A risk posture — assistive, physician-supervised):\n"
                     "1) Regulatory strategy: de novo classification vs 510(k) predicate analysis; Q-Sub/pre-sub "
                     "meeting request with FDA\n"
                     "2) Software documentation: 21 CFR 820 QMS, IEC 62304 (software lifecycle), IEC 82304, SOUP "
                     "inventory, requirements/design/traceability\n"
                     "3) Clinical evaluation: literature, simulated-case performance evidence, clinician "
                     "acceptance testing\n"
                     "4) Usability/human factors (IEC 62366) + cybersecurity (SBOM, UL 2900 posture, NIST 800-53 "
                     "mapping)\n"
                     "5) Labeling + IFU drafts; 510(k)-style summary if predicate route chosen\n"
                     "OWNER: Alexis Schloeter hires the Regulatory Affairs Specialist team (hermes_gateway) — "
                     "working with SEC/legal counsel + Assurance (cost) + clinical (founder).\n"
                     "DELIVERABLES: regulatory strategy memo by 2026-08-14 · Q-Sub package draft by 2026-09-01 · "
                     "documentation framework live by 2026-09-15.")},
    {"title": "CEO DIRECTIVE (founder): RIS + PACS + EMR CONFIGURATION MUST FINISH BY MONDAY (09:00 EDT scrum)",
     "description": ("FOUNDER 2026-08-02: 'Make sure Atlas finishes configuring the RIS, the PACS, the EMR by "
                     "Monday.'\n"
                     "DEADLINE: MONDAY 2026-08-03 09:00 EDT — before/at the scrum, evidence on this issue.\n"
                     "SCOPE: RIS (radiology workflow — ThaiRIS/eMedical lane) · PACS (Orthanc password fix + OHIF "
                     "viewer + TLS) · EMR (OpenEMR clinical lane config — OAuth/connectivity) — all gated by the "
                     "NUR-110 Docker ruling (Monday scrum item).\n"
                     "RULE: NUR-110 ruling = the gate; if the ruling blocks, the blocker + fallback plan must be "
                     "stated ON this issue by Monday 09:00 (no silent carries — kanban discipline).")},
]

for it in issues:
    it["assigneeAgentId"] = aid
    it["priority"] = "critical" if "JARVIS" in it["title"] else ("high" if "FDA" in it["title"] else "critical")
    it["status"] = "todo"
    try:
        req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(it).encode(),
                                     headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print("->", r.status, d.get("id", "?"), "|", it["title"][:60])
    except urllib.error.HTTPError as e:
        print("ERR", e.code, e.read().decode()[:200], "|", it["title"][:50])
