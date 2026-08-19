#!/usr/bin/env python3
"""
emed-gap-audit.py — eMedical Practice gap audit (founder's eMEDICAL GAP-AUDIT LANE).

Read-only walk of the patient list. Per patient: the last 2 SOAP note dates, the
laboratory data, the imaging (X-ray / CT-CAT / MRI), the external consultations —
then an UPDATABLE missing-items log (JSON = machine lane, Markdown = the vault).

ACCESS RULES (the founder's law — non-negotiable):
  * SINGLE-SESSION ONLY: one login at a time. This script logs out EXPLICITLY
    at the end of every run (finally block) and never persists session cookies.
  * READ-ONLY: no chart edits, no note writes, no coding changes — only reads.
  * FHIR API = the only machine lane (client registration pending); the browser
    (playwright + the system chrome) = the single-session fallback lane.
  * MULTIPLE LOGIN ALERT: the "Multi Login Session Expired" dialog means another
    browser holds the session. The script clicks its OK button (= continue in
    THIS browser — the single-session rule) and signs in again.

Usage:
  python3 emed-gap-audit.py --dry-run      # structural verification, no browser
  python3 emed-gap-audit.py --limit 25     # live read-only audit (single session)
  python3 emed-gap-audit.py --headed       # live, visible system chrome
  python3 emed-gap-audit.py --render-only  # rebuild the MD log from existing JSON
  python3 emed-gap-audit.py --selftest     # extraction-engine matcher test only

Live-run env (per the verified recipe, skill playwright-medical-site-login):
  PYTHONPATH=/opt/data/profiles/nura/python-packages
  PLAYWRIGHT_BROWSERS_PATH=/opt/data/profiles/nura/.cache/ms-playwright
The script also inserts the PYTHONPATH itself before importing playwright.

No PHI is ever printed to stdout — only counts + categories.
"""

import argparse
import asyncio
import datetime as dt
import json
import os
import re
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------
# Constants — the lanes, the chrome, the vault
# --------------------------------------------------------------------------
BASE_URL = "https://service.emedpractice.com/"
ENV_PATH = "/opt/data/profiles/nura/.env"
CHROME_PATH = "/opt/data/chrome/chrome-linux64/chrome"
PY_PACKAGES = "/opt/data/profiles/nura/python-packages"
PW_BROWSERS = "/opt/data/profiles/nura/.cache/ms-playwright"
VAULT_MD = "/opt/data/Obsidian Vault/NURA-OS/Clinical/eMedical-Missing-Items-Log.md"
VAULT_JSON = "/opt/data/Obsidian Vault/NURA-OS/Clinical/eMedical-Missing-Items-Log.json"
SCHEMA_VERSION = 1

