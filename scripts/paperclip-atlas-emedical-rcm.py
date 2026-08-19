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
    "title": "CEO DIRECTIVE (founder): ALEXIS'S TEAM — eMedical integration (Medisun PACS + AI) + RCM/practice-management deep-dive (bill · charge · dispute) + OpenEMR PM tied to Perfex seamlessly",
    "description": ("FOUNDER 2026-08-02: 'Keep Brawlerz, keep Medisun PACS and AI tied into eMedical for Alexis. Read "
                    "all documentation on eMedical, learn how to bill, how to create a charge, how to dispute. "
                    "Look at a revenue cycle management company / billing company like Kareo, Epic, Cerner — the "
                    "EMR has a practice management component; that practice management component from OPENEMR "
                    "needs to be tied in with Perfex seamlessly, and any other EMR that we connect. Have Aleyse "
                    "assigned the team to this?' — ASSIGNED: ALEXIS SCHLOETER's team owns this workstream.\n"
                    "SCOPE:\n"
                    "1) EMEDICAL INTEGRATION (Medisun lane): tie Medisun PACS + AI (JARVIS lane) into eMedical "
                    "(EMS ePCR platform) — study eMedical docs fully: billing tab (insurance coverage, transport "
                    "classification, medical necessity, CMS service level, phys-cert statements, supplies), "
                    "charge creation, and dispute/denial handling; Mirth HL7 bridge eMedical <-> PACS/OpenEMR\n"
                    "2) RCM DEEP-DIVE (verified sources): the billing lifecycle — CHARGE CREATION (fee sheets, "
                    "CPT/ICD10 pairing, fee entry) -> CLAIM GENERATION (CMS-1500 / X12-837) -> CLEARINGHOUSE "
                    "(999/277 status) -> EOB/ERA-835 posting -> PATIENT STATEMENTS -> DENIALS: root cause, "
                    "rework, resubmission (resub code 7), appeal; denial code taxonomy (CO-16 etc.); KPIs: "
                    "clean-claim rate, denial rate, A/R aging\n"
                    "3) PRACTICE MANAGEMENT TIE: OpenEMR PM module (Fees/Billing Manager, EOB/ERA, denials, "
                    "reports) <-> Perfex SEAMLESSLY (tickets/tasks/invoicing mirror) + the SAME PM pattern for "
                    "ANY EMR we connect (agnostic doctrine — Kareo/Epic/Cerner PM study: what their PM does, "
                    "what OpenEMR's does, what NURA RCM adds: denial intelligence, claims scrubbing, eligibility "
                    "verification, tamper-evident audit)\n"
                    "4) NURA RCM product spec update from this study (the RCM vertical in the Reg A + SaaS "
                    "offering)\n"
                    "OWNER: Alexis Schloeter's team (hires/assigns hermes_gateway) + Meridian (Mirth) + Florence "
                    "(OpenEMR) + Tally (Perfex) + founder (clinical billing expertise).\n"
                    "DELIVERABLES: eMedical docs study + billing/dispute playbook by 2026-08-10 · OpenEMR PM <-> "
                    "Perfex seamless flow PoC by 2026-08-18 · RCM spec v2 + Kareo/Epic/Cerner PM comparison by "
                    "2026-08-21."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("eMedical + RCM directive (Alexis) ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
