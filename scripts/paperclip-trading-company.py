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
    "title": "NUR-85: CEO — build the NURA Trading Division (PwC-grade), hire investment team, study market",
    "description": ("Founder 2026-08-02: build a trading company at Big-4-grade professionalism (PwC-style "
                    "rigor: research, compliance, audit, separation of duties). CEO (Atlas) owns org + mandate.\n"
                    "BUILD (like the SaaS Division pattern — a Paperclip company):\n"
                    "1) CREATE division company: NURA Capital Markets (or name the CEO decides) with its own "
                    "board + projects.\n"
                    "2) HIRE the investment team (hermes_gateway, report to division CEO):\n"
                    "   - CIO / Head of Investment Strategy (owns the market-study mandate)\n"
                    "   - Quant Researcher (SAF method replication + backtests, walk-forward)\n"
                    "   - Risk & Compliance Officer (1% hard cap, kill switch, STOCK-Act/lag labeling, "
                    "audit trail — from nura-trader-risk-engine-spec.md)\n"
                    "   - Trading Systems Developer (execution lane, broker API, paper-then-live pipeline)\n"
                    "   - Market Intelligence Analyst (congressional tracker: Pelosi + top officials; macro "
                    "FRED; sentiment GDELT; crypto CoinGecko — per trading-data-lanes)\n"
                    "3) MANDATE — STUDY THE MARKET per board decisions:\n"
                    "   - Phase 1 (4 weeks): market study + strategy research — use the data layer "
                    "(data/market-data.json), SAF method, congressional flow; deliver a written market study "
                    "+ proposed strategy list to the board (Atlas + Eddie) for decision\n"
                    "   - Phase 2: board-approved strategy -> backtest (walk-forward, fees+slippage) -> paper "
                    "(min 2 weeks)\n"
                    "   - Phase 3: LIVE only after board approval + founder account ($1,000 learning account, "
                    "1% = $10 risk cap; broker API drop from founder)\n"
                    "4) COMPLIANCE FRAME (from ai-trading-fintech-company-ops): research-first, paper before "
                    "live, fail closed, provenance on every decision, no returns promises, congressional "
                    "disclosures are public information with 30-45d lag (never front-running claims).\n"
                    "DELIVER on this issue: division created + roster + market-study plan + first weekly "
                    "study cadence (Monday with the board scrum)."),
    "assigneeAgentId": ATLAS, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-85 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
