#!/usr/bin/env python3
"""THE FREE-MEDICAL-APIs MCP SERVER — the keyless-lanes: NPPES · RxNorm · MedlinePlus · ClinicalTrials!
The zero-cost clinical-data surface (all verified 200!) — the FastMCP-stdio-lane."""
import json, urllib.request, urllib.parse

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode()[:1500]
    except Exception as e:
        return f"ERR: {str(e)[:60]}"

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read().decode()[:1500]
    except Exception as e:
        return f"ERR: {str(e)[:60]}"

try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("free-medical")

    @mcp.tool()
    def nppes_lookup(npi: str) -> str:
        """Look up a provider in the CMS NPPES registry (the free-official!)."""
        return get(f"https://npiregistry.cms.hhs.gov/api/?version=2.1&number={npi}")

    @mcp.tool()
    def rxnorm_lookup(drug: str) -> str:
        """Resolve a drug name to its RxNorm RxCUI (the free-official!)."""
        return get(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={urllib.parse.quote(drug)}")

    @mcp.tool()
    def rxnorm_interactions(rxcui: str) -> str:
        """Check drug-drug interactions for an RxCUI (the free-official!)."""
        return get(f"https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui={rxcui}")

    @mcp.tool()
    def medlineplus_lookup(icd10: str) -> str:
        """Get the patient-education page for an ICD-10 code (the free-official!)."""
        return get(f"https://connect.medlineplus.gov/service?mainSearchCriteria.v.c={icd10}&mainSearchCriteria.v.cs=2.16.840.1.113883.6.90")

    @mcp.tool()
    def clinicaltrials_search(term: str) -> str:
        """Search ClinicalTrials.gov for studies (the free-official!)."""
        return get(f"https://clinicaltrials.gov/api/v2/studies?query.term={urllib.parse.quote(term)}&pageSize=5")

    mcp.run(transport="stdio")
except ImportError:
    for line in __import__("sys").stdin:
        try:
            req = json.loads(line)
            if req.get("method") == "tools/list":
                print(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), "result": {"tools": [
                    {"name": "nppes_lookup", "description": "CMS NPPES provider lookup", "inputSchema": {"type": "object", "properties": {"npi": {"type": "string"}}}},
                    {"name": "rxnorm_lookup", "description": "RxNorm drug to RxCUI", "inputSchema": {"type": "object", "properties": {"drug": {"type": "string"}}}},
                    {"name": "medlineplus_lookup", "description": "ICD-10 to patient education", "inputSchema": {"type": "object", "properties": {"icd10": {"type": "string"}}}},
                    {"name": "clinicaltrials_search", "description": "ClinicalTrials.gov search", "inputSchema": {"type": "object", "properties": {"term": {"type": "string"}}}},
                ]}}), flush=True)
            elif req.get("method") == "tools/call":
                name = req["params"].get("name")
                args = req["params"].get("arguments", {})
                fn = {"nppes_lookup": lambda: nppes_lookup(args.get("npi", "")),
                      "rxnorm_lookup": lambda: rxnorm_lookup(args.get("drug", "")),
                      "medlineplus_lookup": lambda: medlineplus_lookup(args.get("icd10", "")),
                      "clinicaltrials_search": lambda: clinicaltrials_search(args.get("term", ""))}.get(name, lambda: "unknown")
                print(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), "result": {"content": [{"type": "text", "text": fn()}]}}), flush=True)
        except Exception:
            pass
