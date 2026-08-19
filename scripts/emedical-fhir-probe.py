#!/usr/bin/env python3
"""eMedical FHIR client registration probe: login, open registration form, dump fields."""
import sys, time, re, json, os
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

creds = {}
for line in open("/tmp/nura-portal-creds.env"):
    k, v = line.strip().split("=", 1); creds[k] = v
CHROME = "/opt/data/chrome/chrome-linux64/chrome"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=CHROME, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36")
    page = ctx.new_page()
    # login page
    page.goto("https://service.emedpractice.com/", timeout=45000, wait_until="domcontentloaded")
    time.sleep(4)
    print("landed title:", page.title())
    # find username/password fields
    for sel in ["input[type=text]", "input[name*=ser]", "input[name*=mail]", "input[name*=ogin]", "input[id*=ser]", "input[id*=ogin]", "input[id*=mail]"]:
        try:
            page.fill(sel, creds["EMED_USERNAME"]); print("username filled via", sel); break
        except Exception: pass
    for sel in ["input[type=password]", "input[name*=ass]", "input[id*=ass]"]:
        try:
            page.fill(sel, creds["EMED_PASSWORD"]); print("password filled via", sel); break
        except Exception: pass
    for el in page.query_selector_all("button, input[type=submit], a"):
        t = (el.inner_text() or "").strip().lower()
        if t in ("login", "sign in", "log in", "submit", "continue") or (el.get_attribute("type") == "submit"):
            try:
                el.click(); print("clicked:", t or el.get_attribute("type")); break
            except Exception as e: print("click fail", e)
    time.sleep(8)
    print("after login title:", page.title())
    # navigate to FHIR registration
    try:
        page.goto("https://service.emedpractice.com/admin/fhirclientregistration.aspx", timeout=45000, wait_until="domcontentloaded")
        time.sleep(5)
        print("reg title:", page.title())
        fields = page.eval_on_selector_all("input,select,textarea", "els => els.map(e => ({tag:e.tagName, type:e.type||'', name:e.name||'', id:e.id||'', placeholder:e.placeholder||''}))")
        for f in fields: print("FIELD:", f)
        body = page.inner_text("body")
        print("BODY sample:", body[:800])
    except Exception as e:
        print("reg nav err:", str(e)[:200])
    b.close()
