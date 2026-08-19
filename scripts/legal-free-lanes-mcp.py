#!/usr/bin/env python3
"""MCP stdio server — NURA LEGAL/FREE LANES (2026-08-02, verified live).
Tools: ecfr_titles · ecfr_part · fl_admin_rule · fl_doh_lookup · myflcourt
Zero keys. stdio JSON-RPC MCP (initialize / tools/list / tools/call).
"""
import json
import re
import sys
import urllib.request
import urllib.parse

UA = {"User-Agent": "NURA-Hermes/1.0 (Nuratech.ai)"}

TOOLS = [
    {"name": "ecfr_titles", "description": "eCFR title list (find title/part numbers)",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "ecfr_part", "description": "eCFR full text of a title part (XML -> text)",
     "inputSchema": {"type": "object", "properties": {"title": {"type": "integer"}, "part": {"type": "integer"}}, "required": ["title", "part"]}},
    {"name": "fl_admin_rule", "description": "Florida Administrative Code rule text (e.g. 64J-1.001)",
     "inputSchema": {"type": "object", "properties": {"rule": {"type": "string"}}, "required": ["rule"]}},
    {"name": "fl_doh_lookup", "description": "FL DOH MQA provider license lookup (link + guidance)",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "myflcourt", "description": "MyFLCourtAccess FL state docket search (link + guidance)",
     "inputSchema": {"type": "object", "properties": {}}},
]

def fetch(url, maxbytes=30000, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(maxbytes).decode(errors="ignore")

def strip_html(h):
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<style.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    h = re.sub(r"\s+", " ", h)
    return h.strip()

def call_tool(name, args):
    try:
        if name == "ecfr_titles":
            d = json.loads(fetch("https://www.ecfr.gov/api/versioner/v1/titles.json"))
            return {"source": "eCFR", "result": [{"number": t.get("number"), "name": t.get("name")} for t in d.get("titles", [])][:50]}
        if name == "ecfr_part":
            t = int(args.get("title", 21)); p = int(args.get("part", 11))
            try:
                data = fetch(f"https://www.ecfr.gov/api/versioner/v1/structure/current/title-{t}.json?part={p}")
                return {"source": "eCFR", "title": t, "part": p, "result": data[:12000]}
            except Exception:
                data = fetch(f"https://www.ecfr.gov/api/versioner/v1/full/current/title-{t}.xml", maxbytes=30000)
                return {"source": "eCFR (full-title slice)", "title": t, "part": p, "result": strip_html(data)[:12000]}
        if name == "fl_admin_rule":
            rule = urllib.parse.quote(args.get("rule", ""))
            data = fetch(f"https://www.flrules.org/gateway/ruleno.asp?id={rule}")
            return {"source": "FL Admin Code", "rule": args.get("rule"), "result": strip_html(data)[:12000]}
        if name == "fl_doh_lookup":
            return {"source": "FL DOH MQA", "result": "Lookup at https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders (search by profession + name; FL-specific license verification)."}
        if name == "myflcourt":
            return {"source": "MyFLCourtAccess", "result": "Free FL state-court docket search at https://www.myflcourtaccess.com/ (civil/criminal/traffic by name or case number)."}
        return {"error": f"unknown tool {name}"}
    except Exception as e:
        return {"error": f"{name}: {type(e).__name__}: {e}"}

def main():
    for line in sys.stdin:
        try:
            msg = json.loads(line)
        except Exception:
            continue
        mid = msg.get("id"); method = msg.get("method"); params = msg.get("params") or {}
        if method == "initialize":
            out = {"protocolVersion": params.get("protocolVersion", "2024-11-05"),
                   "capabilities": {"tools": {}}, "serverInfo": {"name": "legal-free-lanes", "version": "1.0.0"}}
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
