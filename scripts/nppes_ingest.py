#!/usr/bin/env python3
"""The NPPES-ingestion — the CMS-registry → the paperclip-Postgres (the founder's-pipeline-adapted!)."""
import os, sys, time, json, urllib.request

DB_HOST = os.getenv("DB_HOST", "72.60.163.140")
DB_NAME = os.getenv("DB_NAME", "paperclip")
DB_USER = os.getenv("DB_USER", "paperclip")
CMS = "https://npiregistry.cms.hhs.gov/api/?version=2.1"

def fetch(state, limit=200, skip=0):
    url = f"{CMS}&enumeration_type=NPI-1&state={state}&limit={limit}&skip={skip}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.loads(r.read()).get("results", [])
    except Exception as e:
        print(f"[!] {e}")
        return []

def parse(item):
    basic = item.get("basic", {})
    addr = next((a for a in item.get("addresses", []) if a.get("address_purpose") == "LOCATION"), {})
    tax = next((t for t in item.get("taxonomies", []) if t.get("primary")), (item.get("taxonomies") or [{}])[0])
    return (str(item.get("number")), "1", (basic.get("first_name") or "")[:100], (basic.get("last_name") or "")[:100],
            None, (basic.get("credential") or "")[:50], (tax.get("code") or "")[:10], (tax.get("desc") or "")[:255],
            (addr.get("address_1") or "")[:255], (addr.get("city") or "")[:100], (addr.get("state") or "")[:2],
            (addr.get("postal_code") or "")[:20], (addr.get("telephone_number") or "")[:25],
            (tax.get("license") or "")[:50], (tax.get("state") or "")[:2], True)

def upsert(records):
    if not records:
        return 0
    vals = ",".join("(" + ",".join(["'" + str(x).replace("'", "''") + "'" if x is not None else "NULL" for x in r]) + ")" for r in records)
    sql = f"""INSERT INTO nppes_registry (npi, entity_type, first_name, last_name, organization_name, credential,
        primary_taxonomy, taxonomy_desc, practice_address_line1, practice_address_city, practice_address_state,
        practice_address_postal_code, practice_address_phone, state_license_number, state_license_state, is_active)
        VALUES {vals} ON CONFLICT (npi) DO UPDATE SET first_name=EXCLUDED.first_name, last_name=EXCLUDED.last_name,
        credential=EXCLUDED.credential, taxonomy_desc=EXCLUDED.taxonomy_desc, updated_at=CURRENT_TIMESTAMP"""
    open("/tmp/nppes_sql.txt", "w").write(sql)
    return len(records)

def main():
    state = sys.argv[1] if len(sys.argv) > 1 else "FL"
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    print(f"[*] NPPES-ingest: {state} (target {target})")
    total, skip = 0, 0
    while total < target and skip <= 1000:
        rows = fetch(state, 200, skip)
        if not rows:
            break
        parsed = [parse(r) for r in rows]
        upsert(parsed)
        total += len(parsed)
        skip += 200
        time.sleep(1)
    print(f"[✓] staged {total} FL records → the psql-load-file (/tmp/nppes_sql.txt!)")

if __name__ == "__main__":
    main()
