#!/usr/bin/env python3
"""CE Broker Web Services sync for the CME logbook (dry-run by default).
Creds: CE_BROKER_ID_PARENT_PROVIDER + CE_BROKER_UPLOAD_KEY in .env 0600.
Usage: python3 cme-cebroker-sync.py [--send]
"""
import json, sys, urllib.request, urllib.parse, os

ENV = "/opt/data/profiles/nura/.env"
LOGBOOK = "/opt/data/profiles/nura/data/cme/cme-logbook.json"

def env(name):
    try:
        for line in open(ENV):
            if line.startswith(name + "="):
                return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

def main():
    send = "--send" in sys.argv
    try:
        log = json.load(open(LOGBOOK))
    except Exception as e:
        print("logbook error:", e); sys.exit(1)
    entries = [e for e in log.get("entries", []) if e.get("status") == "confirmed" and not e.get("cme_broker_id")]
    print(f"confirmed entries pending CE Broker: {len(entries)}")
    if not entries:
        print("nothing to sync"); return
    for e in entries:
        cat = e.get("category", "II")
        creds = e.get("credits", e.get("credits_est", "?"))
        print(f"  would post: {e['date']} Cat{cat} {e['activity']} '{e['topic']}' "
              f"({creds} credits, {'PAID ' + str(e.get('cost','')) if e.get('paid') else 'free'}) "
              f"license={e.get('license', 'FL-PA-PENDING')}" + (" [SEND]" if send else " [DRY-RUN]"))
    if send:
        # build Trans XML per CE Broker schema; POST to endpoint; parse Return Receipt;
        # store returned ID in entry['cme_broker_id']; update logbook.
        print("SEND path: endpoint + schema required from CE Broker testing docs first.")

if __name__ == "__main__":
    main()
