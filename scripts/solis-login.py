#!/usr/bin/env python3
"""Solis login via playwright + system chrome binary (browser tool is version-mismatched)."""
import os, sys, time, re
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

creds = {}
for line in open('/tmp/nura-portal-creds.env'):
    k, v = line.strip().split('=', 1)
    creds[k] = v

CHROME = "/opt/data/chrome/chrome-linux64/chrome"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME,
                                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36")
    page.goto("https://solis.ensuredatasolutions.com/Login", timeout=45000, wait_until="domcontentloaded")
    time.sleep(4)
    # DXR form: find text + password inputs
    inputs = page.eval_on_selector_all("input", "els => els.map(e => ({t: e.type, n: e.name, id: e.id, cls: (e.className||'').slice(0,60)}))")
    print("inputs:", inputs)
    txt = page.query_selector("input[type=text], input[type=email]")
    pwd = page.query_selector("input[type=password]")
    if not (txt and pwd):
        print("FORM NOT FOUND"); browser.close(); sys.exit(1)
    txt.fill(creds["ENSURE_USERNAME"])
    pwd.fill(creds["ENSURE_PASSWORD"])
    time.sleep(1)
    # try the login button: DXR button or any button containing 'Log'
    btn = None
    for sel in ["button", "a.dx-button", ".dx-button", "input[type=submit]"]:
        for b in page.query_selector_all(sel):
            t = (b.inner_text() or "").strip()
            if re.search(r'log\s*in|sign\s*in|login', t, re.I):
                btn = b; break
        if btn: break
    if not btn:
        print("BUTTON NOT FOUND — pressing Enter in password field")
        pwd.press("Enter")
    else:
        print("clicking:", (btn.inner_text() or "")[:30])
        btn.click()
    time.sleep(8)
    print("URL:", page.url)
    print("TITLE:", page.title())
    body = page.inner_text("body")[:400]
    print("BODY:", body)
    page.screenshot(path="/tmp/solis-after-login.png")
    browser.close()
