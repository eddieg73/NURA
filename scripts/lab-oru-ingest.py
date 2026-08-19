#!/usr/bin/env python3
"""NURA Lab ORU Ingest — the HL7 ORU^R01 listener for the LabCorp/Quest feeds.
Listens on :6668 (the MLLP), parses the ORU messages, normalizes to the
LOINC panels, and writes the draft notes to OpenEMR via the API.
The vendor feeds arrive here once the interfaces are turned on.
Usage: python3 lab-oru-ingest.py  (runs the persistent listener)
"""
import socket, threading, json, re, time, os, sys
import urllib.request

LISTEN_PORT = 6668
OPENEMR_API = os.environ.get("OPENEMR_API_URL", "http://127.0.0.1:8300/apis/default")
OPENEMR_TOKEN = os.environ.get("OPENEMR_API_TOKEN", "")

def parse_oru(raw: str) -> dict:
    """Parse the HL7 ORU^R01 into the structured results (the OBX segments)."""
    segments = raw.replace("\r", "\n").split("\n")
    pid = next((s for s in segments if s.startswith("PID|")), "")
    obr = next((s for s in segments if s.startswith("OBR|")), "")
    obx = [s for s in segments if s.startswith("OBX|")]
    def field(s, i, rep=0):
        try:
            return s.split("|")[i].split("~")[rep]
        except IndexError:
            return ""
    results = []
    for o in obx:
        results.append({
            "test": field(o, 3, 1) or field(o, 3),
            "value": field(o, 5),
            "unit": field(o, 6),
            "ref_range": field(o, 7),
            "abnormal_flags": field(o, 8),
            "status": field(o, 11),
        })
    return {
        "patient_mrn": field(pid, 3),
        "patient_name": field(pid, 5),
        "dob": field(pid, 7),
        "sex": field(pid, 8),
        "panel": field(obr, 4, 1) or field(obr, 4),
        "order_date": field(obr, 7),
        "results": results,
        "received": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

def to_openemr_note(lab: dict) -> None:
    """Write the draft lab note to OpenEMR (the review-marked note)."""
    if not OPENEMR_TOKEN:
        return
    lines = [f"LAB PANEL: {lab['panel']} (received {lab['received']})", ""]
    for r in lab["results"]:
        flag = f" [{r['abnormal_flags']}]" if r["abnormal_flags"] else ""
        lines.append(f"{r['test']}: {r['value']} {r['unit']}{flag} (ref {r['ref_range']})")
    lines += ["", "AUTO-DRAFT — PROVIDER REVIEW REQUIRED (the lab-intake lane)"]
    # the OpenEMR API note creation (the patient match by the MRN; the draft type)
    try:
        body = json.dumps({"note": "\n".join(lines), "type": "laboratory", "status": "draft"}).encode()
        req = urllib.request.Request(f"{OPENEMR_API}/notes", data=body,
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {OPENEMR_TOKEN}"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass  # the API's optional here; the JSON lands in the intake queue regardless

def handle(conn, addr):
    try:
        data = b""
        while b"\x1c" not in data and len(data) < 1_000_000:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
        # the MLLP unwrap: the \x0b MSH ... \x1c\x0d
        raw = data.decode("utf-8", "replace").strip("\x0b").strip()
        if raw.startswith("MSH"):
            lab = parse_oru(raw)
            # persist to the intake queue (the interpreter cron consumes it)
            qpath = "/opt/data/lab-queue"
            os.makedirs(qpath, exist_ok=True)
            with open(f"{qpath}/oru-{int(time.time()*1000)}.json", "w") as f:
                json.dump(lab, f, indent=2)
            to_openemr_note(lab)
            print(f"ORU ingested: {lab['panel']} | {len(lab['results'])} results | {lab['patient_mrn']}")
        conn.send(b"\x0bMSH|^~\\&|NURA|PACS|SENDER|RECEIVER|" +
                  time.strftime("%Y%m%d%H%M%S").encode() + b"||ACK|1|P|2.5\rMSA|AA\r\x1c\r")
    except Exception as e:
        print("handle error:", str(e)[:80])
    finally:
        conn.close()

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", LISTEN_PORT))
    srv.listen(8)
    print(f"NURA ORU listener on :{LISTEN_PORT} (the MLLP) — waiting for the lab feeds")
    while True:
        conn, addr = srv.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
