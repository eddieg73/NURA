#!/usr/bin/env python3
"""Load Ensure MRA flat-file CSV into solis_hermes (tenant solis-msl).
Members upserted by (last, first, dob); hcc_opportunities rows with provenance."""
import csv, sys, os, subprocess, datetime
import psycopg2

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/solis-reports/MRA_Open_Cond_MRAExportFlatFile.csv"

ip = subprocess.run(["docker", "inspect", "-f",
    "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
    "mirth-oie-postgres-db-1"], capture_output=True, text=True).stdout.strip()
creds = {}
for line in open("/docker/mirth-connect/.env.oie"):
    if line.strip() and not line.startswith("#") and "=" in line:
        k, v = line.strip().split("=", 1); creds[k] = v
conn = psycopg2.connect(f"postgresql://{creds.get('PG_USER','mirth')}:{creds.get('PG_PASS','')}@{ip}:5432/solis_hermes")

STATUS_MAP = {
    "CMS Open": "RECAPTURE REQUIRED",
    "EMR Open": "SUSPECTED",
    "CMS Closed": "CODED",
    "EMR Documented": "DOCUMENTED",
}

def parse_dob(s):
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try: return datetime.datetime.strptime(s, fmt).date()
        except ValueError: pass
    return None

n_mem = n_opp = 0
with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        name = (row.get("Patient Name") or "").strip()
        dob = parse_dob(row.get("DOB") or "")
        member_nbr = (row.get("MemberNbr") or "").strip()
        if not name:
            continue
        parts = [p.strip() for p in name.split(",")]
        last, first = parts[0], (parts[1] if len(parts) > 1 else "")
        cur = conn.cursor()
        cur.execute("SELECT id FROM members WHERE last_name=%s AND first_name=%s AND dob=%s",
                    (last, first, dob))
        m = cur.fetchone()
        if not m:
            cur.execute("INSERT INTO members (tenant_id, first_name, last_name, dob, pcp_npi)"
                        " VALUES ('solis-msl', %s, %s, %s, %s) RETURNING id",
                        (first, last, dob, (row.get("PCP") or "")[:20]))
            mid = cur.fetchone()[0]
            cur.execute("INSERT INTO member_identifiers (member_id, system, value) VALUES (%s,'SOLIS',%s)",
                        (mid, member_nbr))
            n_mem += 1
        else:
            mid = m[0]
        status_desc = (row.get("Status Description") or "").strip()
        st = STATUS_MAP.get(status_desc, "REQUIRES_PROVIDER_REVIEW")
        evidence_json = (f'{{"claims": true, "source_status": "{status_desc}", '
                         f'"hcc": "{row.get("HCC")}", "model": "{row.get("MRA Version")}", '
                         f'"period": "{row.get("Period")}", "mra": "{row.get("MRA")}"}}')
        hcc_desc = (row.get("HCC Description") or "").strip()
        if not hcc_desc:
            cur.close(); continue
        cur.execute("""INSERT INTO hcc_opportunities
            (member_id, tenant_id, condition, evidence, status, source, source_record, rule_version)
            VALUES (%s,'solis-msl',%s,%s,%s,'ENSURE-MRA',%s,'ensure-flatfile-2026-1')""",
            (mid, hcc_desc[:200], evidence_json, st, f"hcc:{row.get('HCC')}|patient:{member_nbr}"))
        n_opp += 1
        cur.close()
conn.commit()
print(f"members upserted: {n_mem} | hcc_opportunities inserted: {n_opp}")