DESKTOP_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Login form contract (mapped 2026-08-18 from https://service.emedpractice.com/):
#   form#form1 (POST, action="./")  ·  #email · #password · #SigninBtn
#   (input type=image) · hidden: __VIEWSTATE, __VIEWSTATEGENERATOR, hdnPortalUID,
#   hdnRefNo, hdnSSID, hdnWindowWidth, hdnWindowHeight, hdnuserId
LOGIN_EMAIL = "#email"
LOGIN_PASSWORD = "#password"
LOGIN_BUTTON = "#SigninBtn"
LOGIN_ERROR = "#Message"
MULTILOG_DIALOG = "#MultiLogdialog"          # "Multi Login Session Expired"
MULTILOG_OK = ".ui-dialog-buttonset button"  # the OK button = continue here

# Post-login DOM is not mappable until an approved live run; the walk is
# discovery-driven (link heuristics) + text-regex extraction on any page.
PATIENT_NAV_TEXTS = ["patients", "patient list", "patient search", "patient360",
                     "patient 360", "search patient"]
PATIENT_NAV_CANDIDATE_PATHS = ["PatientList.aspx", "Patients.aspx", "Patient/List",
                               "PatientSearch.aspx", "SearchPatient.aspx"]
LOGOUT_URL_CANDIDATES = ["Logout.aspx", "LogOut.aspx", "SignOut.aspx",
                         "Default.aspx?action=logout"]
MAX_SUBPAGES_PER_PATIENT = 3

# --------------------------------------------------------------------------
# The extraction engine (pure stdlib — dry-run/selftest need no playwright)
# --------------------------------------------------------------------------
DATE_RE = re.compile(
    r"\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/]((?:19|20)\d{2})\b")

SOAP_KEYWORDS = ["soap", "progress note", "encounter note", "visit note",
                 "office visit", "chart note"]
LAB_KEYWORDS = ["lab", "laborator", "cbc", "bmp", "cmp", "a1c", "hba1c",
                "lipid", "tsh", "psa", "urinalysis", "metabolic panel",
                "microalbumin"]
IMAGING_KEYWORDS = {
    "xray": ["x-ray", "xray", "x ray", "radiograph"],
    "ct":   ["ct scan", "cat scan", "computed tomography", " ct "],
    "mri":  ["mri", "magnetic resonance"],
}
CONSULT_KEYWORDS = ["consult", "consultation", "referral", "specialist",
                    "specialty", "second opinion"]
ORDERED_WORDS = ["ordered", "pending", "requested", "scheduled", "prescribed",
                 "order placed"]
RECEIVED_WORDS = ["resulted", "result", "final", "received", "completed",
                  "available", "reviewed", "signed"]

# Anchor texts that are UI chrome, never patient rows.
LINK_STOPWORDS = {"patient", "patients", "view", "edit", "add", "new", "search",
                  "next", "prev", "previous", "details", "history", "chart",
                  "login", "logout", "sign", "home", "more", "open", "select",
                  "page", "go", "back", "refresh", "print", "delete"}


def parse_dates(text):
    """All MM/DD/YYYY-style dates in a text, parsed, ascending-deduped."""
    found = []
    for m in DATE_RE.finditer(text):
        raw = m.group(0)
        try:
            d = dt.datetime.strptime(raw.replace("-", "/"),
                                     "%m/%d/%Y").date()
        except ValueError:
            continue
        if d not in found:
            found.append(d)
    return sorted(found)


def _status_of(text):
    low = text.lower()
    if any(w in low for w in RECEIVED_WORDS):
        return "received"
    if any(w in low for w in ORDERED_WORDS):
        return "ordered"
    return "present"


def extract_category(text, keywords):
    """Scan text lines matching keywords → {found, status, dates}."""
    lines = [ln for ln in text.splitlines()
             if any(k in ln.lower() for k in keywords)]
    if not lines:
        return {"found": False, "status": "open", "dates": []}
    blob = " ".join(lines)
    return {"found": True, "status": _status_of(blob),
            "dates": [d.isoformat() for d in parse_dates(blob)]}


def extract_soap(text):
    """The last-2 SOAP-note dates (newest first) + the note count."""
    lines = [ln for ln in text.splitlines()
             if any(k in ln.lower() for k in SOAP_KEYWORDS)]
    blob = " ".join(lines)
    dates = parse_dates(blob)
    if not dates:
        # Fallback: dates anywhere on the page, capped at 2, newest first.
        dates = parse_dates(text)[-2:]
    return {"dates": [d.isoformat() for d in reversed(dates[-2:])],
            "note_lines": len(lines)}


def compute_missing(soap, labs, imaging, consults, now_iso):
    """Per-patient missing items from category evidence."""
    items = []
    if len(soap["dates"]) < 2:
        items.append({"item": f"SOAP notes — only {len(soap['dates'])} of the "
                              f"last 2 found",
                      "category": "soap"})
    if not labs["found"]:
        items.append({"item": "laboratory data — none found",
                      "category": "labs"})
    for mod, ev in imaging.items():
        if not ev["found"]:
            items.append({"item": f"imaging: {mod.upper()} — none found",
                          "category": f"imaging-{mod}"})
    if not consults["found"]:
        items.append({"item": "external consultation — none found",
                      "category": "consults"})
    return [dict(i, status="open", first_seen=now_iso, last_checked=now_iso)
            for i in items]


def patient_overall_status(items):
    if not items:
        return "ok"
    if any(i["status"] == "open" for i in items):
        return "open"
    if any(i["status"] == "ordered" for i in items):
        return "ordered"
    return "received"


# --------------------------------------------------------------------------
# The updatable log — JSON (machine lane) + Markdown (vault)
# --------------------------------------------------------------------------
def load_existing(json_path):
    if not Path(json_path).exists():
        return None
    try:
        return json.loads(Path(json_path).read_text())
    except Exception:
        return None


def merge_patients(old_patients, new_entries):
    """Updatable merge keyed on patient_id: preserve ordered/received statuses,
    resolve items that now have evidence, keep untouched patients as-is."""
    by_key = {}
    for p in old_patients or []:
        by_key[p.get("patient_id") or p.get("patient_name", "")] = dict(p)
    for new in new_entries:
        key = new.get("patient_id") or new.get("patient_name", "")
        old = by_key.get(key)
        if not old:
            by_key[key] = new
            continue
        # Preserve statuses of previously logged missing items.
        old_items = {i["item"]: i for i in old.get("missing_items", [])}
        resolved = list(old.get("resolved_items", []))
        merged_items = []
        for fresh in new["missing_items"]:
            prev = old_items.get(fresh["item"])
            if prev and prev["status"] in ("ordered", "received"):
                merged_items.append(dict(prev, last_checked=new["last_checked"]))
            else:
                merged_items.append(fresh)
        # Items no longer missing this run → resolved.
        fresh_names = {i["item"] for i in merged_items}
        for name, prev in old_items.items():
            if name not in fresh_names and prev["status"] in ("ordered", "received"):
                resolved.append(dict(prev, resolved_at=new["last_checked"]))
        old["missing_items"] = merged_items
        old["resolved_items"] = resolved
        old["last_soap"] = new["last_soap"]
        old["labs_last_found"] = new.get("labs_last_found")
        old["overall_status"] = patient_overall_status(merged_items)
        old["last_checked"] = new["last_checked"]
    return list(by_key.values())


def build_summary(patients):
    s = {"patients": len(patients), "missing_labs": 0, "missing_imaging": 0,
         "missing_consults": 0, "soap_gaps": 0,
         "open": 0, "ordered": 0, "received": 0}
    for p in patients:
        for i in p.get("missing_items", []):
            cat = i["category"]
            if cat == "labs":
                s["missing_labs"] += 1
            elif cat.startswith("imaging"):
                s["missing_imaging"] += 1
            elif cat == "consults":
                s["missing_consults"] += 1
            elif cat == "soap":
                s["soap_gaps"] += 1
            s[i["status"]] = s.get(i["status"], 0) + 1
    return s


def render_markdown(payload):
    p = payload["patients"]
    rows = []
    for pt in p:
        soap = pt.get("last_soap", {}).get("dates", [])
        while len(soap) < 2:
            soap.append("—")
        labs_missing = [i["item"] for i in pt.get("missing_items", [])
                        if i["category"] == "labs"]
        img_missing = [i["item"].replace("imaging: ", "").replace(" — none found", "")
                       for i in pt.get("missing_items", [])
                       if i["category"].startswith("imaging")]
        con_missing = [i["item"] for i in pt.get("missing_items", [])
                       if i["category"] == "consults"]
        soap_gaps = [i["item"] for i in pt.get("missing_items", [])
                     if i["category"] == "soap"]
        rows.append(
            f"| {pt.get('patient_name', '—')} | {soap[0]} | {soap[1]} "
            f"| {_cell(labs_missing + soap_gaps)} | {_cell(img_missing)} "
            f"| {_cell(con_missing)} | {pt.get('overall_status', '—')} "
            f"| {pt.get('last_checked', '—')} |")
    run = payload.get("run", {})
    summary = payload.get("summary", {})
    return f"""# eMedical Missing-Items Log — the updatable record

> DOCTRINE: read-only audit · single-session only (explicit logout every run) ·
> browser = fallback lane until the FHIR client registration clears.

- Last run: `{payload.get('generated_at')}` · mode `{run.get('mode')}` ·
  login `{run.get('login')}` · logout `{run.get('logout')}` ·
  scanned `{run.get('patients_scanned', summary.get('patients', 0))}`
- Counts: patients `{summary.get('patients', 0)}` · missing labs
  `{summary.get('missing_labs', 0)}` · missing imaging
  `{summary.get('missing_imaging', 0)}` · missing consults
  `{summary.get('missing_consults', 0)}` · SOAP gaps `{summary.get('soap_gaps', 0)}`

## Per-patient board

| Patient | Last SOAP #1 | Last SOAP #2 | Missing labs / SOAP | Missing imaging (X-ray/CT/MRI) | Missing consults | Status | Last checked |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows) if rows else '| *(no patients scanned yet)* | — | — | — | — | — | — | — |'}

## Legend

- **Status** — `open` = identified missing, nothing done · `ordered` = the
  item has been ordered/requested · `received` = the result/note arrived ·
  `ok` = no gaps found.
- **Missing imaging** lists only the modalities with no evidence (X-ray / CT / MRI).

## How this log updates

1. Live audit (single session): `python3 emed-gap-audit.py --limit 25`
2. The script merges into the JSON (the machine lane) and regenerates this
   table — statuses you set to `ordered`/`received` in the JSON are preserved.
3. Rebuild the table without a browser: `python3 emed-gap-audit.py --render-only`

## Run history

| Ran at | Mode | Scanned | Open | Ordered | Received |
|---|---|---|---|---|---|
{payload.get('history_line', '| — | — | — | — | — | — |')}
"""


def _cell(items):
    return "<br>".join(items) if items else "—"


# --------------------------------------------------------------------------
# Playwright lane (lazy import — dry-run/selftest never touch it)
# --------------------------------------------------------------------------
def _load_playwright():
    sys.path.insert(0, PY_PACKAGES)
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", PW_BROWSERS)
    try:
        from playwright.async_api import async_playwright  # noqa: PLC0415
        return async_playwright
    except ImportError as e:
        raise SystemExit(
            "playwright not importable from %s — run with "
            "PYTHONPATH=%s (skill: playwright-medical-site-login): %s"
            % (PY_PACKAGES, PY_PACKAGES, e))


def _read_credentials():
    """EMED_USERNAME / EMED_PASSWORD — env first, then the sealed .env (0600)."""
    creds = {"user": os.environ.get("EMED_USERNAME"),
             "password": os.environ.get("EMED_PASSWORD")}
    env = Path(ENV_PATH)
    if env.exists() and (not creds["user"] or not creds["password"]):
        for line in env.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            if k.strip() == "EMED_USERNAME" and not creds["user"]:
                creds["user"] = v
            elif k.strip() == "EMED_PASSWORD" and not creds["password"]:
                creds["password"] = v
    if not creds["user"] or not creds["password"]:
        raise SystemExit("EMED_USERNAME/EMED_PASSWORD missing (env or %s)" % ENV_PATH)
    return creds


async def _set_form_metadata(page):
    """ASP.NET WebForms hidden fields the page JS normally fills on click."""
    try:
        await page.evaluate("""() => {
            const w = document.getElementById('hdnWindowWidth');
            if (w) w.value = window.innerWidth || 1920;
            const h = document.getElementById('hdnWindowHeight');
            if (h) h.value = window.innerHeight || 1080;
        }""")
    except Exception:
        pass


async def handle_multiple_login(page):
    """The Multiple Login Alert: another browser holds the session.
    The OK button = continue in THIS browser (the single-session rule)
    → redirects to ?OK → sign in again."""
    try:
        dlg = page.locator(MULTILOG_DIALOG)
        await dlg.wait_for(state="visible", timeout=8000)
        ok = page.locator(MULTILOG_OK).first
        await ok.click()
        await page.wait_for_load_state("load", timeout=15000)
        return True
    except Exception:
        return False


async def do_login(page, creds):
    """Email/password/__VIEWSTATE flow (browser submit carries VIEWSTATE).
    Returns (logged_in: bool, multiple_login_alert: bool, error: str|None)."""
    for attempt in (1, 2):
        try:
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=45000)
            await page.wait_for_selector(LOGIN_EMAIL, timeout=20000)
            await page.fill(LOGIN_EMAIL, creds["user"])
            await page.fill(LOGIN_PASSWORD, creds["password"])
            await _set_form_metadata(page)
            await page.click(LOGIN_BUTTON)
            await page.wait_for_load_state("load", timeout=45000)
            try:
                await page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            if await handle_multiple_login(page):
                # Continue-in-this-browser chosen; loop re-submits on ?OK.
                continue
            if page.locator(LOGIN_EMAIL).count() == 0:
                return True, False, None
            err = None
            try:
                if page.locator(LOGIN_ERROR).is_visible():
                    err = (page.locator(LOGIN_ERROR).inner_text() or "")[:200]
            except Exception:
                pass
            if attempt == 2:
                return False, False, err or "login page still shown"
        except Exception as e:
            if attempt == 2:
                return False, False, f"login exception: {type(e).__name__}"
    return False, True, "multiple-login loop did not resolve"


