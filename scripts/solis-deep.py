#!/usr/bin/env python3
"""Solis deep crawl: open ☰ menu (full module tree), click representative tiles, capture text."""
import sys, time, re, json, os
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

creds = {}
for line in open('/tmp/nura-portal-creds.env'):
    k, v = line.strip().split('=', 1); creds[k] = v
CHROME = "/opt/data/chrome/chrome-linux64/chrome"
OUT = "/tmp/solis-pages"; os.makedirs(OUT, exist_ok=True)

def login(page):
    page.goto("https://solis.ensuredatasolutions.com/Login", timeout=45000, wait_until="domcontentloaded")
    time.sleep(4)
    page.fill("input[name=Username]", creds["ENSURE_USERNAME"])
    page.fill("input[name=Password]", creds["ENSURE_PASSWORD"])
    for el in page.query_selector_all("button, a.dx-button, .dx-button"):
        if re.search(r'log\s*in', (el.inner_text() or "").strip(), re.I):
            el.click(); break
    time.sleep(8)

def dump(name):
    body = page.inner_text("body")
    open(f"{OUT}/{name}.txt", "w").write(body)
    return body

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=CHROME, args=["--no-sandbox","--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36")
    page = ctx.new_page()
    login(page)
    print("=== HOME ===")
    home = dump("home")
    print(home[:1500])
    # open hamburger menu
    menu_clicked = False
    for sel in ["button", "a"]:
        for el in page.query_selector_all(sel):
            t = (el.inner_text() or "").strip()
            if t == "☰" or t == "" and el.get_attribute("class") and "hamburger" in (el.get_attribute("class") or ""):
                try:
                    el.click(); menu_clicked = True; break
                except Exception: pass
        if menu_clicked: break
    time.sleep(3)
    print("\n=== MENU TREE ===")
    menu = dump("menu")
    print(menu[:2000])
    # click representative tiles
    for tile in ["MRA Open Cond", "HEDIS Gaps", "Membership"]:
        try:
            for el in page.query_selector_all("a, div, span"):
                if (el.inner_text() or "").strip() == tile:
                    el.click(); time.sleep(5); break
            print(f"\n=== TILE {tile} ===")
            t = dump(tile.replace(" ", "_"))
            print(t[:800])
        except Exception as e:
            print(tile, "ERR", str(e)[:80])
    json.dump(ctx.cookies(), open("/tmp/solis-cookies.json", "w"))
    os.chmod("/tmp/solis-cookies.json", 0o600)
    b.close()
print("\nDONE")
