#!/usr/bin/env python3
"""CarePilot — reusable read-only data tool (Hermes consumption lane).
Logs in via sealed .env creds, extracts the live Command Center + RAF risk data into
structured JSON the RAF/coding agent consumes. READ + PROPOSE-ONLY — never writes clinical data.
Run: python3 carepilot-reader.py
"""
import sys, time, re, os, json, argparse
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
from playwright.sync_api import sync_playwright

def env(k):
    for line in open("/opt/data/profiles/nura/.env"):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

USER, PWD = env("CAREPILOT_USERNAME"), env("CAREPILOT_PASSWORD")
CHROME = "/opt/data/chrome/chrome-linux64/chrome"
BASE = "https://carepilot.nuratech.ai"

def main():
    out = {"source": "carepilot", "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "metrics": {}, "cohort_gaps": {}}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, executable_path=CHROME,
                              args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(viewport={"width": 1700, "height": 1300})
        page = ctx.new_page()
        page.goto(BASE + "/login", timeout=45000); time.sleep(3)
        page.query_selector("input[name=username]").fill(USER)
        page.query_selector("input[name=password]").fill(PWD)
        page.query_selector("button[type=submit]").click(); time.sleep(8)
        if "dashboard" not in page.url.lower():
            out["auth"] = "FAILED: " + page.url
            b.close(); return out
        out["auth"] = "ok"
        body = page.inner_text("body")
        def grab(pat):
            m = re.search(pat, body, re.I)
            return m.group(1).strip() if m else None
        out["metrics"]["active_members"] = grab(r'([\d,]+)\s*(?:active\s*members|members)')
        out["metrics"]["raf_gaps"] = grab(r'([\d,]+)\s*RAF\s*Gaps')
        out["metrics"]["no_follow_up"] = grab(r'([\d,]+)\s*No\s*Follow.Up')
        out["metrics"]["current_avg_raf"] = grab(r'Current\s*AVG\s*RAF[\s\n]*([\d.]+)')
        for m in re.finditer(r'([A-Z]{2,4})\s*\n([\d,]+)\s*gaps', body):
            out["cohort_gaps"][m.group(1)] = int(m.group(2).replace(",", ""))
        # financials page for the real capitation card (best-effort)
        try:
            page.goto(BASE + "/financials", timeout=20000); time.sleep(4)
            fin = page.inner_text("body")
            mm = re.search(r'[Mm]onthly\s*[Cc]apitation[\s\S]{0,40}?([$]?\d[\d,.KkMm]*)', fin)
            if mm: out["metrics"]["monthly_capitation"] = mm.group(1).strip()
        except Exception as e:
            out["fin_info"] = str(e)[:60]
        b.close()
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    a = ap.parse_args()
    print(json.dumps(main(), indent=2, default=str))
