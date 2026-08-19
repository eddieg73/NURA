import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
issue_id = "1ed6ab0e-6553-4686-be4d-7ee7cd4dfd7e"

body = ("FOUNDER DIRECTIVE (2026-08-02): founder compensation plan — 'I may take a salary, but I would like my "
        "compensation agreement like Elon Musk.'\n"
        "PLAN BANKED: vault SEC/Founder-Compensation-Plan.md — Tesla-2018-style performance award translated to the "
        "WY LLC: modest-or-nominal salary (founder's choice) + 12 all-or-nothing tranches, EACH gated on a "
        "valuation/raise milestone AND an operating KPI (Reg A $1M/$4M → post-money $10M → $50M → $100M → $250M → "
        "$1B ladder; tenants/ARR/clinics/EMS/Aero KPIs); 10-year term; 5-year post-vest hold; ASC 718 expense with "
        "Assurance; founder recusal on own-comp vote.\n"
        "SPECIALIST ACTIONS: (1) integrate full comp terms into Reg A 'Executive Compensation' + 'Related Party' "
        "sections (disclosure required, not prohibited) (2) confirm valuation-milestone ladder aligns with the "
        "offering structure (3) flag 409A/83(b)/unit-class issues for counsel.\n"
        "BOARD PATH: approval at Monday scrum (Atlas governance; Advisor consult); founder signature + board minutes.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments", data=json.dumps({"body": body}).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("comp plan -> sec specialist ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
