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

body = ("MASTER DRAFT UPDATED TO v3.0 (2026-08-02) — vault SEC/NURA-RegA-Offering-Circular-DRAFT.md.\n"
        "CHANGES vs v2: (1) issuer = NURA TECH AI, INC. — WYOMING CORPORATION (per latest source; LLC→corp "
        "mechanics flagged) (2) instrument = Common Stock $0.0001 par, $20M max, $1,000 min (replaces $4M note "
        "structure — harmonize SAFE suite + comp plan) (3) real traction included: Medisun $250k contract + $100k "
        "install, $5k/mo (2 locations) + $3.5k/mo Brawlerz, recent profitability, founder $600k invested "
        "(management-prepared, unaudited) (4) Delaware IP HoldCo structure added (related-party item) (5) verticals: "
        "Clinical/Comms/CRM/ERP/RCM/Radiology-JARVIS/ONE/Embodied (6) JARVIS + NURA ONE + RCM + international-team "
        "risk factors (7) unaudited financials appendix (8) counsel checklist 12 items.\n"
        "SPECIALIST ACTION: review v3.0 (esp. common-stock vs note sequencing, IP HoldCo licensing disclosure, "
        "audit timeline for the unaudited statements) — gap review due 2026-08-06.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments", data=json.dumps({"body": body}).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("v3.0 update -> sec specialist ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
