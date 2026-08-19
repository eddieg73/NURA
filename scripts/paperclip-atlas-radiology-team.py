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
    "title": "CEO DIRECTIVE (founder): HIRE RADIOLOGY AI BUILD TEAM — vision cascade (detection · caption · structured report) + datasets + training infra",
    "description": ("FOUNDER 2026-08-02: do we have the developers to build AI agents that read radiology images — "
                    "need vision, LLMs, datasets, training sets. Competitive landscape reviewed (see directive notes).\n"
                    "HONEST CAPABILITY AUDIT: HAVE = Bridge (MCP/agents), Meridian (Mirth/HL7), Florence (OpenEMR), "
                    "Loom (n8n), QA, Gemini vision lane (live), Bio_ClinicalBERT ONNX (deployed), PACS skeleton "
                    "(Orthanc :8042), sim tools, eval suite, IDC sample DICOM. MISSING = dedicated Radiology ML "
                    "Engineer (vision model training), ML Data Engineer (dataset/labeling pipeline), Radiology "
                    "Clinical Advisor (radiologist for labels + validation — founder network), training GPU (Lab has "
                    "none; RunPod invalid; GPU purchase = founder sign-off).\n"
                    "HIRE (Atlas): (1) RADIOLOGY ML ENGINEER — detection (CXR nodule/fracture/line-tube bounding "
                    "boxes), caption, structured report generation; MONAI/ONNX stack; (2) ML DATA ENGINEER — dataset "
                    "acquisition + preprocessing + labeling pipeline (public sets first); (3) RADIOLOGY CLINICAL "
                    "ADVISOR (radiologist, founder-network) — label QA + validation + reader studies.\n"
                    "DATASETS (public, verified 08-02): VinDr-CXR (18K radiologist-annotated DICOM, 22 findings + 6 "
                    "diagnoses — BEST starting set) · CheXpert (224K, Stanford) · MIMIC-CXR (377K, PhysioNet "
                    "credentialed — CITI required) · PadChest (160K) · LIDC-IDRI (CT nodules) · IDC (already on disk).\n"
                    "TRAINING INFRA: decision needed — 1x 24GB GPU on Lab (founder sign-off) or cloud spot; "
                    "PCCP-style retraining envelope from day one (FDA de novo lane).\n"
                    "DELIVERABLES: team hired by 2026-08-10 · dataset pipeline v1 (VinDr-CXR) by 2026-08-18 · "
                    "detection model v0 trained + evaluated (mAP on VinDr test) by 2026-09-01 · caption + structured "
                    "report v0 by 2026-09-15.\n"
                    "COMPETITIVE NOTES (2026, verified): 1,451 FDA AI/ML authorizations end-2025, radiology = 1,104 "
                    "(76%) — every clearance narrow-indication; PCCP (2024) = living models; ACR Assess-AI + first "
                    "practice parameter (May 2026); NO autonomous reading authorized — human-in-the-loop is law. "
                    "Leaders: Aidoc (triage, ~1,000 hospitals), Lunit (CXR, 510(k) 2024), Annalise (124 findings), "
                    "Qure (30+, TB standard, edge-friendly), Viz (LVO De Novo + NTAP), Rad AI (drafting LLM), xAID "
                    "(full-CT foundation drafting). IBM Watson = cautionary tale (imaging divested to Merative 2022; "
                    "integration + clinician trust beat grand claims). OUR WEDGE: end-to-end agentic (detection + "
                    "structured report + EHR delivery + sovereign/offline + provider gate) on agnostic per-tenant "
                    "platform — integration debt is the moat."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Radiology AI team directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
