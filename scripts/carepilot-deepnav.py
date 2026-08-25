#!/usr/bin/env python3
"""The CarePilot deep nav — the login, the dump the FULL nav, the walk every link looking for the text bots."""
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
    for attempt in range(3):
        try:
            page.goto("https://carepilot.nuratech.ai", timeout=90, wait_until="domcontentloaded")
            break
        except Exception:
            time.sleep(5)
    time.sleep(6)
    try:
        page.fill("input[name='username']", creds.get("CAREPILOT_USERNAME", ""))
        time.sleep(1.5)
        page.fill("input[type='password']", creds.get("CAREPILOT_PASSWORD", ""))
        time.sleep(2)
        page.click("button[type='submit']")
        time.sleep(9)
    except Exception as e:
        print("login fail:", str(e)[:80])
    print("url:", page.url[:100])
    # The EVERY nav link with the href
    links = page.eval_on_selector_all("a", "els => els.map(e => ({t:(e.innerText||'').trim().slice(0,50), h:e.href.slice(0,110)}))")
    seen = {}
    for l in links:
        key = l["t"] or l["h"]
        if key and key not in seen:
            seen[key] = l["h"]
    print(f"nav links ({len(seen)}):")
    for t, h in seen.items():
        print(f"- {t} → {h}")
    browser.close()
print("session closed")
