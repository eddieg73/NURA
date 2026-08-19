#!/usr/bin/env python3
"""MCP stdio server — NURA FREE MEDICAL LANES (2026-08-02, verified live).
Tools: dailymed_label · rxnorm_lookup · clinicaltrials_search · clinvar_search
Zero keys. Protocol: stdio JSON-RPC (MCP initialize / tools/list / tools/call).
"""
import json
import sys
import urllib.request
import urllib.parse

UA = {"User-Agent": "NURA-Hermes/1.0"}

TOOLS = [
    {"name": "dailymed_label", "description": "Official FDA drug label (SPL) by drug name",
     "inputSchema": {"type": "object", "properties": {"drug": {"type": "string"}}, "required": ["drug"]}},
    {"name": "rxnorm_lookup", "description": "RxNorm drug code (rxcui) + names",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "clinicaltrials_search", "description": "ClinicalTrials.gov search (API v2)",
     "inputSchema": {"type": "object", "properties": {"term": {"type": "string"}, "size": {"type": "integer"}}, "required": ["term"]}},
    {"name": "clinvar_search", "description": "ClinVar variant search (eutils)",
     "inputSchema": {"type": "object", "properties": {"term": {"type": "string"}}, "required": ["term"]}},
]

def fetch(url, maxbytes=20000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read(maxbytes).decode(errors="ignore")

def call_tool(name, args):
    if name == "dailymed_label":
        drug = urllib.parse.quote(args.get("drug", ""))
        data = fetch(f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug}&pagesize=3")
        return {"source": "DailyMed (NLM)", "drug": args.get("drug"), "result": data[:15000]}
    if name == "rxnorm_lookup":
        q = urllib.parse.quote(args.get("name", ""))
        data = fetch(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={q}")
        return {"source": "RxNorm (NLM)", "name": args.get("name"), "result": data[:8000]}
    if name == "clinicaltrials_search":
        term = urllib.parse.quote(args.get("term", ""))
        size = min(int(args.get("size", 3)), 10)
        data = fetch(f"https://clinicaltrials.gov/api/v2/studies?query.term={term}&pageSize={size}")
        return {"source": "ClinicalTrials.gov API v2", "term": args.get("term"), "result": data[:15000]}
    if name == "clinvar_search":
        term = urllib.parse.quote(args.get("term", ""))
        data = fetch(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={term}&retmax=5&retmode=json")
        return {"source": "ClinVar (NCBI eutils)", "term": args.get("term"), "result": data[:8000]}
    return {"error": f"unknown tool {name}"}

def main():
    pending = {}
    for line in sys.stdin:
        try:
            msg = json.loads(line)
        except Exception:
            continue
        mid = msg.get("id")
        method = msg.get("method")
        params = msg.get("params") or {}
        if method == "initialize":
            out = {"protocolVersion": params.get("protocolVersion", "2024-11-05"),
                   "capabilities": {"tools": {}}, "serverInfo": {"name": "medical-free-lanes", "version": "1.0.0"}}
            print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": out}), flush=True)
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}), flush=True)
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            result = call_tool(name, args)
            print(json.dumps({"jsonrpc": "2.0", "id": mid,
                              "result": {"content": [{"type": "text", "text": json.dumps(result)[:18000]}]}}), flush=True)
        elif method == "ping":
            print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": {}}), flush=True)

if __name__ == "__main__":
    main()
