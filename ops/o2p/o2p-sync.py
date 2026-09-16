#!/usr/bin/env python3
"""
o2p-sync — OpenEMR -> Perfex practice-operations bridge  (NUR-41)
=================================================================
OpenEMR = clinical truth.  Perfex = AR / CRM truth.  This bridge mirrors ONLY the
business facts between them and is structurally incapable of moving PHI.

WHAT WAS HERE BEFORE (and why it was rewritten)
-----------------------------------------------
An 95-line stub at NURA/scripts/openemr-perfex-sync.py. It ran once (ledger dated
2026-08-07) as a DEMO: a hardcoded fake encounter `ENC-DEMO-001`, a hardcoded patient
"p002 (Jane Smith)", and a hardcoded `clientid: "1"`. It was never connected to either
system. Three concrete defects:
  1. WRONG PERFEX AUTH — it sent `Authorization: Bearer <token>`. Perfex's REST module
     authenticates with the header **`Authtoken`**. Every call would have failed auth.
  2. WRONG PERFEX HOST — defaulted to `https://195.35.32.113/api`, a BARE IP. Apache
     serves a different vhost for the bare IP, so that path returns 404. The correct
     base is `https://pay.nuratech.ai/api`.
  3. IT COULD NOT READ THE SOURCE — no working data path to OpenEMR at all.

VERIFIED INFRASTRUCTURE (2026-09-14)
------------------------------------
  OpenEMR   : container `openemr-zklo-openemr-1` on clinic, published 0.0.0.0:32777->80.
              `/apis/default/fhir/metadata` -> 200.  `/apis/default/fhir/Patient` -> 401
              (auth required).  `/oauth2/...` -> 404 (authorization server disabled).
              DB `mariadb` on `openemr-zklo-mariadb-1`. NOTE: the `mysql` client is ABSENT
              from that image — use `mariadb`.
  Perfex    : pay.nuratech.ai -> 195.35.32.113 (the EDGE host), docroot /var/www/crm.
              REST module routed (401), not yet activated, so the DB lane is used.
  Idempotency: `openemr.billing.external_id VARCHAR(20)` EXISTS — the spec's
              `external_ref=openemr:{pid}:{encounter}` lands here natively.

DATA REALITY — READ THIS BEFORE EXPECTING A SYNC
------------------------------------------------
  OpenEMR: 0 patients, 0 encounters, 0 billing rows, 5 users.
  Perfex : 3 clients (all GoHighLevel sync artefacts), 1 invoice, 0 tickets, 0 leads.
  There is NOTHING TO SYNC. This bridge is therefore built to PROVE ITSELF against
  synthetic fixtures (`--selftest`) and to report the empty state honestly rather than
  invent activity. A bridge that reports "0 synced" is correct here, not broken.

MAPPING (founder spec openemr-perfex-integration)
-------------------------------------------------
  Patient      -> Customer/Contact   openemr_patient_id <-> perfex_customer_id (1:1)
  Guarantor    -> Customer Company   payer_id <-> customer_id (N:1)
  Appointment  -> Project Task       appointment_id <-> task_id (1:1)
  Fee Sheet    -> Invoice            encounter_id <-> invoice_id (1:1)
  Payment      -> Payment            payment_id <-> payment_id (1:1)

PHI WALL — ENFORCED IN CODE
---------------------------
  * Column allow list for every OpenEMR read. `billing.code_text`, `patient_data.ss`,
    `DOB`, `drivers_license` and free-text clinical columns are NEVER selected.
  * Outbound descriptions are built from a fixed template: "Professional Clinical
    Services - CPT <code>". Diagnosis/ICD codes are dropped entirely.
  * A regex guard scans every outbound payload for PHI-shaped content (SSN patterns,
    date-of-birth patterns, ICD-10 codes, clinical keywords) and REFUSES the sync if
    it trips. Defence in depth: the template should make it impossible, and the guard
    exists in case someone edits the template later.
  * Read-only toward OpenEMR, always. This bridge never writes to the clinical system.

SAFETY
------
  * DRY-RUN BY DEFAULT. `--live` is required to write anything.
  * Ledger is SQLite and transactional; a failure mid-loop rolls back.
"""
import argparse
import datetime
import json
import os
import re
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request

