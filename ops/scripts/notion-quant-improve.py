#!/usr/bin/env python3
"""Append industry-validated improvements to the AI Quant Model Notion project page."""
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
PAGE="3d3a9b14-e498-81da-b51d-fcfdc5061c6e"  # AI Quant Model
def req(m,p,b=None,t=40):
    r=requests.request(m,API+p,headers=H,json=b,timeout=t); return r.status_code,r.json()
def _t(x): return [{"type":"text","text":{"content":x}}]
def bullet(x): return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":_t(x)}}
def head(x,l=2): return {"object":"block","type":f"heading_{l}",f"heading_{l}":{"rich_text":_t(x)}}
def callout(x,e="📈"): return {"object":"block","type":"callout","callout":{"rich_text":_t(x),"icon":{"type":"emoji","emoji":e}}}
def divider(): return {"object":"block","type":"divider","divider":{}}

B=[ divider(),
 callout("INDUSTRY-VALIDATED IMPROVEMENTS (2026-09-05, from live GitHub quant ecosystems) — the edge that separates a demo from a fund-grade system. Evidence-backed, not opinion.","📈"),
 head("1. Walk-Forward Validation (the overfitting killer)",2),
 bullet("InelidaMarketScanner (GitHub): in-sample profit factor 2.27 vs out-of-sample ceiling 1.173 — the gap is the whole game. MANDATORY: train→test on future-only data, one-day signal lag. A system is not validated until OOS holds."),
 head("2. Monte Carlo Risk Validation (N=10,000) before capital",2),
 bullet("YQTS (GitHub gold): gate on a PASS matrix — P(profit)≥65%, P(ruin)≤10% (target 0%), mean return, 5th-percentile, VaR(95%), P(maxDD>20%)≤15%."),
 head("3. Five-Layer Risk Ladder (proven)",2),
 bullet("Per-trade 2% (RR~1:5) · daily 5% · weekly 10% drawdown · kill-switch 20% · circuit-break 2 losses→stop. Independent risk manager (can veto the signal engine)."),
 head("4. Regime-Conditional GARCH",2),
 bullet("wisdomgu/regim: regime-conditional GARCH(1,1) cuts 5-day vol-forecast RMSE by +58.6% vs unconditional. Fit GARCH per regime; crash regime = vol-aware sizing + halt-and-wait."),
 head("5. Bayesian Changepoint beats HMM on timing (PELT/BOCPD)",2),
 bullet("Leads HMM Viterbi by ~1.5 days on transitions (63.2% detected in advance). PELT offline/weekly + BOCPD online/per-bar; HMM as cross-check."),
 head("6. SHAP Explainability",2),
 bullet("KernelExplainer on the HMM/XGBoost posterior — log WHICH features drive each signal (non-negotiable for a high-consequence, auditable system)."),
 head("7. Hurst Calibrated Thresholds",2),
 bullet("H<0.45 = range/mean-reversion; H>0.55 = trend/momentum. Gate direction logic on it, don't just report H."),
 head("8. Honest Bug Patterns (avoid)",2),
 bullet("GARCH never falls back to invented values on fit failure (fail the signal). Watch lookahead leakage, dead strategy paths, single-bar edge that dies in walk-forward."),
]

st,d=req("PATCH",f"/blocks/{PAGE}/children",{"children":B})
print("append:",st, "blocks:",len(B))
# verify
st2,d2=req("GET",f"/blocks/{PAGE}/children?page_size=100")
bl=d2.get("results",[]) if st2<400 else []
print("total blocks:",len(bl))
