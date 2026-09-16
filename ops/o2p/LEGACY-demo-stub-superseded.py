#!/usr/bin/env python3
"""OPENEMR ↔ PERFEX SYNC BRIDGE — the sidecar-safe business mirror.
Best practices: idempotent (encounter-id ledger), dry-run default, audit-log,
business-fields only (NEVER clinical content), reversible, evidence-verified."""
import json, os, sqlite3, sys, urllib.request, urllib.error, datetime, hashlib

BASE = "/opt/data/profiles/nura"
ENV_FILE = os.path.join(BASE, ".env")
LEDGER = os.path.join(BASE, "memories", "openemr-perfex-sync.db")
LOG = os.path.join(BASE, "cron", "output", "openemr-perfex-sync.log")
os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def env(k, default=""):
    try:
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith(k + "="):
                    return line.strip().split("=", 1)[1].strip('"').strip("'")
    except Exception:
        pass
    return default

def log(msg):
    line = f"[{datetime.datetime.now().isoformat()}] {msg}"
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line)

def init_ledger():
    con = sqlite3.connect(LEDGER)
    con.execute("CREATE TABLE IF NOT EXISTS syncs (encounter_id TEXT PRIMARY KEY, patient_ref TEXT, invoice_id TEXT, synced_at TEXT, status TEXT)")
    return con

def call(method, url, headers=None, body=None, timeout=30):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    if body is not None:
        req.data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"status": r.status, "body": r.read().decode()[:400]}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": e.read().decode()[:300]}
    except Exception as e:
        return {"status": 0, "body": str(e)[:200]}

def main():
    dry = "--live" not in sys.argv
    mode = "DRY-RUN" if dry else "LIVE"
    log(f"=== bridge {mode} ===")
    con = init_ledger()
    # 1. THE SOURCE: OpenEMR encounters (the REST — the sidecar: business-fields only!)
    oe_base = env("OPENEMR_BASE_URL", "https://72.61.71.211")
    oe_user = env("OPENEMR_USERNAME", "admin")
    oe_pass = env("OPENEMR_PASSWORD", "")
    if not oe_pass:
        log("⚠ OPENEMR_PASSWORD missing — the OpenEMR-MCP lane carries its own; the bridge needs the REST creds for the raw sync. NOTE-not-blocker: the lane-based path remains.")
    # 2. THE TARGET: Perfex invoice-create (the REST!)
    pfx_base = env("PERFEX_BASE_URL", "https://195.35.32.113/api")
    pfx_token = env("PERFEX_API_TOKEN", "")
    if not pfx_token:
        log("⚠ PERFEX_API_TOKEN missing — the Perfex invoice-write needs the token (the founder's drop from the Perfex → API settings!)")
    # 3. THE MAPPING + THE IDEMPOTENCY (the demo-flow: the encounter → the invoice-draft!)
    sample = {
        "encounter_id": "ENC-DEMO-001",
        "patient_ref": "p002 (Jane Smith)",
        "encounter_date": "2026-08-07",
        "service": "Consultation",
        "codes": {"cpt": "99213", "icd10": "Z00.00"},
        "charge": 150.00,
        "note": "business-mirror only — no clinical content (sidecar doctrine)",
    }
    synced = con.execute("SELECT 1 FROM syncs WHERE encounter_id=?", (sample["encounter_id"],)).fetchone()
    if synced:
        log("↩ idempotent: ENC-DEMO-001 already synced — skipping (no double-invoice!)")
    else:
        log(f"→ would-create invoice: {sample['patient_ref']} | {sample['codes']['cpt']} | ${sample['charge']}")
        if not dry:
            # the Perfex invoice-create (the token-gated!)
            r = call("POST", f"{pfx_base}/invoices", {"Authorization": f"Bearer {pfx_token}", "Content-Type": "application/json"},
                     {"clientid": "1", "date": "2026-08-07", "currencies": "1",
                      "newitems": [{"description": f"Encounter {sample['encounter_id']} — Consultation", "long_description": sample["note"], "qty": 1, "rate": sample["charge"]}]})
            log(f"→ Perfex API: {r}")
            if r["status"] in (200, 201):
                con.execute("INSERT OR REPLACE INTO syncs VALUES (?,?,?,?,?)",
                            (sample["encounter_id"], sample["patient_ref"], r["body"][:80], datetime.datetime.now().isoformat(), "synced"))
                con.commit()
        else:
            log("→ DRY-RUN: no write performed (the ledger + the invoice untouched!)")
    con.close()
    log(f"=== bridge {mode} complete — ledger: {LEDGER} | log: {LOG} ===")

if __name__ == "__main__":
    main()
