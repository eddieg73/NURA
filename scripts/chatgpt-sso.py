#!/usr/bin/env python3
"""ChatGPT login via the Google SSO (the Continue with Google button)."""
import os, sys, time, json
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

CHROME = "/opt/data/chrome/chrome-linux64/chrome"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME,
                                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36",
                              viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto("https://chatgpt.com/auth/login", timeout=60000)
    time.sleep(4)
    # the Google SSO button
    try:
        btn = page.locator('button:has-text("Continue with Google"), div:has-text("Continue with Google")').first
        btn.click(timeout=10000)
        time.sleep(5)
        print("GOOGLE clicked →", page.title()[:60], "|", page.url[:80])
    except Exception as e:
        print("google btn:", str(e)[:60])
        # the fallback: the direct Google auth URL
        page.goto("https://chatgpt.com/auth/login?screen_hint=signup&sso=google", timeout=60000)
        time.sleep(5)
        print("direct google →", page.title()[:60])
    # the account chooser / the password screens — the founder drives the MFA
    print("WAITING for the Google flow (the founder's MFA)...")
    for i in range(24):
        time.sleep(5)
        t = page.title()
        u = page.url[:80]
        print(f"wait {i+1}: {t[:50]} | {u}")
        if "chatgpt" in u.lower() and "auth" not in u.lower():
            print("LANDED on ChatGPT")
            break
    cookies = ctx.cookies()
    open("/opt/data/chatgpt-cookies.json", "w").write(json.dumps(cookies))
    os.chmod("/opt/data/chatgpt-cookies.json", 0o600)
    print("SAVED %d cookies | FINAL: %s" % (len(cookies), page.url[:100]))
    browser.close()