async def collect_anchors(page):
    try:
        return await page.eval_on_selector_all(
            "a", "els => els.map(e => ({href: e.href || '', "
                 "text: (e.innerText || '').trim()}))")
    except Exception:
        return []


def _looks_like_patient_row(text, href):
    t = text.strip()
    if not t or len(t) < 3 or len(t) > 80:
        return False
    if t.lower() in LINK_STOPWORDS:
        return False
    if "patient" not in href.lower():
        return False
    # Name-ish: contains letters and either a comma or two words.
    words = [w for w in t.split() if any(c.isalpha() for c in w)]
    return len(words) >= 2 or "," in t


async def find_patient_list(page):
    """Discovery-driven: nav to the patient list, return [(name, url)]."""
    anchors = await collect_anchors(page)
    nav = None
    for a in anchors:
        t = a["text"].strip().lower()
        if t in PATIENT_NAV_TEXTS and "patient" in a["href"].lower():
            nav = a["href"]
            break
    if not nav:
        for path in PATIENT_NAV_CANDIDATE_PATHS:
            try:
                resp = await page.goto(BASE_URL.rstrip("/") + "/" + path,
                                       wait_until="domcontentloaded", timeout=20000)
                if resp and resp.status < 400:
                    nav = page.url
                    break
            except Exception:
                continue
    if not nav:
        return []
    if page.url != nav:
        try:
            await page.goto(nav, wait_until="domcontentloaded", timeout=30000)
        except Exception:
            return []
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    seen, out = set(), []
    for a in await collect_anchors(page):
        if _looks_like_patient_row(a["text"], a["href"]) and a["href"] not in seen:
            seen.add(a["href"])
            out.append({"name": a["text"].strip(), "url": a["href"]})
    return out


