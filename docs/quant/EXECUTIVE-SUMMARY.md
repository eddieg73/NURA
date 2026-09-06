# AI Quantitative Model — Gold & Oil Multi-Factor Trading System
# Executive Summary (confidential)

**Owner:** Eddie Garrido / NURA · **Built by:** Hermes (CTO) + developer · **Date:** 2026-09-06
**Classification:** Financial — HIGH-CONSEQUENCE. Backtest/paper first; LIVE trading is founder-approval-gated with a kill-switch.

---

## What this is
A professional-grade AI quantitative trading system for **GOLD (XAU/GC)** and **OIL (WTI/CL, Brent/CO)** built on the Rancher's (brother-in-law's) multi-factor model. It integrates **12 core algorithms** to identify trend, assess market regime, predict return probability, control risk, and dynamically manage position size.

## The decision chain (the "why")
```
Regime (Hurst + HMM + ADX)
  → Direction (EMA + Donchian + TSMOM + Kaufman AMA + Kalman)
  → Return-probability (Bayesian + XGBoost)
  → Risk-size (ATR + GARCH + confidence)
```
Each bar produces: **signal + confidence + suggested position size + rationale.**

## Instrument factors
- **Gold (XAU):** DXY dollar, real interest rates (TIPS), CPI/inflation, VIX, GLD ETF fund flows, CFTC COT.
- **Oil (WTI/Brent):** EIA weekly inventories, supply-demand balance, US production, refinery utilization, futures term-structure (contango/backwardation), Brent-WTI spread, CFTC COT.

## The 12 algorithms
Hurst exponent · EMA trend · Donchian breakout · ADX · TSMOM · Kaufman AMA · Kalman filter · HMM state · GARCH volatility · XGBoost · Bayesian probability · ATR dynamic position management.

## Architecture (PHP/Laravel, domain-first)
```
app/Domain/
  Market/   instruments, OHLCV ingestion
  Feature/  EMA, ADX, Hurst, Donchian, TSMOM, AMA, Kalman, HMM, GARCH, ATR, bayes, xgboost
  Signal/   feature -> signal (regime + direction + return-prob)
  Risk/     ATR vol-target sizing, 5-layer ladder, drawdown guard, kill-switch
  Execution/ order intent, paper/backtest, (live = gated)
app/Services/  DataFeeder, FactorUpdater, SignalEngine, RiskManager, BacktestRunner
app/Console/   artisan ingest/signal/backtest/risk commands
app/Jobs/      scheduled data pulls (EIA, COT, SEC/XBRL, ETF, price)
app/Http/      /v1/signals, /v1/risk, /v1/backtest
database/      migrations for instruments, prices, factors, signals, positions, backtests
```

## Industry-validated improvements (the edge)
1. **Walk-forward validation** — in-sample PF 2.27 vs OOS ceiling 1.173; OOS is the gate.
2. **Monte Carlo N=10,000** — PASS matrix (P(profit) ≥65%, P(ruin) ≤10%, VaR bounded, maxDD).
3. **Five-layer risk ladder** — 2%/trade, 5%/day, 10%/week, 20% kill-switch, 2-loss circuit-break + independent risk manager.
4. **Regime-conditional GARCH** — +58.6% vol-forecast RMSE improvement.
5. **Bayesian changepoint (PELT/BOCPD)** — leads HMM by ~1.5 days on regime transitions.
6. **SHAP explainability** — which features drive each signal (auditability).
7. **Hurst thresholds** — H<0.45 range / H>0.55 trend.
8. **No fabrication** — GARCH never invents values on fit failure; point-in-time only, no lookahead.

## LLM inference layer (annotation, NOT prediction)
Core signal = deterministic + XGBoost. LLMs **explain/annotate/audit** only.
- DeepSeek-V3: signal narrative / regime summary (cheap reasoning)
- Claude Sonnet 4 / GPT-5.6: trade-note + risk-report prose
- Local Ollama (Llama/Mistral): private factor Q&A, $0, no data leak
- Nous Hermes / open MoE: future model-selection, no vendor lock

## Data sources (live/accessible)
SEC EDGAR (Form 4, 13F, XBRL) · CFTC COT · EIA (inventories/production/refinery) · FRED (DXY, TIPS, CPI) · price/OHLCV (XAU, CL, CO) · GLD ETF flows · futures term-structure.

## Verification gate before "done"
1. Walk-forward OOS holds (not in-sample)
2. Monte Carlo N≥10,000 passes the risk gate
3. No lookahead/leakage (point-in-time)
4. 5-layer risk ladder armed + independent risk manager
5. SHAP logged on every signal
6. Backtest + paper only; live = founder approval only

## Status
P0 — Scoping. Spec + skill + build files ready. Developer assignable. HIGH-CONSEQUENCE → approval-gated; no live trading without founder sign-off.