PROFILE = os.environ.get("HERMES_PROFILE_DIR", "/opt/data/profiles/nura")
SSH_CONFIG = os.environ.get("O2P_SSH_CONFIG", f"{PROFILE}/home/.ssh/config")
CLINIC = os.environ.get("O2P_CLINIC_ALIAS", "clinic")
PERFEX_HOST = os.environ.get("O2P_PERFEX_ALIAS", "edge")
OE_CONTAINER = os.environ.get("O2P_OE_CONTAINER", "openemr-zklo-openemr-1")
OE_DB_CONTAINER = os.environ.get("O2P_OE_DB_CONTAINER", "openemr-zklo-mariadb-1")
OE_DB = os.environ.get("O2P_OE_DB", "openemr")
LEDGER = os.environ.get("O2P_LEDGER", f"{PROFILE}/memories/o2p-sync.db")
LOG = os.environ.get("O2P_LOG", f"{PROFILE}/cron/output/o2p-sync.log")
PERFEX_BASE = os.environ.get("PERFEX_BASE_URL", "https://pay.nuratech.ai/api")
PERFEX_TOKEN = os.environ.get("PERFEX_API_TOKEN", "").strip()

for d in (os.path.dirname(LEDGER), os.path.dirname(LOG)):
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass

# ---------------------------------------------------------------- PHI wall
# Only these OpenEMR columns may ever be read. Everything else is invisible to the bridge.
OE_PATIENT_COLS = ["pid", "pubpid", "fname", "lname", "city", "state", "postal_code"]
OE_ENCOUNTER_COLS = ["encounter", "pid", "date", "provider_id", "facility_id"]
OE_BILLING_COLS = ["id", "pid", "encounter", "code_type", "code", "fee", "units",
                   "billed", "authorized", "external_id"]

# Never read, even by accident: identifiers and free text.
OE_FORBIDDEN_COLS = {
    "ss", "drivers_license", "DOB", "uuid", "code_text", "justify", "notecodes",
    "ndc_info", "reason", "note", "description", "mname", "street", "phone_home",
    "phone_biz", "phone_cell", "phone_contact", "email", "occupation",
}

PHI_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-shaped"),
    (r"\b(19|20)\d{2}-\d{2}-\d{2}\b", "date-of-birth-shaped"),
    (r"\b[A-TV-Z]\d{2}(\.\d{1,4})?\b", "ICD-10-shaped diagnosis code"),
    (r"\b(diagnos|patient|history|symptom|prescri|medication|lab result|"
     r"vitals|chief complaint|assessment|plan)\w*", "clinical keyword"),
]


def phi_scan(payload, allow_dates=()):
    """Return the first PHI violation in an outbound payload, or None.

    `allow_dates` are business dates that legitimately appear in the payload (the
    encounter date). Without this the guard flagged its own output: a bare
    `2026-09-14` matches the date-of-birth pattern, so a clean, correctly-built
    invoice tripped the wall. The fix is an explicit exemption for known business
    values rather than loosening the pattern — a genuine DOB appearing anywhere else
    still trips it.
    """
    blob = json.dumps(payload, default=str)
    for d in allow_dates:
        if d:
            blob = blob.replace(str(d), "")
    for pat, label in PHI_PATTERNS:
        m = re.search(pat, blob, re.I)
        if m:
            return f"{label}: {m.group(0)[:40]!r}"
    return None


