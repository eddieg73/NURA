#!/usr/bin/env python3
"""Create a detailed Notion project page: AI Quantitative Model (Gold/Oil) — full build spec +
PHP/Laravel developer instructions. Under CTO Suite (canonical engineering). Verifies read-back."""
import os, json, requests

def _token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return next(iter(d.values()))
    raise SystemExit("no token")

TOKEN=_token(); VER="2022-06-28"; H={"Authorization":f"Bearer {TOKEN}","Notion-Version":VER,"Content-Type":"application/json"}
API="https://api.notion.com/v1"
CTO_SUITE="3bea9b14-e498-816e-84c5-d9cda0497f87"

def req(m,p,b=None,t=40):
    r=requests.request(m,API+p,headers=H,json=b,timeout=t); return r.status_code,r.json()
def _t(x): return [{"type":"text","text":{"content":x}}]
def para(x): return {"object":"block","type":"paragraph","paragraph":{"rich_text":_t(x)}}
def head(x,l=2): return {"object":"block","type":f"heading_{l}",f"heading_{l}":{"rich_text":_t(x)}}
def bullet(x): return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":_t(x)}}
def num(x): return {"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":_t(x)}}
def callout(x,e="📈"): return {"object":"block","type":"callout","callout":{"rich_text":_t(x),"icon":{"type":"emoji","emoji":e}}}
def code(x): return {"object":"block","type":"code","code":{"rich_text":_t(x),"language":"bash"}}
def divider(): return {"object":"block","type":"divider","divider":{}}

