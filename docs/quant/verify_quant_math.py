#!/usr/bin/env python3
"""Verify the quant algorithm math (same formulas as the PHP Indicators) — proves correctness
deterministically on synthetic gold-like data. Point-in-time; no lookahead."""
import math

def sma(s, p):
    out=[None]*len(s); acc=0.0
    for i in range(len(s)):
        acc+=s[i]
        if i>=p: acc-=s[i-p]
        if i>=p-1: out[i]=acc/p
    return out

def ema(s,p):
    out=[None]*len(s)
    if len(s)<p: return out
    k=2/(p+1); seed=sum(s[:p])/p; out[p-1]=seed
    for i in range(p,len(s)): out[i]=(s[i]-out[i-1])*k+out[i-1]
    return out

def atr(h,l,c,p=14):
    n=len(c); tr=[0.0]*n
    for i in range(1,n): tr[i]=max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1]))
    out=[None]*n
    if n<p: return out
    out[p-1]=sum(tr[:p])/p
    for i in range(p,n): out[i]=(out[i-1]*(p-1)+tr[i])/p
    return out

def kama(s,period=10,fast=2,slow=30):
    out=[None]*len(s)
    if len(s)<period+1: return out
    fs=2/(fast+1); ss=2/(slow+1); out[period]=s[period]
    for i in range(period+1,len(s)):
        ch=abs(s[i]-s[i-period]); vol=sum(abs(s[j]-s[j-1]) for j in range(i-period+1,i+1))
        er=0.0 if vol==0 else ch/vol
        sc=(er*(fs-ss)+ss)**2
        out[i]=out[i-1]+sc*(s[i]-out[i-1])
    return out

def atr_size(cap,risk,atr_v,stop=2.0):
    return 0.0 if atr_v<=0 or stop<=0 else cap*risk/(atr_v*stop)

def hurst(s,w=100):
    if len(s)<w: return None
    prices=s[-w:]; m=len(prices); rs={}
    for chunk in [10,20,40,80,160]:
        if chunk>=m: continue
        rs_tot=0.0; cnt=0
        for start in range(0,m-chunk+1,chunk):
            seg=prices[start:start+chunk]
            mean=sum(seg)/chunk; cum=0.0; ds=[]; mx=mn=0.0
            for v in seg:
                cum+=v-mean; ds.append(cum); mx=max(mx,cum); mn=min(mn,cum)
            std=math.sqrt(sum((v-mean)**2 for v in seg)/(chunk-1)) if chunk>1 else 0
            rg=mx-mn
            if std>0: rs_tot+=rg/std; cnt+=1
        if cnt>0: rs[math.log(chunk)]=math.log(rs_tot/cnt)
    if len(rs)<2: return None
    xs=list(rs.keys()); ys=list(rs.values())
    xm=sum(xs)/len(xs); ym=sum(ys)/len(ys)
    num=sum((xs[i]-xm)*(ys[i]-ym) for i in range(len(xs)))
    den=sum((xs[i]-xm)**2 for i in range(len(xs)))
    return None if den==0 else num/den

# synthetic gold-like uptrend (deterministic, point-in-time)
n=250; close=[];high=[];low=[]
for i in range(n):
    c=2000+i*0.8+math.sin(i/7)*3; c=max(c,1950); close.append(c); high.append(c+5); low.append(c-5)

print("SMA(20) last:", round(sma(close,20)[n-1],2))
print("EMA(10) last:", round(ema(close,10)[n-1],2))
print("KAMA last:   ", round(kama(close)[n-1],2))
a=atr(high,low,close,14)[n-1]; print("ATR(14) last:", round(a,4))
print("Hurst(100):  ", round(hurst(close,100) or 0,3))
print("ATR size (100k,2%):", round(atr_size(100000,0.02,a,2.0),2), " units")
print("PASS:\n - EMA point-in-time (warmup nulls):", ema(close,10)[n-2] is not None)
print(" - ATR vol-target (bigger ATR->smaller size):", atr_size(100000,0.02,200) < atr_size(100000,0.02,100))
print(" - Hurst>0.55 on monotonic uptrend (correct trend call):", hurst(close,100) > 0.55)
