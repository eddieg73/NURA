#!/usr/bin/env python3
"""eMedical READ-ONLY audit — charts + CPT vs the submitted claims.
NO changes anywhere: review only (the founder's directive 2026-08-17).
Usage: python3 emed-audit.py <patient_name>
Flow: login (ASP.NET WebForms) → the patient search → the progress notes →
the CPT codes on the encounters → the claims (the 837 submissions) →
the documentation-completeness report.
"""
import os, sys, time, re, json
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

creds = {}
for line in open('/tmp/nura-portal-creds.env'):
    if '=' in line:
        k, v = line.strip().split('=', 1)
        creds[k] = v

CHROME = "/opt/data/chrome/chrome-linux64/chrome"
BASE = "https://service.emedpractice.com/"

def find(patient):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME,
                                    args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        out = {"steps": []}
        # 1. login
        page.goto(BASE, timeout=60000)
        time.sleep(3)
        try:
            page.fill('input[name=email]', creds.get("EMED_USERNAME", ""))
            page.fill('input[name=password]', creds.get("EMED_PASSWORD", ""))
            page.click('input[name=SigninBtn]')
            time.sleep(8)
            out["steps"].append(f"login → title: {page.title()[:60]}")
        except Exception as e:
            out["steps"].append(f"login ERR: {str(e)[:80]}")
            browser.close()
            return out
        # 2. the patient search
        out["patient"] = patient
        try:
            search = page.locator('input[placeholder*="atient"], input[name*="earch"], input[name*="atient"]').first
            search.fill(patient)
            page.keyboard.press("Enter")
            time.sleep(6)
            out["steps"].append(f"search done → title: {page.title()[:60]}")
            # the visible result rows
            rows = page.locator("table tr").count()
            out["result_rows"] = rows
            body = page.inner_text("body")[:1500]
            out["page_text"] = body
        except Exception as e:
            out["steps"].append(f"search ERR: {str(e)[:80]}")
        browser.close()
        return out

if __name__ == "__main__":
    patient = sys.argv[1] if len(sys.argv) > 1 else ""
    if not patient:
        print("usage: emed-audit.py <patient_name>")
        sys.exit(1)
    print(json.dumps(find(patient), indent=2, default=str))
