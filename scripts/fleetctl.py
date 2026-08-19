#!/usr/bin/env python3
"""fleetctl — NURA fleet operations CLI (keyless local checks + DNS/endpoint audit).
Remote mutations go through the hostinger_api MCP (approval-gated per autonomous-infrastructure-ops).
Usage: fleetctl status | fleetctl dns | fleetctl endpoints | fleetctl help"""
import json, subprocess, sys, urllib.request

CORE_IP, AI_IP, EDGE_IP = "72.61.71.211", "72.60.163.140", "195.35.32.113"
SUBDOMAINS = ["nuratech.ai", "www.nuratech.ai", "n8n.nuratech.ai", "pay.nuratech.ai",
              "carepilot.nuratech.ai", "crm.nuratech.ai", "pacs.nuratech.ai", "viewer.nuratech.ai",
              "emr.nuratech.ai", "mirth.nuratech.ai", "chatwoot.nuratech.ai", "ai.nuratech.ai", "behive.nuratech.ai"]
EXPECTED = {"nuratech.ai": AI_IP, "www.nuratech.ai": AI_IP, "n8n.nuratech.ai": AI_IP,
            "pay.nuratech.ai": EDGE_IP, "carepilot.nuratech.ai": "cloudflare", "crm.nuratech.ai": "cloudflare"}
ENDPOINTS = [("n8n", "https://n8n.nuratech.ai/"), ("apex", "https://nuratech.ai/"), ("pay", "https://pay.nuratech.ai/"),
             ("carepilot", "https://carepilot.nuratech.ai/"), ("paperclip", "http://127.0.0.1:3100/api/health"),
             ("gateway", "http://127.0.0.1:8642/health"), ("qdrant", "http://127.0.0.1:6333/healthz")]

def status():
    print("== LOCAL HEALTH ==")
    for name, url in ENDPOINTS:
        try:
            code = subprocess.run(["curl", "-s", "-m", "5", "-o", "/dev/null", "-w", "%{http_code}", url],
                                  capture_output=True, text=True, timeout=10).stdout.strip()
            print(f"  {name}: {code}")
        except Exception as e:
            print(f"  {name}: ERR {str(e)[:40]}")

def dns():
    print("== DNS AUDIT (expected -> actual) ==")
    for h in SUBDOMAINS:
        ip = ""
        try:
            ip = subprocess.run(["getent", "hosts", h], capture_output=True, text=True, timeout=5).stdout.split()[0]
        except Exception:
            pass
        exp = EXPECTED.get(h, "pending")
        if exp == "cloudflare":
            verdict = "CF-OK" if ("2a06" in ip or "2.24" in ip or "104." in ip) else f"CHECK ({ip})"
        elif exp == "pending":
            verdict = "PENDING (no record yet)" if not ip else f"LIVE on {ip}"
        else:
            verdict = "MATCH" if ip == exp else f"MISMATCH (want {exp})"
        print(f"  {h}: {ip or 'NO RECORD'} — {verdict}")

def endpoints():
    print("== ENDPOINT SWEEP ==")
    for name, url in ENDPOINTS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "NURA-Hermes/1.0"}, method="GET")
            with urllib.request.urlopen(req, timeout=8) as r:
                print(f"  {name}: {r.status}")
        except Exception as e:
            print(f"  {name}: DOWN ({str(e)[:50]})")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "dns": dns, "endpoints": endpoints}.get(cmd, lambda: print(__doc__))()