TITLE="AI Quantitative Model — Gold & Oil Multi-Factor Trading System"
B=[
 callout("Professional-grade AI quantitative trading system for GOLD (XAU) and OIL (WTI/Brent). Multi-factor, 12 core algorithms, macro + micro factor blending, dynamic risk/position management. Built in PHP/Laravel (currently being clarified) or the stack of record. High-consequence financial system → approval-gated, auditable, deterministic-first.","📈"),
 head("Mission",2),
 para("Build a reproducible, evidence-backed trading intelligence system that identifies trends, assesses market regime, predicts return probability, controls risk, and dynamically manages position size for gold and oil — using the founder's brother-in-law's professional-grade algorithm suite."),
 head("1. Instrument & Data Model",2),
 num("GOLD (XAU/USD): macro factors — DXY dollar, real interest rates (TIPS), CPI/inflation, VIX risk index, gold ETF fund flows, CFTC COT positions (managed money), plus price/volume/ATR."),
 num("OIL (WTI or Brent): micro + unique factors — EIA weekly inventories (crude/gasoline/distillates), supply-demand balance, US production, refinery utilization, futures term structure, contango/backwardation, Brent-WTI spread, CFTC COT positions, plus price/volume/ATR."),
 head("2. Core Algorithm Library (12)",2),
 bullet("**Hurst exponent** — trend persistence / mean-reversion regime (long-memory)."),
 bullet("**EMA trend** — short/long exponential moving average crossovers (direction)."),
 bullet("**Donchian breakout** — N-day high/low channel (volatility breakout)."),
 bullet("**ADX** — trend strength (≥25 = trending, <20 = ranging)."),
 bullet("**TSMOM** — time-series momentum (sign of past return, scaled by vol)."),
 bullet("**Kaufman Adaptive MA (AMA)** — efficiency-ratio-weighted trend (adapts to noise)."),
 bullet("**Kalman filter** — state-space estimate of 'true' price / trend under noise."),
 bullet("**HMM state** — hidden Markov model regime classification (trend/sideways/high-vol)."),
 bullet("**GARCH volatility** — conditional volatility forecast (risk sizing)."),
 bullet("**XGBoost** — gradient-boosted ML signal combining engineered features."),
 bullet("**Bayesian probability** — posterior probability of up/down/sideways per regime."),
 bullet("**ATR dynamic position management** — position size = f(ATR) so risk is vol-targeted."),
 head("3. Architecture (PHP/Laravel)",2),
 code("# Laravel monolith with modular services (domain-first)\napp/\n  Domain/\n    Market/      # instruments, price, Volume, OHLCV ingestion\n    Feature/     # EMA, ADX, Hurst, Donchian, TSMOM, AMA, Kalman, HMM, GARCH, ATR, bayes, xgboost\n    Signal/      # feature -> signal (trend/regime/return-prob)\n    Risk/        # ATR target sizing, vol targeting, max risk, drawdown guard\n    Execution/   # order intent, paper/backtest, (live = gated)\n  Services/       # DataFeeder, FactorUpdater, SignalEngine, RiskManager, BacktestRunner\n  Console/        # artisan ingest/backtest/signal/risk commands\n  Jobs/           # scheduled data pulls (EIA, COT, ETF flows, price)\n  Http/           # API: /v1/signals, /v1/risk, /v1/backtest\nDatabase/         # migrations: instruments, prices, factors, signals, positions, backtests\n"),
 head("4. Data Ingestion Pipeline",2),
 bullet("Price/OHLCV: guaranteed-repeatable (deterministic first), source-refresh per schedule (Laravel schedule)."),
 bullet("Macro factors: DXY, TIPS real yield, CPI, VIX, GLD ETF flows, COT — each a typed factor provider with provenance + freshness gate."),
 bullet("Oil factors: EIA weekly inventories/supply/production/refinery, futures term-structure (contango/backwardation), Brent-WTI spread, COT — each with freshness + validation."),
 bullet("**Never-train-on-future rule**: features computed on point-in-time data only (no lookahead); backtest uses the exact feature view at each bar."),
 head("5. Signal Engine (regime-aware)",2),
 para("Combine the 12 algorithms into ONE per-bar composite: (a) regime (HURST + HMM + ADX) → (b) direction (EMA + Donchian + TSMOM + AMA + Kalman) → (c) return-probability (Bayesian + XGBoost) → (d) risk-size (ATR + GARCH + Bayesian confidence). Output: signal + confidence + suggested position."),
 head("6. Risk Management (non-negotiables)",2),
 bullet("Vol-target position sizing via ATR & GARCH (position inversely scales with risk)."),
 bullet("Max position/risk cap, drawdown guard, kill-switch, daily loss limit, no overnight leverage blow-up."),
 bullet("Dashboard-status any signal that hits risk limits — never silent. High-consequence → approval-gated for LIVE; paper/backtest first."),
 bullet("Audit every decision: timestamp → factor set → model output → position → rationale (traceable)."),
 head("7. Build Phases",2),
 num("P0 — Scaffold: Laravel app, Docker/compose, migrations, market+price ingestion, artisan commands. EVIDENCE: raw price pulls + DB rows."),
 num("P1 — Feature layer: EMA/ADX/Hurst/Donchian/TSMOM/AMA/Kalman/HMM/GARCH/ATR pure functions + unit tests (deterministic)."),
 num("P2 — Signal engine: regime + direction + return-prob (Bayesian + XGBoost) composite. Backtest harness on real gold/oil data."),
 num("P3 — Risk: ATR vol-targeted sizing + drawdown guard + kill-switch. Risk/return metrics over the backtest."),
 num("P4 — API/UI: /v1/signals + /v1/risk + a dashboard; paper-trading lane. LIVE = explicit founder approval (financial = high-consequence)."),
 head("8. Developer Instructions (PHP/Laravel)",2),
 bullet("Stack: PHP 8.2+, Laravel 11, MySQL/Postgres, Redis (queue/cache), cron via `schedule:run`, Docker compose for dev/repro, Pest/PHPUnit tests."),
 bullet("Setup: `composer create-project`, then modules; use strict types, typed DTOs, no raw SQL (Eloquent/query-builder)."),
 bullet("Reproduce: deterministic + seeded; random-number functions injected; every backtest run reproducible from a data snapshot."),
 bullet("Safety: financial proof-of-concept = backtest/paper only; LIVE is approval-gated, logged, kill-switch always armed."),
 bullet("Kill-criterion gate: before any capital, a 90-day backtest + drawdown/Sharpe target + a named existing system it replaces + a prewritten kill rule."),
 head("9. Status",2),
 bullet("P0 — Scoping (spec drafted). Owner: Hermes (CTO). Priority: P1. NUR-quant. Financial = HIGH-CONSEQUENCE; approval-gated; no live authority without explicit founder sign-off."),
 divider(),
 para("Registry: run as candidate lane in docs/AI-Product-Registry.md. Backend of record = PHP/Laravel per the founder. Deterministic-first; verify-before-declare; audit every decision."),
]

def create_page(pid,title,blocks):
    body={"parent":{"page_id":pid},"properties":{"title":{"title":_t(title)}},"children":blocks[:100]}
    st,d=req("POST","/pages",body)
    return st,d

st,d=create_page(CTO_SUITE,TITLE,B)
if st>=400:
    print("ERR",st,d.get("message",d)[:200])
else:
    pid=d.get("id")
    print("OK page:",pid,"| url:",d.get("url"))
    # verify read-back
    st2,d2=req("GET",f"/blocks/{pid}/children?page_size=100")
    bl=d2.get("results",[]) if st2<400 else []
    print("blocks:",len(bl))
    for b in bl[:8]:
        bt=b.get("type"); rt=b.get(bt,{}).get("rich_text",[]) if isinstance(b.get(bt),dict) else []
        txt="".join(x.get("plain_text","") for x in rt)
        if txt: print("  [",bt,"]",txt[:70])
