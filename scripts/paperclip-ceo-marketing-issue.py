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
ATLAS = "f2f6e8a6-6d99-4113-9604-1e8259fc1d83"

issue = {
    "title": "NUR-80: CEO — marketing org + strategy + launch (hire CMO + team, own the plan)",
    "description": ("Founder 2026-08-02: PAPERCLIP CEO (Atlas) owns the market response end-to-end.\n"
                    "MANDATE:\n"
                    "1) HIRE THE CMO + TEAM: confirm/formalize Iris (CMO, 084cd44f) as the marketing lead; hire "
                    "2-3 analysts under her: Competitive Intelligence Analyst, Marketing Analyst, Brand/Content "
                    "Strategist (hermes_gateway, report to CMO; CMO reports to CEO).\n"
                    "2) SWOT: NURA vs field — verified market facts (Abridge $400-600/mo KLAS-2x $5.3B; DAX "
                    "$369-830/mo Epic-native; Ambience $500-700+; Suki $299-399; Freed/Heidi ~$99 solo; NURA "
                    "planned $100-150 bundle + Hermes baked in + born-agnostic; gaps: validation, SOC2, "
                    "reference deployment).\n"
                    "3) SALES STRATEGY: from docs/manuals/NURA-SALES-PLAN.md (Dan Martell audience-first, ICPs "
                    "1-4, funnel metrics demo->trial 50% trial->paid 40%, objection handling).\n"
                    "4) MARKETING PLAN + LAUNCH: positioning (the operator-baked-in bundle at 1/3 enterprise "
                    "price), channels (media engine SOP-5/6/7 + X + Moltbook + LinkedIn), launch sequence tied "
                    "to the North Miami reference case (client #1), KPIs (MQL->demo 25%, NPS>70, churn<3%).\n"
                    "5) Weekly competitor brief (Fri 10:00 cron, skill competitive-intelligence-marketing) "
                    "feeds the CMO.\n"
                    "DELIVER on this issue: roster + SWOT + strategy + marketing plan + launch timeline. "
                    "NUR-79 = the CMO work order underneath."),
    "assigneeAgentId": ATLAS, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-80 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
