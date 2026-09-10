#!/usr/bin/env python3
"""Offline test suite for the Drive organizer's classification engine (no Drive access needed)."""
import json, sys, importlib.util
from collections import defaultdict

spec = importlib.util.spec_from_file_location("org", "/opt/data/drive-organizer/drive_organizer.py")
org = importlib.util.module_from_spec(spec)
sys.modules["org"] = org
spec.loader.exec_module(org)

PASS = FAIL = 0
def check(label, got, want_substr):
    global PASS, FAIL
    ok = want_substr.lower() in str(got).lower()
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    if ok: PASS += 1
    else:
        FAIL += 1
        print(f"         expected ~{want_substr!r}  got {got!r}")

print("=== 1. TAXONOMY ===")
tax = org.TAXONOMY
print(f"  top-level: {len(tax)} sections")
check("01 has 7 companies", len(tax['01 — COMPANIES']['_companies']), "7")
check("Nuratech extras exist", len(tax['01 — COMPANIES']['_per_company_extras']['Nuratech AI']), "14")
check("Medisun extras exist", len(tax['01 — COMPANIES']['_per_company_extras']['Medisun Health Group']), "17")

print("\n=== 2. CLASSIFIER ROUTING ===")
cases = [
    ("2026-09-10 — Medisun — MIH — Community Paramedic Clinical Guidelines — Draft",
     "01 — COMPANIES/Medisun"),
    ("CarePilot Architecture v3", "Care Pilot"),
    ("Orthanc PACS dicom config notes", "Orthanc"),
    ("Mirth HL7 FHIR interface spec", "Mirth"),
    ("Solis HEDIS Stars gap report", "HEDIS"),
    ("RAF risk adjustment hcc mapping", "Risk Adjustment"),
    ("2026-09-01 — Garrido — Legal — FCRA Evidence Index", "LEGAL"),
    ("Smith v. Jones Complaint filed", "03 — LEGAL"),
    ("FAA flight plan PA-32R instrument rating", "Aviation"),
    ("DEA license renewal DEA number", "SENSITIVE"),
    ("Hermes agent skills inventory", "Hermes"),
    ("NURA ERP module spec", "Nura ERP"),
    ("unknown gibberish zzz", "INBOX"),
]
for name, want in cases:
    f = {"id": "x", "name": name, "mimeType": "application/pdf", "size": "100", "parents": []}
    s = org.detect_sensitive(f)
    if s:
        got = "SENSITIVE: " + ",".join(s)
    elif want.endswith("SENSITIVE"):
        got = "SENSITIVE: " + ",".join(s) if s else "NOT-FLAGGED"
    else:
        got = org.classify(f)["dest"]
    check(name[:52], got, want)

print("\n=== 3. DUPLICATE DETECTION ===")
size_i = defaultdict(int); name_i = defaultdict(int)
for n in ["Report Final.pdf", "Report Final (1).pdf", "Report Final Copy.pdf"]:
    size_i[(n.lower(), "500")] += 1
    name_i[n.lower().replace(".pdf", "")] += 1
for n, want in [("Report Final (1).pdf", "dup"), ("Report Final Copy.pdf", "dup"),
                ("Totally Unique Name.pdf", "not-dup")]:
    f = {"name": n, "size": "500"}
    d, why = org.is_dup_candidate(f, size_i, name_i)
    got = "dup" if d else "not-dup"
    check(f"{n[:40]}", got, want)

print("\n=== 4. SENSITIVE DETECTION ===")
for n, want in [("patient chart MRN 12345.pdf", "PHI"),
                ("bank account number routing.rtf", "Banking"),
                ("api key secrets env.txt", "Credentials"),
                ("attorney-client privileged memo", "Privileged"),
                ("personnel file performance review", "Employment"),
                ("vacation photos.jpg", "NONE")]:
    s = org.detect_sensitive({"name": n})
    got = ",".join(s) if s else "NONE"
    check(n[:42], got, want)

print("\n=== 5. RENAME PROTECTION ===")
for n, want in [("Court Order final.pdf", "True"), ("Executed Contract.pdf", "True"),
                ("random notes.docx", "False")]:
    check(n[:40], org.protected_from_rename({"name": n}), want)

print("\n=== 6. NAMING STANDARD ===")
ns = org.naming_standard({"name": "Report Final Final (1).pdf", "modifiedTime": "2026-09-04T10:00:00Z"})
print(f"  output: {ns}")
check("date prefix", ns, "2026-09-04")
check("strips noise", ns, "Unclassified")

print(f"\n{'='*46}\nRESULT: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
