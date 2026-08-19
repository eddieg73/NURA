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

body = ("FOUNDER (2026-08-02): THE ATTORNEY WORKS WITH THE ACCOUNTING TEAM FOR A SOLID PROJECT — joint workstream "
        "with NURA Assurance (internal accounting firm, Midas CFO) on REG A FILING READINESS.\n"
        "JOINT DELIVERABLES (attorney + Assurance):\n"
        "1) AUDIT-READY FINANCIALS: engagement of independent auditor + books to audit standard (Assurance leads; "
        "attorney defines SEC requirements: Form 1-A financial statement rules — 2 years audited for Tier 1)\n"
        "2) CAP TABLE + EQUITY STRUCTURE: full cap table, entity structure (DE/WY per founder plan), option/unit "
        "plans — attorney legal framing + accounting equity treatment\n"
        "3) USE-OF-PROCEEDS BUDGET: line-item budget the SEC will scrutinize (attorney) + CFO/Assurance cost "
        "validation\n"
        "4) MD&A SUPPORT: operating history, liquidity, results (Assurance data + attorney disclosure framing)\n"
        "5) RELATED-PARTY TRANSACTIONS: disclosure + arms-length documentation (founder/affiliates/clinics — "
        "both teams)\n"
        "6) NOTE ACCOUNTING: convertible note treatment (ASC 470/815 — beneficial conversion, derivative "
        "assessment) — Assurance books + attorney terms\n"
        "7) ONGOING REPORTING CALENDAR: 1-K/1-SA semi-annual/annual + 1-Z exit (attorney) fed by Assurance "
        "monthly close\n"
        "RULES: the accounting firm (Assurance) provides the numbers; the attorney provides the legal/disclosure "
        "frame; no number without a source; audit engagement = founder-approved spend.\n"
        "EVIDENCE: joint readiness plan + task ownership matrix by 2026-08-10.")
try:
    req = urllib.request.Request(base + f"/api/issues/{issue_id}/comments", data=json.dumps({"body": body}).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("attorney+accounting coordination ->", r.status)
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
