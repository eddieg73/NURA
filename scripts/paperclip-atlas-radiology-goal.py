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

issue = {
    "title": "CEO DIRECTIVE (founder): RADIOLOGY PRODUCT GOAL — agentic wet reads + over reads · small local LLM in EVERY desktop app · mammo CAD + modality/equipment connections",
    "description": ("FOUNDER 2026-08-02 (three lanes, one goal):\n"
                    "GOAL: AGENTIC RADIOLOGY READING providing WET READS and OVER READS.\n"
                    "- WET READ = preliminary interpretation for time-critical findings (on-call/attending "
                    "radiologist drafts, critical-findings escalation in minutes, Twilio 727 lane)\n"
                    "- OVER READ = secondary review / QA (peer read or AI-assisted discrepancy check, structured "
                    "tracking, feedback loop into the cascade)\n"
                    "- JARVIS drafts BOTH modes (assistive), providers sign, everything audit-logged.\n"
                    "LANE 1 — SMALL LOCAL LLM WITH EVERY DESKTOP APPLICATION: bundle an on-device LLM "
                    "(llama.cpp GGUF 1-4B class / ONNX) inside every clinician desktop app — privacy-first, "
                    "offline-capable, zero per-seat inference cost; desktop packaging + update lane; per-tenant "
                    "doctrine (NUR-106). HIRE: desktop-app developers + LLM edge packaging engineers (Atlas).\n"
                    "LANE 2 — EQUIPMENT CONNECTIONS: mammo CAD + radiology devices/computers/equipment:\n"
                    "- MAMMO CAD integration (iCAD ProFound-class / Hologic / Volpara-class detection lanes; "
                    "CAD results as DICOM SR/secondary capture into the reading flow)\n"
                    "- MODALITY CONNECTIONS: mammo, US, CT, MRI, DR, DX — DICOM modality worklist + MPPS "
                    "(performed procedure steps), C-STORE ingest, modality vendor interfaces\n"
                    "- PACS/RIS worklist + report distribution (Mirth HL7 ORU, FHIR DiagnosticReport)\n"
                    "- The universal 4-surface connector pattern (API/MCP/CLI/WEBHOOK) for every device lane\n"
                    "LANE 3 — TEAM: Atlas hires Radiology Reading Product Devs (wet/over-read workflow + "
                    "escalation), Desktop App + Edge LLM Devs, Modality Integration Devs (DICOM/MPPS/CAD). "
                    "Works with the Radiology AI team (44b5b4d6) + Alexis FDA lane + Meridian (Mirth) + "
                    "Florence (OpenEMR) + QA.\n"
                    "GATES: desktop LLM PoC (Qwen3-4B GGUF in app shell) by 2026-08-15 · wet-read workflow v0 "
                    "(draft + critical escalation) by 2026-08-22 · over-read/QA v0 by 2026-09-01 · mammo CAD "
                    "integration PoC (vendor SDK or DICOM SR lane) by 2026-09-15 · MPPS/modality worklist live "
                    "by 2026-09-15. Sim-first + provider gate + audit doctrine everywhere."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Radiology product goal directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
