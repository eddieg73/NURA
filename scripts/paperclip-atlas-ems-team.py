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
    "title": "CEO DIRECTIVE (founder): Design + BUILD the NURA EMS team — use the AMR/Paramedics Plus outbid study",
    "description": ("FOUNDER 2026-08-02: use the Texas outbid competitive study (AMR/Paramedics Plus, directive "
                    "0e3a0d0b) to DESIGN and BUILD the team that manages the NURA EMS Agency (company #5).\n\n"
                    "=== DESIGN INPUT (from competitor study) ===\n"
                    "AMR/PP structure the company around: 911 operations · dispatch/communications · fleet & "
                    "maintenance · billing/RCM · clinical/medical-director relations · compliance/licensing · HR/crews "
                    "· business development (RFPs).\n"
                    "NURA DESIGN RULE: same functions, LEANER + automated — NURA lanes replace their manual ops "
                    "(RCM = the Perfex/NMI lane · dispatch intelligence = telemetry + NURA CDS · QA = audit lane · "
                    "compliance = licensing tracker). Lean-senior org (Musk doctrine): few, senior, automated.\n\n"
                    "=== TEAM TO DESIGN + BUILD ===\n"
                    "1) PRESIDENT (already tasked — RECRUIT now, EMS ops exec, fire-dept relationships).\n"
                    "2) OPERATIONS LEAD — 911/MIH ops, response-time compliance, dispatch integration.\n"
                    "3) CLINICAL LEAD (NP/PA senior) — MIH unit clinical ops + medical director liaison (FL "
                    "physician + DEA, 401.265).\n"
                    "4) FLEET/FACILITIES — vehicles, Med 8 radio, maintenance (REVA ground vehicles included).\n"
                    "5) BILLING/RCM — EMS claims (ALS/BLS rates, collections — NURA RCM lane).\n"
                    "6) COMPLIANCE/LICENSING — FL DOH package, Broward COPCN, DH Form 1510s, renewals.\n"
                    "7) BUSINESS DEVELOPMENT — Texas RFP pipeline (the outbid playbook), REVA + municipal contracts.\n\n"
                    "=== DELIVERABLES ===\n"
                    "Org chart (role → owner → reports-to President) · role specs · hire list with names wired "
                    "(hermes_gateway) · first-90-day plan (license → Lauderhill unit → first contract).\n"
                    "Evidence: org chart + role specs posted by Monday scrum 2026-08-03; hires wired by 2026-08-10.\n"
                    "Founder approves org chart before hires beyond the President."),
    "assigneeAgentId": aid, "priority": "critical", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("EMS team build directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
