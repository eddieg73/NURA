#!/usr/bin/env python3
"""MCP stdio server — NURA KNOWLEDGE LANES (2026-08-02, verified live).
Tools: edgar_submissions · openalex_search · europepmc_search · openmeteo_forecast
       · pubchem_property · crossref_search · coingecko_price
Zero keys. Protocol: stdio JSON-RPC (initialize / tools/list / tools/call).
"""
import json
import sys
import urllib.request
import urllib.parse

UA = {"User-Agent": "NURA-Hermes/1.0 (Nuratech.ai)"}

TOOLS = [
    {"name": "edgar_submissions", "description": "SEC EDGAR company submissions/filings by CIK",
     "inputSchema": {"type": "object", "properties": {"cik": {"type": "string"}}, "required": ["cik"]}},
    {"name": "openalex_search", "description": "OpenAlex research graph search",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "europepmc_search", "description": "Europe PMC full-text biomedical literature search",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "openmeteo_forecast", "description": "Open-Meteo weather forecast (lat/lon)",
     "inputSchema": {"type": "object", "properties": {"lat": {"type": "number"}, "lon": {"type": "number"}}, "required": ["lat", "lon"]}},
    {"name": "pubchem_property", "description": "PubChem compound properties by name",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "crossref_search", "description": "Crossref scholarly works search",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "coingecko_price", "description": "CoinGecko crypto price (ids comma-separated)",
     "inputSchema": {"type": "object", "properties": {"ids": {"type": "string"}}, "required": ["ids"]}},
]

def fetch(url, maxbytes=15000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read(maxbytes).decode(errors="ignore")

def call_tool(name, args):
    try:
        if name == "edgar_submissions":
            cik = str(args.get("cik", "")).zfill(10)
            data = fetch(f"https://data.sec.gov/submissions/CIK{cik}.json")
            return {"source": "SEC EDGAR", "cik": cik, "result": data[:12000]}
        if name == "openalex_search":
            q = urllib.parse.quote(args.get("query", ""))
            data = fetch(f"https://api.openalex.org/works?search={q}&per-page=3")
            return {"source": "OpenAlex", "query": args.get("query"), "result": data[:12000]}
        if name == "europepmc_search":
            q = urllib.parse.quote(args.get("query", ""))
            data = fetch(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={q}&format=json&pageSize=3")
            return {"source": "Europe PMC", "query": args.get("query"), "result": data[:12000]}
        if name == "openmeteo_forecast":
            lat, lon = float(args.get("lat")), float(args.get("lon"))
            data = fetch(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true")
            return {"source": "Open-Meteo", "result": data[:6000]}
        if name == "pubchem_property":
            n = urllib.parse.quote(args.get("name", ""))
            data = fetch(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{n}/property/MolecularFormula,CanonicalSMILES,IsomericSMILES,InChIKey/json")
            return {"source": "PubChem", "name": args.get("name"), "result": data[:6000]}
        if name == "crossref_search":
            q = urllib.parse.quote(args.get("query", ""))
            data = fetch(f"https://api.crossref.org/works?query={q}&rows=3")
            return {"source": "Crossref", "query": args.get("query"), "result": data[:12000]}
        if name == "coingecko_price":
            ids = urllib.parse.quote(args.get("ids", ""))
            data = fetch(f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd")
            return {"source": "CoinGecko", "result": data[:4000]}
        return {"error": f"unknown tool {name}"}
    except Exception as e:
        return {"error": f"{name}: {type(e).__name__}: {e}"}

def main():
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
                   "capabilities": {"tools": {}}, "serverInfo": {"name": "knowledge-free-lanes", "version": "1.0.0"}}
            print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": out}), flush=True)
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}), flush=True)
        elif method == "tools/call":
            result = call_tool(params.get("name"), params.get("arguments") or {})
            print(json.dumps({"jsonrpc": "2.0", "id": mid,
                              "result": {"content": [{"type": "text", "text": json.dumps(result)[:18000]}]}}), flush=True)
        elif method == "ping":
            print(json.dumps({"jsonrpc": "2.0", "id": mid, "result": {}}), flush=True)

if __name__ == "__main__":
    main()
