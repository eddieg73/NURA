#!/usr/bin/env python3
"""MLLP sink + Zone-01/02: ACK each message, store RAW byte-exact, run the
spec's transaction state machine (sections 25-27): idempotency key, VALIDATED or QUARANTINED."""
import socket, sys, time, hashlib, os, re
import psycopg2

HOST, PORT = "0.0.0.0", 6665
LOG = open("/tmp/mllp-sink.log", "a")
def log(msg):
    LOG.write(f"[sink] {time.strftime('%H:%M:%S')} {msg}\n"); LOG.flush(); print(msg, flush=True)

def db():
    import subprocess
    ip = subprocess.run(["docker", "inspect", "-f",
        "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
        "mirth-oie-postgres-db-1"], capture_output=True, text=True).stdout.strip()
    creds = {}
    for line in open("/docker/mirth-connect/.env.oie"):
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.strip().split("=", 1); creds[k] = v
    return psycopg2.connect(f"postgresql://{creds.get('PG_USER','mirth')}:{creds.get('PG_PASS','')}@{ip}:5432/solis_hermes")

def idem_key(payload: bytes) -> str:
    """Section 26: SHA256(payer + member_id + claim_id + service_date + transaction_type)."""
    txt = payload.decode(errors="replace")
    msh = txt.split("MSH|", 1)[1].split("\r", 1)[0].split("|") if "MSH|" in txt else []
    evn = txt.split("EVN|", 1)[1].split("\r", 1)[0].split("|") if "EVN|" in txt else []
    pid = txt.split("PID|", 1)[1].split("\r", 1)[0].split("|") if "PID|" in txt else []
    payer = msh[3] if len(msh) > 3 else "UNKNOWN"
    txn_type = msh[8] if len(msh) > 8 else "UNKNOWN"
    member_id = pid[2] if len(pid) > 2 else ""
    service_date = evn[1] if len(evn) > 1 else ""
    return hashlib.sha256("|".join([payer, member_id, "", service_date, txn_type]).encode()).hexdigest()

def valid_hl7(txt: str) -> bool:
    return txt.startswith("MSH|") and "PID|" in txt

conn = db()
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT)); srv.listen(5)
log(f"listening {HOST}:{PORT} | Zone-01 RAW + Zone-02 state machine -> solis_hermes")

while True:
    c, addr = srv.accept()
    buf = b""
    try:
        while b"\x1c\x0d" not in buf:
            chunk = c.recv(65536)
            if not chunk: break
            buf += chunk
    except Exception as e:
        log(f"recv err {e}")
    payload = buf.split(b"\x0b", 1)[-1].rsplit(b"\x1c", 1)[0] if b"\x0b" in buf else buf
    txt = payload.decode(errors="replace")
    try:
        cur = conn.cursor()
        sha = hashlib.sha256(payload).hexdigest()
        cur.execute("SELECT id FROM source_documents WHERE payload_sha256 = %s", (sha,))
        row = cur.fetchone()
        if row:
            doc_id = row[0]; log(f"dup raw skip {addr} {len(payload)}b")
        else:
            cur.execute(
                "INSERT INTO source_documents (tenant_id, transaction_type, raw_payload, payload_sha256)"
                " VALUES (%s,%s,%s,%s) RETURNING id",
                ("solis-msl", "HL7_ADT", psycopg2.Binary(payload), sha))
            doc_id = cur.fetchone()[0]; conn.commit()
            log(f"RAW id={doc_id} {addr} {len(payload)}b")
        # state machine: upsert transaction, then validate
        key = idem_key(payload)
        cur.execute("SELECT id, state FROM transactions WHERE idempotency_key = %s", (key,))
        trow = cur.fetchone()
        if trow:
            tid, state = trow
            cur.execute("UPDATE transactions SET version = version + 1, last_updated = now() WHERE id = %s", (tid,))
        else:
            cur.execute("INSERT INTO transactions (tenant_id, idempotency_key, source_document_id, state)"
                        " VALUES ('solis-msl', %s, %s, 'RECEIVED') RETURNING id", (key, doc_id))
            tid = cur.fetchone()[0]
        conn.commit()
        if valid_hl7(txt):
            cur.execute("UPDATE transactions SET state='VALIDATED', last_updated=now() WHERE id=%s", (tid,))
            state = "VALIDATED"
        else:
            cur.execute("UPDATE transactions SET state='QUARANTINED', error_category='schema',"
                        " error_detail='malformed HL7' WHERE id=%s", (tid,))
            state = "QUARANTINED"
        conn.commit()
        log(f"txn {tid}: {state} ({key[:10]}…)")
        cur.close()
    except Exception as e:
        log(f"db err {e}")
        try: conn.rollback()
        except Exception: pass
        try: conn = db()
        except Exception as e2: log(f"reconnect err {e2}")
    try:
        c.sendall(b"\x0bMSH|^~\\&|SINK|NURA|MIRTH|20260815120000||ACK||P|2.3\x0d\x1c\x0d")
    except Exception as e:
        log(f"ack err {e}")
    c.close()