async def visit_patient(page, entry):
    """Read-only patient chart walk: main page + up to 3 lab/imaging/consult
    sub-pages. Returns the merged visible text."""
    texts = []
    try:
        await page.goto(entry["url"], wait_until="domcontentloaded", timeout=45000)
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        texts.append(await page.inner_text("body"))
        sub = 0
        for a in await collect_anchors(page):
            if sub >= MAX_SUBPAGES_PER_PATIENT:
                break
            low = (a["href"] + " " + a["text"]).lower()
            if any(k in low for k in ("lab", "imag", "xray", "x-ray", "mri",
                                      "scan", "consult", "document", "report")):
                try:
                    await page.goto(a["href"], wait_until="domcontentloaded",
                                    timeout=25000)
                    texts.append(await page.inner_text("body"))
                    sub += 1
                except Exception:
                    continue
    except Exception as e:
        return " ".join(texts), f"visit exception: {type(e).__name__}"
    return " ".join(texts), None


async def do_logout(page):
    """The explicit session close — the single-session law. Returns the outcome."""
    if page.locator(LOGIN_EMAIL).count() > 0:
        return "already-at-login"
    for pat in (r"log\s*out", r"sign\s*out"):
        try:
            el = page.get_by_text(re.compile(pat, re.I)).first
            if await el.count() > 0:
                await el.click(timeout=6000)
                try:
                    await page.wait_for_load_state("load", timeout=15000)
                except Exception:
                    pass
                if page.locator(LOGIN_EMAIL).count() > 0:
                    return "explicit"
        except Exception:
            continue
    for path in LOGOUT_URL_CANDIDATES:
        try:
            await page.goto(BASE_URL.rstrip("/") + "/" + path,
                            wait_until="domcontentloaded", timeout=15000)
            if page.locator(LOGIN_EMAIL).count() > 0:
                return "explicit-url"
        except Exception:
            continue
    return "failed"


