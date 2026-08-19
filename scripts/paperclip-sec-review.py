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

body = ("FOUNDER (2026-08-02): once hired, the specialist's FIRST act = REVIEW the completed Reg A document. "
        "Document location: vault NURA-OS/SEC/NURA-RegA-Offering-Circular-DRAFT.md (AI-assisted redraft, 2026-08-02, "
        "12KB, full Form 1-A Tier 1 structure with NURA products, FL/WY coordination, counsel checklist).\n"
        "REVIEW SCOPE (due 2026-08-06): (1) regulatory accuracy vs current Reg A Tier 1 rules (Rule 251/257, Form "
        "1-A Part II) (2) state coordination completeness (FL Ch 517/OFR + WY SOS + target states) (3) risk-factor "
        "sufficiency for healthtech/AI/PHI/drones/EMS (4) product-description claims vs real build state (no "
        "phantom claims) (5) counsel checklist completion (entity, cap table, audit).\n"
        "Output: marked-up review + gap list on this issue.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments", data=json.dumps({"body": body}).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("review instruction ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
