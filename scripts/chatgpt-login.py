#!/usr/bin/env python3
"""ChatGPT web login via the playwright + the system chrome.
Logs into chatgpt.com, persists the session cookies for the CLI lane.
The founder drives the MFA live.
"""
import os, sys, time, json
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

CHROME = "/opt/data/chrome/chrome-linux64/chrome"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False if os.environ.get("SHOW") else True,
                                executable_path=CHROME,
                                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
                              viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto("https://chatgpt.com/auth/login", timeout=60000)
    time.sleep(4)
    print("STEP: on the login page")
    print("TITLE:", page.title())
    # the email field or the Google button
    try:
        email = page.locator('input[type=email], input[name=email], input[autocomplete=username]').first
        email.fill(os.environ.get("OPENAI_EMAIL", ""))
        page.keyboard.press("Enter")
        time.sleep(4)
        print("email entered — the password/next screen")
    except Exception as e:
        print("email field:", str(e)[:60])
    # the MFA dance: the founder reads the code
    try:
        pw = page.locator('input[type=password]').first
        if pw.is_visible() and os.environ.get("OPENAI_PASSWORD"):
            pw.fill(os.environ["OPENAI_PASSWORD"])
            page.keyboard.press("Enter")
            time.sleep(4)
            print("password entered")
    except Exception:
        pass
    # the wait for the founder's MFA + the dashboard
    for i in range(12):
        time.sleep(5)
        t = page.title()
        print(f"wait {i+1}: {t[:60]}")
        if "ChatGPT" in t and "login" not in page.url.lower():
            break
    # the session save
    cookies = ctx.cookies()
    open("/opt/data/chatgpt-cookies.json", "w").write(json.dumps(cookies))
    os.chmod("/opt/data/chatgpt-cookies.json", 0o600)
    print("SAVED: /opt/data/chatgpt-cookies.json (%d cookies)" % len(cookies))
    print("FINAL URL:", page.url[:100])
    browser.close()