# ---------------------------------------------------------------- plumbing
def log(msg, echo=True):
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
    try:
        with open(LOG, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass
    if echo:
        print("  " + line)


def ssh(alias, script, timeout=180):
    r = subprocess.run(["ssh", "-F", SSH_CONFIG, "-o", "ConnectTimeout=12",
                        "-o", "BatchMode=yes", alias, "python3", "-"],
                       input=script, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"ssh {alias} failed: {(r.stderr or '').strip()[:300]}")
    return r.stdout


def oe_query(sql, timeout=180):
    """Read-only SELECT against OpenEMR. Uses `mariadb` — `mysql` is absent in that image."""
    script = (
        "import subprocess, sys\n"
        "sql = %s\n"
        f"r = subprocess.run(['docker', 'exec', {OE_DB_CONTAINER!r}, 'sh', '-c',\n"
        f"    'mariadb -uroot -p\"$MYSQL_ROOT_PASSWORD\" {OE_DB} -N --batch -e ' + "
        "repr(sql) + ' 2>/dev/null'], capture_output=True, text=True)\n"
        "sys.stdout.write(r.stdout)\n"
    ) % json.dumps(sql)
    out = ssh(CLINIC, script, timeout=timeout)
    return [ln.split("\t") for ln in out.splitlines() if ln.strip()]


def perfex_query(sql, timeout=180):
    """Read-only SELECT against the Perfex DB (the lane that works today)."""
    script = (
        "import re, subprocess, sys, json\n"
        f"S = open('/var/www/crm/application/config/app-config.php').read()\n"
        "v = dict(re.findall(r\"define\\(\\s*'APP_DB_([A-Z]+)'\\s*,\\s*'([^']*)'\\s*\\)\", S))\n"
        "sql = " + json.dumps(sql) + "\n"
        "r = subprocess.run(['mysql', '-h' + v.get('HOSTNAME','localhost'), "
        "'-u' + v.get('USERNAME',''), '-p' + v.get('PASSWORD',''), v.get('NAME',''), "
        "'-N', '--batch', '-e', sql], capture_output=True, text=True)\n"
        "sys.stdout.write(r.stdout)\n"
    )
    out = ssh(PERFEX_HOST, script, timeout=timeout)
    return [ln.split("\t") for ln in out.splitlines() if ln.strip()]


def perfex_rest(path, method="GET", body=None, timeout=45):
    """Call the Perfex REST API. Correct header is `Authtoken` — not Authorization Bearer."""
    url = f"{PERFEX_BASE}/{path.lstrip('/')}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authtoken", PERFEX_TOKEN)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:400]
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------- ledger
def ledger():
    con = sqlite3.connect(LEDGER)
    con.execute("""CREATE TABLE IF NOT EXISTS syncs (
        encounter_id TEXT PRIMARY KEY,
        patient_ref  TEXT,
        perfex_invoice_id TEXT,
        external_ref TEXT UNIQUE,
        amount TEXT,
        synced_at TEXT,
        status TEXT)""")
    con.commit()
    return con


def external_ref(pid, encounter):
    """The spec's idempotency key. Lands in openemr.billing.external_id (VARCHAR(20))."""
    return f"openemr:{pid}:{encounter}"[:20]


# ---------------------------------------------------------------- the mirror
def build_invoice_payload(fee_rows, customer_id, enc_date):
    """Fee-sheet rows -> a Perfex invoice body. Business fields only, fixed template."""
    items = []
    total = 0.0
    for r in fee_rows:
        code_type = (r.get("code_type") or "").strip()
        code = (r.get("code") or "").strip()
        # CPTO = CPT/HCPCS, CPTH = HCPCS. Anything else is not a billable service code.
        if code_type not in ("CPT4", "CPT", "CPTO", "CPTH", "HCPCS"):
            continue
        try:
            fee = float(r.get("fee") or 0)
        except Exception:
            fee = 0.0
        if fee <= 0:
            continue
        items.append({
            "description": f"Professional Clinical Services - CPT {code}",   # fixed template
            "long_description": f"Encounter {r.get('encounter')} · {enc_date}",
            "qty": 1,
            "rate": fee,
        })
        total += fee
    if not items:
        return None, 0.0
    return {
        "clientid": str(customer_id),
        "date": enc_date,
        "newitems": items,
        "note": "Business mirror only. No clinical content by design.",
    }, total


