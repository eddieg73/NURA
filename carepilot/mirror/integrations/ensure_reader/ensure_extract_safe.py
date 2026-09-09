#!/usr/bin/env python3
"""Non-demo Ensure read that emits ONLY aggregate / non-PHI signals.

Never writes patient names, MRNs, DOB, SSN, or free-text patient rows.
Output JSON is safe for out/ and for propose-only intake.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CREDS = os.environ.get("ENSURE_CREDS_FILE", "/tmp/nura-portal-creds.env")
CHROME_CANDIDATES = [
    os.environ.get("ENSURE_CHROME", ""),
    "/root/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome",
    "/opt/data/chrome/chrome-linux64/chrome",
]
LOGIN_URL = "https://solis.ensuredatasolutions.com/Login"
TIMEOUT_MS = int(os.environ.get("ENSURE_SMOKE_TIMEOUT_MS", "120000"))
OUT_DIR = Path(__file__).resolve().parent / "out"

PHI_HINT = re.compile(
    r"\b(mrn|dob|ssn|patient|member\s*id|date\s*of\s*birth)\b"
    r"|(\d{3}-\d{2}-\d{4})"
    r"|(\b\d{8,}\b)",
    re.I,
)


def load_creds(path: str) -> dict:
    if not os.path.isfile(path):
        print("AUTH=BLOCKED")
        print("REASON=missing sealed creds")
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
        sys.exit(2)
    return creds


def pick_chrome():
    for pth in CHROME_CANDIDATES:
        if pth and os.path.isfile(pth) and os.access(pth, os.X_OK):
            return pth
    return None


def safe_label(text: str, max_len: int = 40):
    t = (text or "").strip()
    if not t or len(t) > 80:
        return None
    if PHI_HINT.search(t):
        return None
    if re.match(r"^[A-Z][a-z]+\s+[A-Z][a-z]+$", t):
        return None
    return t[:max_len]


def aggregate_signals(page) -> dict:
    title = ""
    try:
        title = (page.title() or "")[:80]
    except Exception:
        pass

    url = page.url
    path = url.split("?", 1)[0]
    url_hash = hashlib.sha256(path.encode()).hexdigest()[:16]

    nav_count = 0
    nav_labels = []
    for sel in ["nav a", "aside a", ".dx-menu-item", "[role=menuitem]", ".sidebar a", ".menu a"]:
        try:
            els = page.query_selector_all(sel)
            if els:
                nav_count = max(nav_count, len(els))
                for el in els[:30]:
                    lab = safe_label(el.inner_text() or "")
                    if lab and lab not in nav_labels:
                        nav_labels.append(lab)
                break
        except Exception:
            continue

    card_count = 0
    safe_metric_labels = []
    for sel in [
        ".dx-card",
        ".card",
        "[class*=metric]",
        "[class*=kpi]",
        "[class*=stat]",
        ".dashboard-tile",
        ".tile",
    ]:
        try:
            els = page.query_selector_all(sel)
            if els:
                card_count = max(card_count, len(els))
                for el in els[:12]:
                    lab = safe_label((el.inner_text() or "").split("\n")[0])
                    if lab and not re.search(r"\d{5,}", lab):
                        if lab not in safe_metric_labels:
                            safe_metric_labels.append(lab)
                break
        except Exception:
            continue

    link_count = 0
    try:
        link_count = len(page.query_selector_all("a"))
    except Exception:
        pass

    btn_count = 0
    try:
        btn_count = len(page.query_selector_all("button, .dx-button, input[type=submit]"))
    except Exception:
        pass

    session_token = hashlib.sha256(
        f"{path}|{title}|{nav_count}|{card_count}|{datetime.now(timezone.utc).strftime('%Y%m%d')}".encode()
    ).hexdigest()[:12]

    return {
        "auth_ok": True,
        "page_title": title if not PHI_HINT.search(title) else "[redacted]",
        "url_path_hash": url_hash,
        "nav_item_count": nav_count,
        "nav_labels_safe": nav_labels[:15],
        "metric_card_count": card_count,
        "metric_labels_safe": safe_metric_labels[:10],
        "link_count": link_count,
        "button_count": btn_count,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "phi_policy": "aggregates_only_no_patient_identifiers",
        "external_ref": f"ensure-agg-{session_token}",
    }


def main() -> int:
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
                return 1
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
                    return 1
                if "captcha" in body_l:
                    print("AUTH=FAILED")
                    print("REASON=captcha")
                    print("URL=" + url)
                    browser.close()
                    return 1
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
                return 1

            time.sleep(4)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            signals = aggregate_signals(page)
            print("AUTH=OK")
            print("URL=" + url.split("?")[0])
            if title:
                print("TITLE=" + title[:80])
            print("NAV_COUNT=" + str(signals["nav_item_count"]))
            print("METRIC_CARD_COUNT=" + str(signals["metric_card_count"]))
            print("LINK_COUNT=" + str(signals["link_count"]))
            print("BUTTON_COUNT=" + str(signals["button_count"]))

            rows = [{
                "kind": "ensure_aggregate_probe",
                "external_ref": signals["external_ref"],
                "summary": (
                    "Ensure aggregate read: nav=%s cards=%s links=%s (no PHI; propose-only)"
                    % (signals["nav_item_count"], signals["metric_card_count"], signals["link_count"])
                ),
                "lane": "A",
                "signals": {
                    "page_title": signals["page_title"],
                    "url_path_hash": signals["url_path_hash"],
                    "nav_item_count": signals["nav_item_count"],
                    "metric_card_count": signals["metric_card_count"],
                    "link_count": signals["link_count"],
                    "button_count": signals["button_count"],
                    "nav_labels_safe": signals["nav_labels_safe"],
                    "metric_labels_safe": signals["metric_labels_safe"],
                    "phi_policy": signals["phi_policy"],
                },
            }]

            OUT_DIR.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            out_path = OUT_DIR / ("ensure_safe_extract_%s.json" % stamp)
            payload = {"rows": rows, "extracted_at": signals["extracted_at"], "auth": "OK"}
            out_path.write_text(json.dumps(payload, indent=2) + "\n")
            print("OUT_PATH=" + str(out_path))
            browser.close()
            return 0
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
            return 1


if __name__ == "__main__":
    sys.exit(main())