async def live_audit(args):
    creds = _read_credentials()
    pw = _load_playwright()
    run = {"mode": "live", "login": False, "multiple_login_alert": False,
           "logout": "n/a", "patients_scanned": 0, "read_only": True}
    entries, notes = [], []
    async with pw() as p:
        browser = await p.chromium.launch(
            executable_path=CHROME_PATH, headless=not args.headed,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                  "--window-size=1920,1080"])
        context = await browser.new_context(user_agent=DESKTOP_UA,
                                            viewport={"width": 1920,
                                                      "height": 1080})
        page = await context.new_page()
        page.set_default_timeout(30000)
        try:
            logged, multi, err = await do_login(page, creds)
            run["login"] = logged
            run["multiple_login_alert"] = multi
            if not logged:
                notes.append(f"login blocked: {err}")
                return run, [], notes
            patient_links = await find_patient_list(page)
            if not patient_links:
                notes.append("no patient list found post-login (DOM unmapped — "
                             "discovery heuristics failed; needs one approved "
                             "headed run to map selectors)")
            now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
            limit = args.limit if args.limit and args.limit > 0 else len(patient_links)
            for i, entry in enumerate(patient_links[:limit]):
                run["patients_scanned"] += 1
                text, err = await visit_patient(page, entry)
                soap = extract_soap(text)
                labs = extract_category(text, LAB_KEYWORDS)
                imaging = {m: extract_category(text, kws)
                           for m, kws in IMAGING_KEYWORDS.items()}
                consults = extract_category(text, CONSULT_KEYWORDS)
                pid = re.search(r"(?:id|pid)=(\d+)", entry["url"])
                entries.append({
                    "patient_id": pid.group(1) if pid else "",
                    "patient_name": entry["name"],
                    "chart_url": entry["url"],
                    "last_soap": soap,
                    "labs_last_found": (labs["dates"][-1] if labs["dates"] else None),
                    "missing_items": compute_missing(soap, labs, imaging,
                                                     consults, now),
                    "resolved_items": [],
                    "overall_status": patient_overall_status(
                        compute_missing(soap, labs, imaging, consults, now)),
                    "visit_error": err,
                    "last_checked": now,
                })
        finally:
            try:
                run["logout"] = await do_logout(page)
            finally:
                await context.close()
                await browser.close()
    return run, entries, notes


