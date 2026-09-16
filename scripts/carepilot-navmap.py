#!/usr/bin/env python3
"""The CarePilot post-login nav map — the list EVERY link + the find the RPA section."""
import time

ENV = "/opt/data/profiles/nura/.env"
creds = {}
for l in open(ENV):
    if l.startswith("CAREPILOT_"):
        k, v = l.split("=", 1)
        creds[k.strip()] = v.strip().strip('"')

from playwright.sync_api import sync_playwright

CHROME = "/opt/data/chrome/chrome-linux64/chrome"
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True, args=["--no-sandbox"])
    page = browser.new_page()
    page.goto("https://carepilot.nuratech.ai", timeout=90, wait_until="domcontentloaded")
    time.sleep(6)
    page.fill("input[name='username']", creds.get("CAREPILOT_USERNAME", ""))
    time.sleep(1.5)
    page.fill("input[type='password']", creds.get("CAREPILOT_PASSWORD", ""))
    time.sleep(2)
    page.click("button[type='submit']")
    time.sleep(8)
    print("url:", page.url[:100])
    links = page.eval_on_selector_all("a", "els => els.map(e => (e.innerText || '').trim().slice(0,50))")
    seen = []
    for l in links:
        if l and l not in seen:
            seen.append(l)
    print("ALL NAV LINKS:")
    for l in seen[:40]:
        print("-", l)
    # The the RPA-ish click attempt by the text
    for kw in ["Automation", "RPA", "Bots", "Workflows", "Flows", "Campaign", "Text"]:
        try:
            page.click(f"a:has-text('{kw}')", timeout=4000)
            time.sleep(5)
            print(f"--- CLICKED {kw} → {page.url[:100]} ---")
            print(page.inner_text("body")[:800])
            break
        except Exception:
            continue
    browser.close()
print("session closed")
