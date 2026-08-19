import json, urllib.request, urllib.error

def env_file(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env_file("/opt/data/paperclip-runtime/mcp.env", ["PAPERCLIP_API_KEY", "API_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"
IRIS = "084cd44f-6570-4370-b8f0-fe66ec8b8baf"

issue = {
    "title": "NUR-79: CMO — SWOT + sales strategy + hire competitive team + marketing plan",
    "description": ("Founder 2026-08-02: CMO (Iris) owns market response. Skills available: "
                    "competitive-intelligence-marketing + NURA-SALES-PLAN + dan-martell-operating-system + "
                    "nura-product-lineup.\n"
                    "TASKS:\n"
                    "1) SWOT ANALYSIS (NURA vs field) — verified market facts embedded: Abridge $400-600/mo "
                    "(Best in KLAS 2x, $5.3B), DAX $369-830/mo (Epic-native, 200+ EHR), Ambience $500-700+ "
                    "(inpatient/coding), Suki $299-399, Freed/Heidi ~$99 (solo). NURA planned $100-150 with the "
                    "bundle (scribe+dialer+fax+imaging+evidence) + Hermes baked in + born-agnostic adapters. "
                    "Gaps: no clinical validation yet (MIMIC 10K + RCT planned P9), no SOC2/HITRUST yet, no "
                    "reference deployment yet (North Miami go-live pending).\n"
                    "2) SALES STRATEGY — from NURA-SALES-PLAN (Dan Martell audience-first; ICPs 1-4; funnel via "
                    "media engine; objection handling; metrics: demo->trial 50%, trial->paid 40%).\n"
                    "3) HIRE the competitive/marketing analysis team (2-3 agents: Competitive Intelligence "
                    "Analyst, Marketing Analyst, Brand/Content Strategist) — CMO owns hiring per best practice.\n"
                    "4) MARKETING PLAN — positioning (operator-baked-in bundle at 1/3 enterprise price), "
                    "channels (media engine SOP-5/6/7, X, Moltbook, LinkedIn), launch sequence tied to North "
                    "Miami reference case, metrics (MQL->demo 25%, demo->trial 50%, trial->paid 40%, NPS>70).\n"
                    "DELIVER: SWOT + sales strategy + roster + marketing plan on this issue. Weekly competitor "
                    "brief cron feeds you (Fri 10:00)."),
    "assigneeAgentId": IRIS, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-79 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
