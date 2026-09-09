#!/usr/bin/env python3
"""Auth-only Ensure (Solis) portal smoke. Prints AUTH + URL (+ optional title). No PHI."""
import os, sys, time, re

CREDS = os.environ.get("ENSURE_CREDS_FILE", "/tmp/nura-portal-creds.env")
CHROME_CANDIDATES = [
    os.environ.get("ENSURE_CHROME", ""),
    "/root/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome",
    "/opt/data/chrome/chrome-linux64/chrome",
]
LOGIN_URL = "https://solis.ensuredatasolutions.com/Login"
TIMEOUT_MS = int(os.environ.get("ENSURE_SMOKE_TIMEOUT_MS", "120000"))

def load_creds(path):
    if not os.path.isfile(path):
        print("AUTH=BLOCKED")
        print("REASON=missing sealed creds")
        print("URL=")
        sys.exit(2)
    creds = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip().strip('"').strip("'")
    if not creds.get("ENSURE_USERNAME") or not creds.get("ENSURE_PASSWORD"):
        print("AUTH=BLOCKED")
        print("REASON=creds file missing ENSURE_USERNAME/ENSURE_PASSWORD keys")
        print("URL=")
        sys.exit(2)
    return creds

def pick_chrome():
    for pth in CHROME_CANDIDATES:
        if pth and os.path.isfile(pth) and os.access(pth, os.X_OK):
            return pth
    return None

def main():
    creds = load_creds(CREDS)
    chrome = pick_chrome()
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        launch_kwargs = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        }
        if chrome:
            launch_kwargs["executable_path"] = chrome
        try:
            browser = p.chromium.launch(**launch_kwargs)
        except Exception:
            try:
                browser = p.chromium.launch(headless=True, args=launch_kwargs["args"])
            except Exception as e2:
                print("AUTH=BLOCKED")
                print("REASON=browser launch failed: " + type(e2).__name__)
                print("URL=")
                sys.exit(3)

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
            )
        )
        try:
            page.goto(LOGIN_URL, timeout=min(TIMEOUT_MS, 60000), wait_until="domcontentloaded")
            time.sleep(3)
            txt = page.query_selector("input[name=Username], input[type=text], input[type=email]")
            pwd = page.query_selector("input[name=Password], input[type=password]")
            if not (txt and pwd):
                print("AUTH=FAILED")
                print("REASON=login form not found")
                print("URL=" + page.url)
                browser.close()
                sys.exit(1)
            txt.fill(creds["ENSURE_USERNAME"])
            pwd.fill(creds["ENSURE_PASSWORD"])
            time.sleep(0.5)
            btn = None
            for sel in ["button", "a.dx-button", ".dx-button", "input[type=submit]"]:
                for b in page.query_selector_all(sel):
                    t = (b.inner_text() or "").strip()
                    if re.search(r"log\s*in|sign\s*in|login", t, re.I):
                        btn = b
                        break
                if btn:
                    break
            if btn:
                btn.click()
            else:
                pwd.press("Enter")
            deadline = time.time() + (TIMEOUT_MS / 1000.0) - 10
            while time.time() < deadline:
                url = page.url
                if "Login" not in url:
                    break
                body_l = (page.inner_text("body") or "").lower()
                if "unauthorized" in body_l and "ip" in body_l:
                    print("AUTH=FAILED")
                    print("REASON=Unauthorized IP")
                    print("URL=" + url)
                    browser.close()
                    sys.exit(1)
                if "captcha" in body_l:
                    print("AUTH=FAILED")
                    print("REASON=captcha")
                    print("URL=" + url)
                    browser.close()
                    sys.exit(1)
                time.sleep(1)
            url = page.url
            title = ""
            try:
                title = page.title()
            except Exception:
                pass
            ok = "Login" not in url
            if not ok:
                body_l = (page.inner_text("body") or "").lower()
                reason = "login failed"
                if "unauthorized" in body_l and "ip" in body_l:
                    reason = "Unauthorized IP"
                elif "captcha" in body_l:
                    reason = "captcha"
                elif "invalid" in body_l or "incorrect" in body_l:
                    reason = "invalid credentials"
                print("AUTH=FAILED")
                print("REASON=" + reason)
                print("URL=" + url)
                if title:
                    print("TITLE=" + title[:80])
                browser.close()
                sys.exit(1)
            print("AUTH=OK")
            print("URL=" + url)
            if title:
                print("TITLE=" + title[:80])
            browser.close()
            sys.exit(0)
        except Exception as e:
            print("AUTH=FAILED")
            print("REASON=" + type(e).__name__)
            try:
                print("URL=" + page.url)
            except Exception:
                print("URL=")
            try:
                browser.close()
            except Exception:
                pass
            sys.exit(1)

if __name__ == "__main__":
    main()
