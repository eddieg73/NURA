#!/usr/bin/env python3
"""SAF Scanner — FXAlexG Set & Forget Sunday scanner (decision support only, NOT a bot).
Pulls weekly+daily candles from Yahoo Finance (free, no key) and checks:
  TF sync (weekly vs daily trend via structure) · weekly engulfing · AOI touch count proxy.
Usage: python3 saf-scanner.py [--json]
"""
import json, sys, time, urllib.request

PAIRS = ["CADJPY=X", "EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "GBPJPY=X",
         "EURGBP=X", "USDCHF=X", "NZDUSD=X", "EURAUD=X"]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}

def fetch(symbol, interval, rng):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={rng}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.loads(r.read())
    res = d["chart"]["result"][0]
    ts = res.get("timestamp", [])
    q = res["indicators"]["quote"][0]
    closes, highs, lows = q["close"], q["high"], q["low"]
    return [(t, c, h, l) for t, c, h, l in zip(ts, closes, highs, lows) if c is not None]

def structure(candles, n=6):
    """HH/HL bullish, LH/LL bearish over last n candles (simplified)."""
    if len(candles) < n + 1:
        return None, []
    seg = candles[-n:]
    highs = [c[2] for c in seg]
    lows = [c[3] for c in seg]
    hh = highs[-1] > highs[-2] > highs[-3]
    hl = lows[-1] > lows[-2] > lows[-3]
    lh = highs[-1] < highs[-2] < highs[-3]
    ll = lows[-1] < lows[-2] < lows[-3]
    if hh and hl:
        return "bullish", seg
    if lh and ll:
        return "bearish", seg
    return "mixed", seg

def engulfing(candles):
    """Big bullish/bearish engulfing on last closed candle."""
    if len(candles) < 3:
        return None
    a, b = candles[-3], candles[-2]
    range_a = abs(a[2] - a[3]) or 1e-9
    if b[2] > a[2] and b[3] < a[3] and (b[2] - b[3]) > 1.2 * range_a:
        return "bullish"
    if b[2] < a[2] and b[3] > a[3] and (b[3] - b[2]) > 1.2 * range_a:
        return "bearish"
    return None

def touches(candles, k=3):
    """Proxy for AOI validation: count closes near the last swing low/high (3+ touches)."""
    if len(candles) < 12:
        return 0
    last = candles[-1]
    lo, hi = last[3], last[2]
    span = (hi - lo) or 1e-9
    near_lo = sum(1 for c in candles[-12:] if abs(c[3] - lo) / span < 0.08)
    near_hi = sum(1 for c in candles[-12:] if abs(c[2] - hi) / span < 0.08)
    return max(near_lo, near_hi)

def main():
    out = []
    for sym in PAIRS:
        try:
            wk = fetch(sym, "1wk", "1y")
            dy = fetch(sym, "1d", "3mo")
        except Exception as e:
            out.append({"pair": sym, "error": str(e)[:60]})
            continue
        w_trend, _ = structure(wk)
        d_trend, _ = structure(dy)
        eng = engulfing(wk)
        tch = touches(wk)
        sync = "SYNC" if (w_trend == d_trend and w_trend != "mixed") else ("CONFLICT" if w_trend != "mixed" and d_trend != "mixed" else "mixed")
        close = wk[-1][1] if wk else None
        out.append({"pair": sym, "close": round(close, 4) if close else None,
                    "weekly": w_trend, "daily": d_trend, "sync": sync,
                    "engulfing": eng, "aoi_touches": tch})
        time.sleep(0.3)
    if "--json" in sys.argv:
        print(json.dumps(out, indent=1))
        return
    print("=== SAF SUNDAY SCAN (decision support — verify on real charts) ===")
    for r in out:
        if "error" in r:
            print(f"{r['pair']}: ERR {r['error']}")
            continue
        flag = "CANDIDATE" if r["sync"] == "SYNC" and r["aoi_touches"] >= 3 else ""
        print(f"{r['pair']:12} close={r['close']:<10} W={r['weekly']:<8} D={r['daily']:<8} "
              f"{r['sync']:<9} engulf={str(r['engulfing']):<8} touches={r['aoi_touches']} {flag}")

if __name__ == "__main__":
    main()