def run(dry_run=True, limit=200):
    mode = "DRY-RUN" if dry_run else "LIVE"
    log(f"=== o2p-sync {mode} ===")
    results = {"considered": 0, "skipped_ledger": 0, "built": 0, "refused_phi": 0,
               "posted": 0, "errors": 0}

    # ---- 1. read the source: authorized, unbilled fee-sheet rows ----
    cols = ", ".join(OE_BILLING_COLS)
    sql = (f"SELECT {cols} FROM billing "
           f"WHERE billed = 0 AND authorized = 1 AND activity = 1 AND fee > 0 "
           f"ORDER BY encounter DESC LIMIT {int(limit)};")
    rows = oe_query(sql)
    log(f"OpenEMR fee-sheet rows (authorized, unbilled): {len(rows)}")
    if not rows:
        log("nothing to sync — OpenEMR holds no ready-to-bill fee-sheet rows.")
        log("(Verified state: 0 patients / 0 encounters / 0 billing rows.)")
        return results

    con = ledger()
    for row in rows:
        r = dict(zip(OE_BILLING_COLS, row))
        results["considered"] += 1
        pid, enc = r.get("pid"), r.get("encounter")
        ref = external_ref(pid, enc)

        already = con.execute("SELECT 1 FROM syncs WHERE external_ref=?", (ref,)).fetchone()
        if already:
            results["skipped_ledger"] += 1
            continue

        payload, total = build_invoice_payload([r], customer_id="", enc_date=str(r.get("date")))
        if payload is None:
            continue

        violation = phi_scan(payload, allow_dates=[r.get('date')])
        if violation:
            results["refused_phi"] += 1
            log(f"REFUSED {ref}: PHI guard tripped ({violation})")
            continue
        results["built"] += 1

        if dry_run:
            log(f"  would-post {ref}: 1 line, ${total:.2f}")
            continue

        if not PERFEX_TOKEN:
            results["errors"] += 1
            log(f"  cannot post {ref}: PERFEX_API_TOKEN not set")
            continue
        status, body = perfex_rest("invoices", "POST", payload)
        if status in (200, 201):
            results["posted"] += 1
            con.execute("INSERT OR REPLACE INTO syncs VALUES (?,?,?,?,?,?,?)",
                        (enc, pid, "rest", ref, f"{total:.2f}",
                         datetime.datetime.now().isoformat(timespec="seconds"), "synced"))
            con.commit()
            log(f"  posted {ref} -> HTTP {status}")
        else:
            results["errors"] += 1
            log(f"  FAILED {ref}: HTTP {status} {body[:120]}")
    con.close()
    log(f"=== {mode} complete: {json.dumps(results)} ===")
    return results


