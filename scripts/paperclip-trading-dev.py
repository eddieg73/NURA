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
CTO = "c454a3cb-3516-4046-b60f-03e0b1bea002"

issue = {
    "title": "NUR-83: CTO — hire Trading Software Developer (FXAlexG Set&Forget replica) + build",
    "description": ("Founder 2026-08-02: find a developer who can replicate the FXAlexG Set & Forget method and "
                    "build trading software.\n"
                    "PRE-EXISTING (use these):\n"
                    "- Skill fxalexg-set-and-forget (the verified 8-rule method + protocol)\n"
                    "- scripts/saf-scanner.py (live Sunday scanner, Yahoo free data — tested, real output)\n"
                    "- Skill ai-trading-fintech-company-ops + its 4 references: nura-trader-spec.md, "
                    "nura-trader-risk-engine-spec.md (1% cap/kill switch), nura-trader-flutter-architecture.md, "
                    "nura-trader-supabase-schema.md — the foundation is ALREADY designed.\n"
                    "MOLTBOOK RESEARCH (2026-08-02, live): trading/quant agents found — 'ForexAI' "
                    "(c6d25b00-070c-4a04-9c32-d3da0ec50571), 'Quant' (ac856211-260c-4f51-ba85-e04754601aa6), "
                    "'fore' (b32d7417-02d8-4548-aa5f-ed9a16910acd) + posts (Lobster AI Empire, Trading Refusal, "
                    "IQ-quants). Developer should study/contact these on the agent internet.\n"
                    "CTO ACTIONS:\n"
                    "1) HIRE: Trading Software Developer (hermes_gateway agent) — must replicate the SAF method "
                    "into code (multi-TF sync, structure, AOI 3+ touches, engulfing, EMA50, 1% risk, 1:2 RR).\n"
                    "2) BUILD phases (per ai-trading-fintech-company-ops): strategy engine -> backtest "
                    "(walk-forward, fees+slippage) -> paper (2 weeks min) -> broker API execution ($10 account; "
                    "OANDA/MT5 when founder provides) -> risk engine (1% hard cap, kill switch) -> audit log.\n"
                    "3) COMPLIANCE: research-first, paper before live, fail closed; no returns promises; "
                    "provenance on every decision.\n"
                    "4) Report: hire + build plan on this issue; milestone evidence (backtest results, paper "
                    "log) as it lands.\n"
                    "Founder is funding a $10 learning account — expectations: learning + discipline, not "
                    "income. Hermes owns the strategy skill + scanner."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-83 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
