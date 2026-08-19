#!/usr/bin/env python3
"""Solis explorer: login, crawl every nav section, save pages + cookies (0600)."""
import os, sys, time, re, json
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

creds = {}
for line in open('/tmp/nura-portal-creds.env'):
    k, v = line.strip().split('=', 1)
    creds[k] = v

OUT = "/tmp/solis-pages"
os.makedirs(OUT, exist_ok=True)
CHROME = "/opt/data/chrome/chrome-linux64/chrome"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=CHROME,
                                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36")
    page = ctx.new_page()
    page.goto("https://solis.ensuredatasolutions.com/Login", timeout=45000, wait_until="domcontentloaded")
    time.sleep(4)
    page.fill("input[name=Username]", creds["ENSURE_USERNAME"])
    page.fill("input[name=Password]", creds["ENSURE_PASSWORD"])
    clicked = False
    for b in page.query_selector_all("button, a.dx-button, .dx-button"):
        t = (b.inner_text() or "").strip()
        if re.search(r'log\s*in', t, re.I):
            b.click(); clicked = True; break
    if not clicked:
        page.keyboard.press("Enter")
    time.sleep(8)
    print("TITLE:", page.title())
    # save cookies
    cookies = ctx.cookies()
    with open("/tmp/solis-cookies.json", "w") as f:
        json.dump(cookies, f)
    os.chmod("/tmp/solis-cookies.json", 0o600)
    print("cookies saved:", len(cookies))
    # crawl nav sections
    sections = {}
    for a in page.query_selector_all("a"):
        t = (a.inner_text() or "").strip()
        h = a.get_attribute("href") or ""
        if t and h and not h.startswith("#") and t in ["Home","Membership","Hospitalization","Referrals","Coding","Rx","Claims","Revenue"]:
            sections.setdefault(t, h)
    print("NAV:", json.dumps(sections))
    for name, href in sections.items():
        try:
            page.goto("https://solis.ensuredatasolutions.com" + href if href.startswith("/") else href, timeout=40000, wait_until="domcontentloaded")
            time.sleep(4)
            body = page.inner_text("body")
            html = page.content()
            with open(f"{OUT}/{name.replace('/','_')}.html", "w") as f:
                f.write(html)
            # sub-nav links on this page
            subs = sorted(set((a.inner_text() or "").strip() for a in page.query_selector_all("a") if (a.inner_text() or "").strip() and len((a.inner_text() or "").strip()) < 40))[:20]
            print(f"=== {name} ({len(html)}b) subnav: {subs[:12]}")
        except Exception as e:
            print(f"{name}: FAIL {e}")
    page.screenshot(path="/tmp/solis-home.png")
    browser.close()
print("DONE")
