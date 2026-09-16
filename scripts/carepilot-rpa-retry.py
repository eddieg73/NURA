#!/usr/bin/env python3
"""The CarePilot RPA review — the retry with the relaxed loading + the longer waits."""
import json, time

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
    try:
        page.goto("https://carepilot.nuratech.ai", timeout=90, wait_until="domcontentloaded")
    except Exception as e:
        print("goto:", str(e)[:80])
    time.sleep(6)
    print("url:", page.url[:120])
    print("title:", page.title()[:80])
    txt = page.inner_text("body")[:400]
    print("body:", txt[:400])
    # The try the login fill
    try:
        for sel in ["input[type='email']", "input[name='email']", "input[name='username']", "input[type='text']"]:
            try:
                page.fill(sel, creds.get("CAREPILOT_USERNAME", ""), timeout=4000)
                print("filled user via", sel)
                break
            except Exception:
                continue
        time.sleep(1.5)
        for sel in ["input[type='password']"]:
            try:
                page.fill(sel, creds.get("CAREPILOT_PASSWORD", ""), timeout=4000)
                print("filled pass")
                break
            except Exception:
                continue
        time.sleep(2)
        for sel in ["button[type='submit']", "button:has-text('Sign')", "button:has-text('Log')"]:
            try:
                page.click(sel, timeout=4000)
                print("clicked", sel)
                break
            except Exception:
                continue
        time.sleep(8)
        print("post-login url:", page.url[:120])
        links = page.eval_on_selector_all("a", "els => els.map(e => e.innerText.trim().slice(0,40) + ' | ' + e.href.slice(0,80))")
        rpa = [l for l in links if any(k in l.lower() for k in ["autom", "rpa", "bot", "workflow", "process", "campaign"])]
        print("RPA links:", rpa[:10])
        if rpa:
            # The click the first RPA-ish link
            try:
                page.click(f"a:has-text('{rpa[0].split(' | ')[0].strip()[:20]}')", timeout=5000)
                time.sleep(5)
                print("RPA PAGE BODY:", page.inner_text("body")[:900])
            except Exception as e:
                print("click fail:", str(e)[:60])
    except Exception as e:
        print("login flow fail:", str(e)[:80])
    browser.close()
print("session closed")