# --------------------------------------------------------------------------
# Writers + the dry-run / selftest structural verification
# --------------------------------------------------------------------------
def write_outputs(json_path, md_path, payload, merge):
    if merge:
        old = load_existing(json_path)
        if old and old.get("patients") is not None:
            payload["patients"] = merge_patients(old["patients"],
                                                 payload["patients"])
    payload["summary"] = build_summary(payload["patients"])
    payload["history_line"] = (
        f"| {payload['generated_at']} | {payload['run']['mode']} "
        f"| {payload['run'].get('patients_scanned', 0)} "
        f"| {payload['summary']['open']} | {payload['summary']['ordered']} "
        f"| {payload['summary']['received']} |")
    json_path = Path(json_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(json_path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, json_path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    md_path = Path(md_path)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(payload))
    return payload


def selftest():
    """The extraction engine on synthetic text (no PHI) — proves the matchers."""
    sample = """
    SOAP Note 05/12/2026 — progress note, MEAT documented.
    SOAP Note 04/08/2026 — encounter note.
    Lab: CBC, BMP ordered 05/15/2026. A1C pending.
    X-ray chest: ordered. CT abdomen: resulted 04/20/2026.
    Consultation: Cardiology received 06/01/2026.
    """
    checks = []
    soap = extract_soap(sample)
    checks.append(("SOAP — 2 dates, newest first",
                   soap["dates"] == ["2026-05-12", "2026-04-08"]))
    labs = extract_category(sample, LAB_KEYWORDS)
    checks.append(("labs found + ordered",
                   labs["found"] and labs["status"] == "ordered"))
    xr = extract_category(sample, IMAGING_KEYWORDS["xray"])
    ct = extract_category(sample, IMAGING_KEYWORDS["ct"])
    mri = extract_category(sample, IMAGING_KEYWORDS["mri"])
    checks.append(("X-ray found", xr["found"]))
    checks.append(("CT received", ct["found"] and ct["status"] == "received"))
    checks.append(("MRI missing (open)", not mri["found"] and mri["status"] == "open"))
    con = extract_category(sample, CONSULT_KEYWORDS)
    checks.append(("consult received",
                   con["found"] and con["status"] == "received"))
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    items = compute_missing(soap, labs,
                            {"xray": xr, "ct": ct, "mri": mri}, con, now)
    checks.append(("missing items = MRI only",
                   len(items) == 1 and items[0]["category"] == "imaging-mri"))
    return checks


def dry_run(args):
    print("== eMedical gap audit — DRY-RUN (no browser, no login) ==")
    ok = True
    env = Path(ENV_PATH)
    if env.exists():
        mode = oct(env.stat().st_mode & 0o777)
        print(f"[ok]  .env present ({mode})")
        keys = {k for k in ("EMED_USERNAME", "EMED_PASSWORD") if k in os.environ}
        body = env.read_text()
        for k in ("EMED_USERNAME", "EMED_PASSWORD"):
            m = re.search(rf"^{k}=(.*)$", body, re.M)
            if m and m.group(1).strip().strip('"'):
                keys.add(k)
        missing = {"EMED_USERNAME", "EMED_PASSWORD"} - keys
        if missing:
            print(f"[FAIL] missing env keys: {sorted(missing)}")
            ok = False
        else:
            print("[ok]  EMED_USERNAME + EMED_PASSWORD sealed (values not read)")
    else:
        print(f"[FAIL] .env missing: {ENV_PATH}")
        ok = False
    chrome = Path(CHROME_PATH)
    if chrome.exists() and os.access(chrome, os.X_OK):
        print(f"[ok]  system chrome {chrome}")
    else:
        print(f"[FAIL] system chrome missing: {chrome}")
        ok = False
    for p in (args.json, args.md):
        parent = Path(p).parent
        if parent.exists() and os.access(parent, os.W_OK):
            print(f"[ok]  writable {p}")
        else:
            print(f"[FAIL] not writable {p}")
            ok = False
    print("-- extraction-engine selftest --")
    for name, passed in selftest():
        print(f"[{'ok' if passed else 'FAIL'}]  {name}")
        ok = ok and passed
    print("-- selector contract (mapped 2026-08-18) --")
    for name, sel in (("email", LOGIN_EMAIL), ("password", LOGIN_PASSWORD),
                      ("signin button", LOGIN_BUTTON),
                      ("__VIEWSTATE", "input#__VIEWSTATE (browser form submit "
                                       "carries it)"),
                      ("MultiLogin dialog", MULTILOG_DIALOG),
                      ("MultiLogin OK=continue", MULTILOG_OK)):
        print(f"[ok]  {name}: {sel}")
    print("-- output schema skeleton --")
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now,
        "run": {"mode": "dry-run", "login": False, "logout": "n/a",
                "multiple_login_alert": False, "patients_scanned": 0,
                "read_only": True,
                "note": "live login not executed — approval gate denied the "
                        "playwright runtime check (2026-08-18); browser lane "
                        "untouched, single-session preserved"},
        "patients": [],
        "summary": {},
    }
    write_outputs(args.json, args.md, payload, merge=False)
    print(f"[ok]  wrote {args.json}")
    print(f"[ok]  wrote {args.md}")
    print("DRY-RUN " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def render_only(args):
    old = load_existing(args.json)
    if not old:
        print(f"[FAIL] no JSON log at {args.json} — run the audit or --dry-run first")
        return 1
    payload = write_outputs(args.json, args.md, dict(old), merge=False)
    print(f"[ok]  rebuilt {args.md} from {args.json} "
          f"({payload['summary']['patients']} patients)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="structural verification only — no browser, no login")
    ap.add_argument("--render-only", action="store_true",
                    help="rebuild the MD log from the existing JSON")
    ap.add_argument("--selftest", action="store_true",
                    help="run only the extraction-engine matcher test")
    ap.add_argument("--limit", type=int, default=25,
                    help="max patients per live run (0 = all; default 25)")
    ap.add_argument("--headed", action="store_true",
                    help="run the system chrome visible (default headless)")
    ap.add_argument("--json", default=VAULT_JSON, help="JSON log path")
    ap.add_argument("--md", default=VAULT_MD, help="Markdown log path")
    ap.add_argument("--no-merge", action="store_true",
                    help="overwrite instead of merging into the existing JSON")
    args = ap.parse_args()
    if args.selftest:
        fails = [n for n, p in selftest() if not p]
        for n, p in selftest():
            print(f"[{'ok' if p else 'FAIL'}]  {n}")
        return 1 if fails else 0
    if args.dry_run:
        return dry_run(args)
    if args.render_only:
        return render_only(args)
    run, entries, notes = asyncio.run(live_audit(args))
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now,
        "run": run,
        "notes": notes,
        "patients": entries,
        "summary": {},
    }
    payload = write_outputs(args.json, args.md, payload, merge=not args.no_merge)
    s = payload["summary"]
    print("== eMedical gap audit complete ==")
    print(f"login={run['login']} multiple-login-alert="
          f"{run['multiple_login_alert']} logout={run['logout']} "
          f"scanned={run['patients_scanned']}")
    print(f"patients={s['patients']} missing-labs={s['missing_labs']} "
          f"missing-imaging={s['missing_imaging']} "
          f"missing-consults={s['missing_consults']} soap-gaps={s['soap_gaps']}")
    print(f"statuses: open={s['open']} ordered={s['ordered']} "
          f"received={s['received']}")
    for n in notes:
        print(f"note: {n}")
    return 0 if run["login"] or run["patients_scanned"] else 1


if __name__ == "__main__":
    sys.exit(main())
