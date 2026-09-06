#!/usr/bin/env python3
"""Add the AI Quant Model project task + record to the CANONICAL Master Tasks board (d3ff0c00)."""
import os, json, sys, importlib.util, requests

def _token():
    ap = "/opt/data/profiles/nura/home/.config/notion/auth.json"
    if os.path.exists(ap):
        d = json.load(open(ap))
        if d:
            return next(iter(d.values()))
    raise SystemExit("no token")

TOKEN=_token(); VER="2022-06-28"; H={"Authorization":f"Bearer {TOKEN}","Notion-Version":VER,"Content-Type":"application/json"}
API="https://api.notion.com/v1"
DB="d3ff0c00-c629-43dc-b82c-06a28866fcb1"
def req(m,p,b=None,t=30):
    r=requests.request(m,API+p,headers=H,json=b,timeout=t); return r.status_code,r.json()
def _t(x): return [{"type":"text","text":{"content":x}}]

TASK=("Build the AI Quantitative Model (Gold/Oil multi-factor trading system) in PHP/Laravel — 12 algorithms, "
      "macro+micro factors, ATR/vol-targeted risk, backtest+paper first, LIVE = approval-gated. NUR-quant. "
      "Notion spec: AI Quantitative Model — Gold & Oil Multi-Factor Trading System. HIGH-CONSEQUENCE (financial), "
      "no live trading authority without founder sign-off.")

body={"parent":{"database_id":DB},"properties":{
    "Task":{"title":_t(TASK)},
    "Status":{"select":{"name":"Next"}},
    "Priority":{"select":{"name":"P1 — High"}},
    "Owner":{"rich_text":_t("Hermes")},
    "Source System":{"select":{"name":"Hermes"}},
    "Task Type":{"select":{"name":"Build"}},
}}
st,d=req("POST","/pages",body)
print("task status:",st)
print("id:",d.get("id"),"url:",(d.get("url") or "")[:70] if st<400 else d.get("message",d)[:200])
