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
    {"title": "CEO DIRECTIVE: HIRE + manage the CAREPILOT team (CarePilot MSO — population health/RAF product)",
     "description": ("FOUNDER 2026-08-02: CarePilot MSO (carepilot.nuratech.ai — 'Sign in · Care Pilot MSO', Laravel, "
                     "username+password auth) runs on a SEPARATE Hostinger account (panel creds pending from founder). "
                     "CTO (Hermes) is probing schema + reviewing build (probe in progress; login creds Alexsis/Alexsis "
                     "REJECTED — awaiting correct creds).\n"
                     "ATLAS: hire a CarePilot product team — dev (Osama built it — confirm founder re-engagement), "
                     "ops/QA, data/reporting — to own the program: schema map, feature roadmap, hosting admin (2nd "
                     "Hostinger account), population-health reports. Evidence: team roster + hosting access plan by "
                     "Monday scrum.")},
    {"title": "CEO DIRECTIVE: PERFEX <-> OPENEMR flawless interop squad (founder: 'make these two programs speak flawlessly')",
     "description": ("FOUNDER 2026-08-02: hire a team of Perfex developers to work WITH OpenEMR developers so the two "
                     "systems integrate flawlessly (billing/CRM <-> EHR).\n"
                     "EXISTING ROSTER (assign, hire only true gaps): Tally (Perfex CRM Developer, OpenEMR sync) · "
                     "Florence (OpenEMR Dev — concierge/HRT/GLP-1) · Meridian (Mirth/FHIR-HL7 bridges) · Loom (n8n "
                     "workflow builder) · QA & Test Engineering Lead · openemr-perfex-integration skill (already "
                     "banked).\n"
                     "SQUAD MISSION: bidirectional claims/encounters/patients sync, billing integrity (Perfex=CRM/"
                     "billing, OpenEMR=clinical), reconciliation, error-free handoffs. Deliver: integration spec + "
                     "test suite (nura-clinical-regression-suite lane) by 2026-08-10. Evidence: squad roster + spec.")},
    {"title": "CEO DIRECTIVE: WENO EPCS DEVELOPER — own the e-prescribing integration (NUR-76)",
     "description": ("FOUNDER 2026-08-02: develop a WENO developer role to MANAGE the EPCS integration (NUR-76 filed: "
                     "WENO Exchange EZ, $119/yr/prescriber, OpenEMR module; DEA MG5963296 expiry 2026-09-30 = hard "
                     "gate).\n"
                     "ATLAS: hire WENO EPCS Developer (hermes_gateway wired) — scope: WENO module deployment (blocked "
                     "by NUR-110 docker ruling — route through it), identity proofing (NIST IAL2-style), 2FA at sign, "
                     "DEA renewal tracking (license registry watchdog). First deliverable: WENO integration plan + "
                     "DEA renewal checklist by Monday scrum.")},
]

for it in issues:
    it["assigneeAgentId"] = aid
    it["priority"] = "high"
    it["status"] = "todo"
    try:
        req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(it).encode(),
                                     headers=hdr, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print("->", r.status, d.get("id", "?"), "|", it["title"][:60])
    except urllib.error.HTTPError as e:
        print("ERR", e.code, e.read().decode()[:150], "|", it["title"][:60])
