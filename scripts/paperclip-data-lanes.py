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
    "title": "NUR-84: DATA LAYER — connect all trading databases into the algorithm (+ congressional tracker)",
    "description": ("Founder 2026-08-02: connect to ALL the databases to figure the trading algorithm. Registry "
                    "built + probed: data/market-data.json (scripts/market-data-connect.py). Skill: "
                    "trading-data-lanes.\n"
                    "VERIFIED SOURCES (probe evidence on the registry): Yahoo LIVE (SAF structure), CoinGecko "
                    "LIVE, Senate efdsearch LIVE, Quiver page OK (key), Alpha Vantage demo OK (key), GDELT "
                    "429 (backoff), House disclosures 500 (retry new site), FRED 400 (key), Finnhub 401 "
                    "(key), Stooq 404 (format).\n"
                    "TRADING DEV BUILD (alongside NUR-83):\n"
                    "1) ALGORITHM INPUTS: SAF structure (Yahoo, saf-scanner.py) + macro overlay (FRED once "
                    "key) + sentiment (GDELT backoff) + crypto (CoinGecko) + CONGRESSIONAL FLOW module.\n"
                    "2) CONGRESSIONAL TRACKER (founder): Nancy Pelosi + other top officials (committee chairs, "
                    "leadership, visible traders) — parse House disclosure transactions (new site API/XML; "
                    "Senate efdsearch bulk w/ session) + Quiver (key drop). Output: per-official trade log: "
                    "ticker, buy/sell, amount range, filing date, asset (stock/options). Digest: daily flags "
                    "on notable buys (NVDA/SPY/options patterns). LAG WARNING: disclosures are 30-45 days "
                    "late — information, not front-running; display lag prominently.\n"
                    "3) KEYS TO DROP (founder): QUIVER_API_KEY, ALPHAVANTAGE_API_KEY, FRED_API_KEY, "
                    "FINNHUB_API_KEY (~/uploads/). After each drop: rerun market-data-connect.py, update "
                    "registry, extend algorithm.\n"
                    "4) Evidence: registry output + first congressional digest on this issue."),
    "assigneeAgentId": CTO, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-84 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
