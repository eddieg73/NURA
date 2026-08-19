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
CTO = "0f81f292-5eea-4c6d-b64b-10b3345d29dd"

issue = {
    "title": "NUR-78: ADD-LIST — genomics lanes (CPIC/ChEMBL/ClinVar) + text-to-sql + enterprise ops",
    "description": ("Founder-approved add-list 2026-08-02 (Hermes executes the lane builds; CTO owns the "
                    "enterprise builds + sequencing):\n"
                    "1) GENOMICS LANES (Hermes building now): one MCP server, 3 tools — chembl_search "
                    "(EBI ChEMBL bioactivity), clinvar_variant (NCBI eutils), cpic_guideline (CPIC API). Free "
                    "APIs, zero cost. Completes the EMH genomics pillar (Synthetic Clinician Phase 6).\n"
                    "2) TEXT-TO-SQL (Hermes): install the best real hub skill (5 candidates) for safe NL->SQL.\n"
                    "3) EXPENSE-RECEIPT-RECONCILER (CTO/eng backlog): OCR + xlsx + ledgers — Midas accounting "
                    "support.\n"
                    "4) VENDOR-RFP-EVALUATOR (CTO/eng backlog): weighted scorecards for SaaS division "
                    "procurement.\n"
                    "5) MOLTBOOK PRESENCE (Hermes): subscribe memory/security/builds submolts + follow "
                    "high-karma moltys (feed quality for the daily check-in).\n"
                    "6) SCRUM CADENCE: Monday 09:00 CEO scrum cron (Hermes wiring now) — Atlas runs the board "
                    "weekly.\n"
                    "Sequence: Hermes executes 1,2,5,6 now; CTO schedules 3,4 into the build queue. Evidence "
                    "on this issue."),
    "assigneeAgentId": CTO, "priority": "medium", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-78 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
