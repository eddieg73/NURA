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
    "title": "CEO DIRECTIVE (founder): NEW COMPANY — NURA EMS Agency (Mobile Integrated Health). RECRUIT + HIRE President + licensing team",
    "description": ("FOUNDER 2026-08-02: new company. Mobile Integrated Health (MIH) unit with NP or PA + fire dept "
                    "partnership. First unit: LAUDERHILL. Partner clinic: Medisun Health Group. Revenue: REVA Air "
                    "Ambulance ground-portion partnership. Spec: vault EMSAgency-Spec.md (FL requirements verified).\n\n"
                    "=== THE MODEL (references) ===\n"
                    "1) The Villages Fire + UF Mobile Stroke Unit — CT-on-wheels, tele-stroke, fire partnership.\n"
                    "2) LA Fire NP1 — NP-led MIH ambulance: 911 alternative response, chronic/behavioral/post-"
                    "discharge, 911 call reduction.\n"
                    "3) NURA MIH unit: NP/PA + paramedic + driver + NURA telemetry/CDS lane (NEWS2, provider gate); "
                    "Medisun = medical home for follow-up.\n\n"
                    "=== ATLAS MUST EXECUTE ===\n"
                    "1) RECRUIT + HIRE the EMS Agency PRESIDENT (healthcare/EMS operations executive; fire-dept "
                    "relationships a must).\n"
                    "2) HIRE the licensing/business team: business-plan writer + FL EMS licensing coordinator "
                    "(they produce the FULL application package).\n"
                    "3) The FLORIDA PACKAGE (verified requirements, DOH Bureau of EMS): DH Form 631 (ALS/BLS license, "
                    "30+ days lead) · COPCN from BROWARD COUNTY COMMISSION · Medical Director (FL physician + DEA) · "
                    "DH Form 1510 vehicle permits · insurance · trauma transport protocols · DMS-approved radio (Med 8) "
                    "· management plan (training/dispatch/complaints/accidents/QA) · fees 401.34.\n"
                    "4) FIRE DEPT MOU: Lauderhill FD (or BSO) — dispatch integration + mutual aid (founder: 'handle "
                    "calls like LA Fire').\n"
                    "5) REVA AIR AMBULANCE ground partnership: NURA provides the ground ambulance for REVA's ground "
                    "portion — recurring revenue lane.\n"
                    "6) Business plan deliverable: 90-day to license + first unit operating in Lauderhill.\n\n"
                    "=== GOVERNING ===\n"
                    "- Medical director + clinical oversight = non-negotiable (401.265 F.S.)\n"
                    "- No PHI in artifacts · provider-gated CDS · founder approval for all contracts/leases\n"
                    "- Hires wired hermes_gateway; President reports to CEO (Atlas).\n"
                    "- Evidence: President hired + team roster + business plan skeleton by Monday scrum 2026-08-03."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("EMS Agency directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
