#!/usr/bin/env python3
"""eMedical READ-ONLY practice + patient count (the Medisun clinics).
NO changes. Login → the Select Practice screen → the practice list →
the patient counts per practice.
"""
import os, sys, time, json
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

creds = {}
for line in open('/tmp/nura-portal-creds.env'):
    if '=' in line:
        k, v = line.strip().split('=', 1)
        creds[k] = v

CHROME = "/opt/data/chrome/chrome-linux64/chrome"
BASE = "https://service.emedpractice.com/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME,
                                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    out = {}
    page.goto(BASE, timeout=60000)
    time.sleep(3)
    page.fill('input[name=email]', creds.get("EMED_USERNAME", ""))
    page.fill('input[name=password]', creds.get("EMED_PASSWORD", ""))
    page.click('input[name=SigninBtn]')
    time.sleep(8)
    out["after_login_title"] = page.title()
    # the Select Practice screen: dump the visible options + any counts
    body = page.inner_text("body")
    out["select_practice_text"] = body[:2000]
    # the links/buttons (the practice entries)
    links = page.locator("a").all_inner_texts()[:30]
    out["links"] = [l.strip() for l in links if l.strip()][:20]
    browser.close()
    print(json.dumps(out, indent=2, default=str))
