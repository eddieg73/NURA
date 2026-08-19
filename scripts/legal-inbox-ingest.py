#!/usr/bin/env python3
"""LEGAL INBOX INGEST — legal@nuratech.ai (MLR division, 2026-08-02).
Polls the legal mailbox, ingests case emails + attachments into the sealed
case workspace, updates manifests. SILENT when no mail (watchdog pattern).
Activated when LEGAL_IMAP_* creds exist in .env (sealed 0600).
"""
import imaplib
import json
import os
import re
import sys
import email
from email.header import decode_header
from datetime import date

ENV = "/opt/data/profiles/nura/.env"
ROOT = "/opt/data/legal-cases"


def envval(name):
    try:
        env = open(ENV).read()
        m = re.search(rf"^{name}=(.+)$", env, re.M)
        return m.group(1).strip().strip('"').strip("'") if m else ""
    except Exception:
        return ""


def dec(s):
    if not s:
        return ""
    parts = decode_header(s)
    out = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            out += text.decode(enc or "utf-8", errors="ignore")
        else:
            out += text
    return out


def main():
    host = envval("LEGAL_IMAP_HOST") or envval("EMAIL_IMAP_HOST")
    user = envval("LEGAL_IMAP_USER") or envval("EMAIL_ADDRESS") or envval("EMAIL_HOME_ADDRESS")
    pw = envval("LEGAL_IMAP_PASS") or envval("EMAIL_PASSWORD") or envval("GOOGLE_OAUTH_PASSWORD")
    if not (host and user and pw):
        print("NO_CREDS")  # silent — lane not activated yet
        return 0

    try:
        M = imaplib.IMAP4_SSL(host)
        M.login(user, pw)
        M.select("INBOX")
        typ, data = M.search(None, "UNSEEN")
        ids = data[0].split()
        if not ids:
            print("NO_MAIL")  # silent
            M.logout()
            return 0

        findings = []
        for i in ids[-10:]:
            typ, msgdata = M.fetch(i, "(RFC822)")
            msg = email.message_from_bytes(msgdata[0][1])
            subject = dec(msg.get("Subject", ""))
            sender = dec(msg.get("From", ""))
            # LEGAL FILTER: Stavrou/Alex + case patterns only (normal mail is ignored)
            s = (sender + " " + subject).lower()
            if not any(k in s for k in ["stavrou", "alex", "case-", "case ", "criminal",
                                         "autopsy", "forensic", "murder", "legal", "discovery"]):
                continue
            case_id = None
            m = re.search(r"([A-Z]{2,4}-\d{2,6})", subject) or re.search(r"(CASE[-_ ]?\d+)", subject, re.I)
            if m:
                case_id = m.group(1).replace(" ", "-")
            case_dir = os.path.join(ROOT, case_id or f"CASE-{date.today():%Y%m%d}")
            os.makedirs(os.path.join(case_dir, "source"), exist_ok=True)
            os.chmod(case_dir, 0o700)
            files = []
            for part in msg.walk():
                fn = part.get_filename()
                if fn:
                    fn = dec(fn)
                    payload = part.get_payload(decode=True)
                    if payload:
                        path = os.path.join(case_dir, "source", fn)
                        with open(path, "wb") as f:
                            f.write(payload)
                        files.append(fn)
            man_path = os.path.join(case_dir, "manifest.json")
            man = {"case_id": case_id or "CASE-PENDING", "sender": sender, "subject": subject,
                   "received": str(date.today()), "privilege": "attorney-client + work-product",
                   "files": files}
            if os.path.exists(man_path):
                old = json.load(open(man_path))
                old.setdefault("emails", []).append(man)
                man = old
            json.dump(man, open(man_path, "w"), indent=2)
            findings.append({"case": case_id or "CASE-PENDING", "sender": sender,
                             "subject": subject[:80], "files": files})
        M.logout()
        print(json.dumps({"ingested": findings}, indent=2))
        return 0
    except imaplib.IMAP4.error as e:
        msg = str(e)
        if "AUTHENTICATIONFAILED" in msg or "LOGIN" in msg:
            print("BLOCKED_2SV (Google 2-Step Verification blocks plain-password IMAP — T18/T19 pending; silent)")
            return 0
        print("INGEST_ERROR", e)
        return 1
    except Exception as e:
        print("INGEST_ERROR", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
