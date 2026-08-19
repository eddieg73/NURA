#!/usr/bin/env python3
"""Forensic case intake — sealed workspace creator (MLR division, 2026-08-02).
Creates a case folder under /opt/data/legal-cases (0700, OUTSIDE RAG/vault),
a non-PHI manifest, and drops OCR/report templates.
Usage: python3 forensic-case-intake.py CASE-001 "People v. X" "capital murder"
"""
import json
import os
import sys
from datetime import date

ROOT = "/opt/data/legal-cases"

def main():
    case_id = sys.argv[1] if len(sys.argv) > 1 else f"CASE-{date.today():%Y%m%d}"
    name = sys.argv[2] if len(sys.argv) > 2 else "UNNAMED"
    matter = sys.argv[3] if len(sys.argv) > 3 else "medical-forensic review"
    d = os.path.join(ROOT, case_id)
    os.makedirs(os.path.join(d, "source"), exist_ok=True)
    os.makedirs(os.path.join(d, "ocr"), exist_ok=True)
    os.makedirs(os.path.join(d, "analysis"), exist_ok=True)
    os.makedirs(os.path.join(d, "reports"), exist_ok=True)
    os.chmod(d, 0o700)
    manifest = {
        "case_id": case_id, "matter": matter, "client": "Attorney Alex Stavrou (privileged)",
        "created": str(date.today()), "status": "intake",
        "privilege": "attorney-client + work-product",
        "files": [], "findings": [], "reports": [],
    }
    with open(os.path.join(d, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Case workspace: {d}")
    print("Drop source docs into source/ — I'll OCR + build the chronology.")

if __name__ == "__main__":
    main()
