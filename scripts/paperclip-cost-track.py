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
MIDAS = "9c2f1a4e-0000-0000-0000-000000000000"

# find Midas (CFO) id from the agents dump
import re
raw = open("/tmp/agents.json").read()
m = re.search(r'"id":"([^"]+)","companyId":"[^"]+","name":"Midas"', raw)
if m:
    MIDAS = m.group(1)
    print("Midas id:", MIDAS)

issue = {
    "title": "NUR-98: Per-developer cost tracking — weekly report + cron cost optimization",
    "description": ("Founder 2026-08-02: track cost per developer. BUILT: scripts/agent-cost-tracker.py reads "
                    "state.db session_model_usage (gateway already logs estimated_cost_usd per session with "
                    "model/billing_provider/tokens). FIRST RUN (2 days): 315 sessions, $11.93 est — top "
                    "owners: 2026-07-30 heavy session $4.95 (2,710 calls), cron c04325c5 (Incident Commander "
                    "5-min health check) $3.54 / 259 sessions, paperclip:company sessions visible $0.09.\n"
                    "CFO (Midas) EXECUTE:\n"
                    "1) WEEKLY COST REPORT: run agent-cost-tracker.py --days 7 on Mondays (scrum prep); "
                    "break down by developer/agent + cron; compare vs $9-15/mo budget doctrine; flag >$2 "
                    "owners.\n"
                    "2) COST OPTIMIZATION: Incident Commander 5-min check = the top recurring cost (~$1.7/day "
                    "est) — evaluate cadence to 15m or script-only health checks (no LLM) for uptime-only "
                    "probes; propose change to founder.\n"
                    "3) PER-DEVELOPER CAPS: agents use --max-budget-usd 2 per claude-code task; gateway "
                    "sessions logged; review monthly.\n"
                    "4) RECONCILIATION: estimated vs actual (billing_provider in DB; DeepSeek/OpenRouter "
                    "invoices) — monthly.\n"
                    "Evidence: first weekly report on this issue."),
    "assigneeAgentId": MIDAS, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-98 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
