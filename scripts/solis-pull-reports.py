#!/usr/bin/env python3
"""Ensure/Solis report puller: login, click a report tile, export the DevExtreme grid, save file.
Usage: python3 solis-pull-reports.py <report-name>  (e.g. 'MRA Open Cond')"""
import sys, time, re, os
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

creds = {}
for line in open("/tmp/nura-portal-creds.env"):
    k, v = line.strip().split("=", 1); creds[k] = v
CHROME = "/opt/data/chrome/chrome-linux64/chrome"
OUT = "/tmp/solis-reports"; os.makedirs(OUT, exist_ok=True)
REPORT = sys.argv[1] if len(sys.argv) > 1 else "MRA Open Cond"

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=CHROME, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
    ctx = b.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36", accept_downloads=True)
    page = ctx.new_page()
    page.goto("https://solis.ensuredatasolutions.com/Login", timeout=45000, wait_until="domcontentloaded")
    time.sleep(4)
    page.fill("input[name=Username]", creds["ENSURE_USERNAME"])
    page.fill("input[name=Password]", creds["ENSURE_PASSWORD"])
    for el in page.query_selector_all("button, a.dx-button, .dx-button"):
        if re.search(r"log\s*in", (el.inner_text() or "").strip(), re.I):
            el.click(); break
    time.sleep(8)
    print("login landed:", page.title())
    # click the report tile by exact text
    clicked = False
    for el in page.query_selector_all("a, div, span, li"):
        if (el.inner_text() or "").strip() == REPORT:
            try:
                el.click(); clicked = True; print("clicked tile:", REPORT); break
            except Exception as e:
                print("click fail:", str(e)[:80])
    if not clicked:
        # try partial match
        for el in page.query_selector_all("a, div, span, li"):
            t = (el.inner_text() or "").strip()
            if REPORT.lower() in t.lower() and len(t) < 60:
                try:
                    el.click(); clicked = True; print("clicked (partial):", t); break
                except Exception: pass
    time.sleep(8)
    print("after tile:", page.title())
    body = page.inner_text("body")
    print("grid present:", "dx-datagrid" in page.inner_html("body"))
    # inventory export-ish buttons
    export_btns = []
    for el in page.query_selector_all("button, .dx-button, .dx-toolbar-item, span, i"):
        try:
            cls = el.get_attribute("class") or ""
            t = (el.inner_text() or "").strip()
            if re.search(r"export|excel|xlsx|csv|download", cls + " " + t, re.I):
                export_btns.append((cls[:60], t[:40]))
        except Exception: pass
    print("export candidates:", export_btns[:10])
    # try to click an export control and capture the download
    got = False
    for el in page.query_selector_all("button, .dx-button, i, span"):
        try:
            cls = el.get_attribute("class") or ""
            t = (el.inner_text() or "").strip()
            if re.search(r"xlsxfile|excel|export|csv", cls + " " + t, re.I):
                with page.expect_download(timeout=25000) as dl_info:
                    el.click()
                dl = dl_info.value
                fn = os.path.join(OUT, f"{REPORT.replace(' ','_')}_{dl.suggested_filename}")
                dl.save_as(fn)
                print("DOWNLOADED:", fn)
                got = True
                break
        except Exception:
            pass
    if not got:
        # fallback: the toolbar EXPORT menu (membership/hospitalization grids)
        for el in page.query_selector_all("span, div, a, button"):
            t = (el.inner_text() or "").strip().upper()
            if t == "EXPORT" and len(t) < 10:
                try:
                    el.click(); time.sleep(3); break
                except Exception:
                    pass
        for el in page.query_selector_all("span, div, a, li"):
            t = (el.inner_text() or "").strip().lower()
            if t in ("export to excel", "export to csv", "excel", "csv", "xlsx"):
                try:
                    with page.expect_download(timeout=25000) as dl_info:
                        el.click()
                    dl = dl_info.value
                    fn = os.path.join(OUT, f"{REPORT.replace(' ','_')}_{dl.suggested_filename}")
                    dl.save_as(fn)
                    print("DOWNLOADED(menu):", fn)
                    got = True
                    break
                except Exception:
                    pass
    if not got:
        print("no download captured; dumping visible grid text sample")
        print(body[:600])
    page.screenshot(path=f"/tmp/solis-reports/{REPORT.replace(' ', '_')}_screen.png")
    b.close()
print("done")
