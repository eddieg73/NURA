#!/usr/bin/env python3
"""The CarePilot login + the RPA text-bot review. The human-paced, the single session, the explicit logout."""
import json, os, subprocess, time

ENV = "/opt/data/profiles/nura/.env"
creds = {}
for l in open(ENV):
    if l.startswith("CAREPILOT_"):
        k, v = l.split("=", 1)
        creds[k.strip()] = v.strip().strip('"')

from playwright.sync_api import sync_playwright

CHROME = "/opt/data/chrome/chrome-linux64/chrome"
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page()
    # The login — the human-paced
    page.goto("https://carepilot.nuratech.ai", timeout=60)
    time.sleep(3)
    # The fill the creds if the login form shows
    for sel in ["input[type='email']", "input[name='email']", "input[name='username']", "input#email"]:
        try:
            page.fill(sel, creds.get("CAREPILOT_USERNAME", ""), timeout=5000)
            break
        except Exception:
            continue
    time.sleep(1.5)
    for sel in ["input[type='password']", "input[name='password']", "input#password"]:
        try:
            page.fill(sel, creds.get("CAREPILOT_PASSWORD", ""), timeout=5000)
            break
        except Exception:
            continue
    time.sleep(2)
    for sel in ["button[type='submit']", "button:has-text('Sign')", "button:has-text('Log')", "input[type='submit']"]:
        try:
            page.click(sel, timeout=5000)
            break
        except Exception:
            continue
    time.sleep(6)
    print("URL after login:", page.url[:100])
    # The hunt the RPA / automation nav
    links = page.eval_on_selector_all("a", "els => els.map(e => e.innerText + ' | ' + e.href)")
    rpa = [l for l in links if any(k in l.lower() for k in ["automation", "rpa", "bot", "workflow", "process"])]
    print("RPA-ish links:", rpa[:8])
    # The try the likely paths
    for path in ["/rpa", "/automation", "/bots", "/workflows", "/robotic-process-automation"]:
        try:
            page.goto(f"https://carepilot.nuratech.ai{path}", timeout=20)
            time.sleep(2)
            txt = page.inner_text("body")[:600]
            if "bot" in txt.lower() or "automation" in txt.lower():
                print(f"--- {path} ---")
                print(txt[:600])
                break
        except Exception:
            continue
    browser.close()
print("done — the session closed")
