#!/usr/bin/env python3
"""Kaggle login via the playwright + the system chrome.
The email + the password → the session cookies → the upload lane.
"""
import os, sys, time, json
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

CHROME = "/opt/data/chrome/chrome-linux64/chrome"
EMAIL = os.environ.get("KAGGLE_EMAIL", "")
PASS = os.environ.get("KAGGLE_PASSWORD", "")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME,
                                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
                              viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto("https://www.kaggle.com/account/login", timeout=60000)
    # the reCAPTCHA "Checking your browser" — the wait for the clear
    for i in range(12):
        time.sleep(5)
        t = page.title()
        if "reCAPTCHA" not in t and "Checking" not in t:
            break
        print(f"recaptcha wait {i+1}...")
    time.sleep(3)
    print("TITLE:", page.title()[:60])
    # the Kaggle login form
    try:
        email = page.locator('input[name=email], input[type=email], input[autocomplete=username]').first
        email.fill(EMAIL)
        pw = page.locator('input[name=password], input[type=password]').first
        pw.fill(PASS)
        page.keyboard.press("Enter")
        time.sleep(10)
        print("login submitted →", page.title()[:60], "|", page.url[:80])
    except Exception as e:
        print("form ERR:", str(e)[:80])
    # the wait for the dashboard
    for i in range(6):
        time.sleep(5)
        u = page.url
        print(f"wait {i+1}: {page.title()[:50]} | {u[:70]}")
        if "login" not in u and "kaggle.com" in u:
            break
    cookies = ctx.cookies()
    open("/opt/data/kaggle-cookies.json", "w").write(json.dumps(cookies))
    os.chmod("/opt/data/kaggle-cookies.json", 0o600)
    print("SAVED %d cookies | FINAL: %s" % (len(cookies), page.url[:100]))
    browser.close()