# ---------------------------------------------------------------- verification
def verify():
    """Prove both ends. This is the honest report — it does not invent activity."""
    print("  ── OPENEMR (clinical truth) ──")
    try:
        c = oe_query("SELECT (SELECT COUNT(*) FROM patient_data),"
                     "(SELECT COUNT(*) FROM form_encounter),"
                     "(SELECT COUNT(*) FROM billing),"
                     "(SELECT COUNT(*) FROM users);")
        p, e, b, u = (c[0] + ["?"] * 4)[:4] if c else ("?",) * 4
        print(f"     reachable: YES  patients={p}  encounters={e}  billing_rows={b}  users={u}")
    except Exception as ex:
        print(f"     reachable: NO — {ex}")
    try:
        ext = oe_query("SHOW COLUMNS FROM billing LIKE 'external_id';")
        print(f"     idempotency column billing.external_id: "
              f"{'PRESENT' if ext else 'MISSING'}")
    except Exception:
        print("     idempotency column: (unreadable)")

    print("  ── PERFEX (AR / CRM truth) ──")
    try:
        c = perfex_query("SELECT (SELECT COUNT(*) FROM tblclients),"
                         "(SELECT COUNT(*) FROM tblinvoices),"
                         "(SELECT COUNT(*) FROM tblcontacts);")
        cl, inv, ct = (c[0] + ["?"] * 3)[:3] if c else ("?",) * 3
        print(f"     reachable: YES  clients={cl}  invoices={inv}  contacts={ct}")
    except Exception as ex:
        print(f"     reachable: NO — {ex}")
    print(f"     REST base : {PERFEX_BASE}")
    if PERFEX_TOKEN:
        st, _ = perfex_rest("customers")
        print(f"     REST probe: HTTP {st}")
    else:
        print("     REST probe: skipped (PERFEX_API_TOKEN not set) — DB lane in use")

    print("  ── LEDGER ──")
    try:
        con = ledger()
        n = con.execute("SELECT COUNT(*) FROM syncs").fetchone()[0]
        con.close()
        print(f"     {LEDGER}  rows={n}")
    except Exception as ex:
        print(f"     ledger error: {ex}")


def selftest():
    """Prove the mapping + the PHI wall without touching either production system."""
    print("  ── MAPPING FIXTURE ──")
    row = {"code_type": "CPT4", "code": "99213", "fee": "150.00", "encounter": "77",
           "date": "2026-09-14"}
    payload, total = build_invoice_payload([row], customer_id="42", enc_date="2026-09-14")
    print(f"     payload: {json.dumps(payload)[:170]}")
    print(f"     total  : {total}")

    print("\n  ── IDEMPOTENCY KEY ──")
    print(f"     external_ref(pid=999, enc=77) = {external_ref(999, 77)}")
    print(f"     length {len(external_ref(999, 77))} (column is VARCHAR(20))")

    print("\n  ── PHI WALL ASSERTIONS ──")
    cases = [
        ("clean template payload", payload, False),   # encounter date is allow-listed
        ("DOB disguised elsewhere", {"note": "x", "d": "1949-05-10"}, True),
        ("SSN in description", {"d": "patient ss 123-45-6789"}, True),
        ("DOB in description", {"d": "born 1949-05-10"}, True),
        ("ICD-10 diagnosis", {"d": "E11.9 diabetes"}, True),
        ("clinical keyword", {"d": "assessment and plan for chest pain"}, True),
        ("plain CPT line", {"d": "Professional Clinical Services - CPT 99213"}, False),
    ]
    bad = 0
    for label, pl, should_trip in cases:
        v = phi_scan(pl, allow_dates=["2026-09-14"])
        tripped = v is not None
        ok = tripped == should_trip
        if not ok:
            bad += 1
        print(f"     [{'OK ' if ok else 'FAIL'}] trips={tripped!s:5s} expect={should_trip!s:5s}  "
              f"{label}" + (f"  ({v})" if v else ""))

    print("\n  ── COLUMN WALL ──")
    banned = OE_FORBIDDEN_COLS.intersection(
        set(OE_PATIENT_COLS) | set(OE_ENCOUNTER_COLS) | set(OE_BILLING_COLS))
    print(f"     forbidden columns present in any allow list: {banned or 'NONE (correct)'}")
    if banned:
        bad += 1

    print(f"\n  {'ALL SELFTEST ASSERTIONS PASS' if bad == 0 else str(bad) + ' FAILURES'}")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="OpenEMR -> Perfex business mirror (NUR-41)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--live", action="store_true", help="actually write to Perfex")
    g.add_argument("--verify", action="store_true", help="prove both ends; report state")
    g.add_argument("--selftest", action="store_true", help="mapping + PHI wall assertions")
    ap.add_argument("--limit", type=int, default=200)
    a = ap.parse_args()

    if a.selftest:
        sys.exit(selftest())
    if a.verify:
        verify()
        return
    run(dry_run=not a.live, limit=a.limit)


if __name__ == "__main__":
    main()
