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
    "title": "CEO DIRECTIVE (founder): COMPETITIVE — AMR / Paramedics Plus — outbid Texas playbook",
    "description": ("FOUNDER 2026-08-02: 'Have Atlas look at American Medical Response or Paramedics Plus — outbid "
                    "Texas.' Research + strategy task (evidence-first).\n\n"
                    "=== INTEL (verified 2026-08-02) ===\n"
                    "Texas market = county/city RFPs, single-provider contracts, MICU (ALS) license, 3-yr terms + "
                    "extensions, subsidy + user-fee (APC = Average Patient Charge) funding, response-time compliance "
                    "(e.g. 7.5-min avg).\n"
                    "- AMR (Global Medical Response): expanding in TX small cities — Royse City (Jan 1 start, FD-"
                    "stationed), Temple/Bell County (since 2017), Belton (1-yr + 2 options; vehicles leased $2,100/mo; "
                    "ALS base $1,125; response 7.5-min avg). Weaknesses: national cookie-cutter, rate hikes passed to "
                    "residents, staffing churn (Belton FD lost 17 in 17 months), subsidy dependence.\n"
                    "- Paramedics Plus (ETMC-affiliated, East Texas roots): strong TX 911 contracts, hospital-integrated "
                    "model. Weakness: regional footprint, less tech-forward.\n\n"
                    "=== OUTBID PLAYBOOK (build this) ===\n"
                    "1) TARGET MAP: catalog TX ESDs/counties with open or upcoming EMS RFP cycles (monitor Fannin/"
                    "Brown-style public RFP boards + ESD meeting calendars) — focus mid-size counties, cities where "
                    "AMR just won (contract churn = re-bid in 3-5 yrs) and rural gaps AMR/PP skip.\n"
                    "2) PRICE: bid on APC + subsidy REDUCTION (maximize collections via the NURA RCM lane; lower "
                    "subsidy = the county budget win).\n"
                    "3) DIFFERENTIATOR: MIH/community paramedicine (LA Fire NP1 model) — 911 call reduction = direct "
                    "county savings; fire-dept partnership story (Royse City shows AMR uses the same hook — we beat "
                    "them with the Medisun medical home + NURA telemetry CDS).\n"
                    "4) ENTRY: non-emergency/interfacility + event standby contracts first (lower barrier, build the "
                    "license + track record), then 911 RFP.\n"
                    "5) DELIVERABLES: (a) AMR dossier + (b) Paramedics Plus dossier (contracts, prices, weaknesses) "
                    "(c) TX market/RFP map (d) bid template (e) target list with RFP dates.\n"
                    "Evidence: dossier + map + first 3 targets with dates by 2026-08-10. Founder reviews before any "
                    "bid submission."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Texas outbid directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
