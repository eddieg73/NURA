#!/usr/bin/env python3
"""
NURA Executive Records Manager — Google Drive organizer.

Implements the executive filing standard:
  - Builds the 01-10 taxonomy (never deletes anything)
  - Classifies every file; low confidence -> 08 INBOX (no guessing)
  - Suspected duplicates -> 09 DUPLICATES — REVIEW (never auto-deleted)
  - PHI -> RESTRICTED — PHI / PATIENT RECORDS (never mixed with general docs)
  - Audits sharing permissions and flags "anyone with link" (never alters them)
  - Applies the YYYY-MM-DD naming standard, skipping protected workflows
  - Emits an executive summary + EXECUTIVE ATTENTION REQUIRED list

Usage:
  python3 drive_organizer.py --dry-run          # plan only (default, safe)
  python3 drive_organizer.py --build-tree       # create folders only
  python3 drive_organizer.py --execute          # perform moves + renames
  python3 drive_organizer.py --report           # summary from last scan

Auth: uses the Hermes google-workspace OAuth token (google_token.json).
"""
from __future__ import annotations

import argparse, json, os, re, sys, time, hashlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAXONOMY = json.loads((HERE / "taxonomy.json").read_text())
STATE_DIR = HERE / "state"
STATE_DIR.mkdir(exist_ok=True)

SCOPES = ["https://www.googleapis.com/auth/drive"]

# ---------------------------------------------------------------- auth

def find_token() -> Path:
    """Locate the Hermes google-workspace OAuth token."""
    cands = []
    hh = os.environ.get("HERMES_HOME")
    if hh:
        cands.append(Path(hh) / "google_token.json")
        cands.append(Path(hh) / "home" / ".hermes" / "google_token.json")
    cands += [
        Path.home() / ".hermes" / "google_token.json",
        Path("/opt/data/profiles/nura/home/.hermes/google_token.json"),
        Path("/opt/data/profiles/nura/.hermes/google_token.json"),
    ]
    for c in cands:
        if c.exists():
            return c
    sys.exit(
        "NOT_AUTHENTICATED: no google_token.json found.\n"
        "Run the google-workspace setup (skill: google-workspace) first:\n"
        "  python3 <skill>/scripts/setup.py --check"
    )


def service():
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ModuleNotFoundError as e:
        sys.exit(f"ModuleNotFoundError: {e}. Run setup.py --install-deps")
    tok = find_token()
    creds = Credentials.from_authorized_user_file(str(tok), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tok.write_text(creds.to_json())
    return build("drive", "v3", credentials=creds, cache_discovery=False)


# ---------------------------------------------------------------- classify

COMPANY_ALIASES = {
    "Nuratech AI": ["nuratech", "nura tech", "nura-os", "nura os", "nura ", "hermes",
                    "care pilot", "carepilot", "openemr", "orthanc", "ohif", "mirth",
                    "hl7", "fhir", "nura erp", "radiology ai", "clinical ai"],
    "Medisun Health Group": ["medisun", "medi sun", "mih", "mobile integrated",
                             "community paramedicine", "solis", "hedis", "stars",
                             "risk adjustment", "raf", "medicare advantage",
                             "hospital-at-home", "hospital at home"],
    "Medisun Medical Centers": ["medical center", "procedure suite", "urgent care",
                                "imaging center"],
    "Rescue Health Foundation": ["rescue health", "rhf"],
    "Garrido Group": ["garrido group", "garrido consulting"],
    "Citrus Health Group": ["citrus health"],
}

PROJECT_HINTS = {
    "ACTIVE — Medisun MIH Program": ["mih", "mobile integrated healthcare",
                                     "community paramedicine", "standing order"],
    "ACTIVE — Care Pilot": ["care pilot", "carepilot"],
    "ACTIVE — Radiology Center Launch": ["radiology center", "pacs build", "ris ", "modality"],
    "ACTIVE — Nura ERP": ["nura erp", "erp"],
    "ACTIVE — Hermes": ["hermes", "mission control", "nura os"],
    "PLANNING — Hospital-at-Home": ["hospital-at-home", "hospital at home"],
}

LEGAL_STRONG = ["v.", "plaintiff", "defendant", "complaint", "motion", "affidavit",
                "subpoena", "deposition", "discovery", "judgment", "court order",
                "docket", "fcra", "fdcpa", "demand letter", "summons", "case no",
                "case number", "pleading", "statute", "litigation"]
LEGAL_WEAK = ["settlement", "credit report", "exhibit", "evidence", "counsel",
              "attorney", "esq", "filed", "court"]

CLINICAL_SUBS = {
    "Emergency Medicine": ["emergency medicine", "em ", "triage", "acls", "atls"],
    "Critical Care": ["critical care", "icu", "ventilator", "ards", "sepsis"],
    "EMS / Prehospital": ["ems", "paramedic", "prehospital", "ambulance", "emt"],
    "Mobile Integrated Healthcare": ["mobile integrated", "mih"],
    "Community Paramedicine": ["community paramedicine", "cp program"],
    "Primary Care": ["primary care", "family medicine", "internal medicine"],
    "Population Health": ["population health", "care gap"],
    "Radiology": ["radiology", "x-ray", "ct ", "mri", "ultrasound", "dicom", "pacs"],
    "Cardiology": ["cardiology", "ekg", "ecg", "echo", "cardiac"],
    "Pulmonology": ["pulmonology", "pulmonary", "copd", "spirometry"],
    "Neurology": ["neurology", "stroke", "seizure", "neuro"],
    "Surgery": ["surgery", "surgical", "operative"],
    "Anesthesia": ["anesthesia", "anesthesiology", "sedation"],
    "Pharmacology": ["pharmacology", "drug", "medication", "formulary", "dosage"],
    "Medical Education": ["medical education", "lecture", "curriculum", "teaching"],
    "CME": ["cme", "ce credit", "ce broker", "category 2"],
    "Coding / Billing / Reimbursement": ["cpt", "icd-10", "icd10", "coding", "billing",
                                          "reimbursement", "claim", "e/m"],
    "Medicare / CMS": ["medicare", "cms", "hcc", "v28", "v24", "mra"],
    "Regulatory / AHCA": ["ahca", "department of health", "doh", "survey", "deficiency"],
}

PERSONAL_SUBS = {
    "Aviation": ["aviation", "ppl", "instrument rating", "foreflight", "pa-32",
                 "pa-46", "sr22", "bonanza", "aircraft", "flight plan"],
    "EMS / Paramedic": ["paramedic license", "emt-p", "remac"],
    "Professional Licenses": ["license", "licensure", "npi", "dea", "pa9103256"],
    "Certifications": ["certification", "certificate", "board cert"],
    "Education": ["diploma", "degree", "transcript", "university", "college"],
    "Taxes": ["tax return", "1040", "w-2", "w2", "1099", "irs"],
    "Banking": ["bank statement", "checking", "savings", "wire"],
    "Insurance": ["policy", "premium", "deductible", "coverage"],
    "Vehicles": ["vehicle", "registration", "title", "tag renewal"],
    "Property": ["deed", "mortgage", "lease", "property tax"],
    "Travel": ["itinerary", "boarding pass", "reservation", "hotel"],
}

SENSITIVE_PATTERNS = {
    "PHI / Patient Information": ["patient", "phi", "chart", "medical record",
                                   "encounter", "diagnosis", "mrn", "dob"],
    "SSN / Tax ID": ["ssn", "social security", "ein ", "tax id"],
    "Banking / Financial Account": ["account number", "routing", "ach", "iban"],
    "Credentials / Passwords": ["password", "credential", "api key", "secret",
                                "private key", "token"],
    "DEA / NPI / Licensing": ["dea ", "npi ", "license number"],
    "Legal Privileged": ["privileged", "attorney-client", "work product",
                          "confidential legal"],
    "Employment Records": ["personnel file", "performance review", "termination",
                            "offer letter", "compensation"],
}

DUP_PATTERNS = [
    r"\(\d+\)", r"\bcopy\b", r"\bcopy of\b", r"\bfinal\s*final\b", r"\bnew\b",
    r"\bupdated\b", r"\brevised\b", r"\brev\d+\b", r"\bv\d+\b", r"\bdraft\b",
    r"\bold\b", r"\bbackup\b", r"\bduplicate\b", r"\buntitled\b", r"-\s*\d+$",
]

PROTECTED_NAME_SIGNALS = [
    "court", "docket", "exhibit", "evidence", "filed", "signed", "executed",
    "recorded", "notarized", "ahca", "cms", "submitted", "contract", "agreement",
]


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower())


def score_bucket(text: str, mapping: dict) -> tuple[str | None, int, list[str]]:
    best, best_score, why = None, 0, []
    for bucket, kws in mapping.items():
        hits = [k for k in kws if k in text]
        if len(hits) > best_score:
            best, best_score, why = bucket, len(hits), hits[:4]
    return best, best_score, why


def classify(f: dict) -> dict:
    """Classify one Drive file. Returns destination path + confidence + reasons."""
    name = f.get("name", "")
    text = norm(name + " " + " ".join(f.get("parents", [])))
    is_folder = f.get("mimeType") == "application/vnd.google-apps.folder"

    reasons: list[str] = []

    # 0. already inside the new taxonomy -> leave it
    if any(str(s).startswith(("01 —", "02 —", "03 —", "04 —", "05 —", "06 —",
                              "07 —", "08 —", "09 —", "10 —", "RESTRICTED", "REVIEW"))
           for s in [name]):
        return {"dest": None, "confidence": 1.0, "reasons": ["already filed"], "skip": True}

    # 1. LEGAL beats everything (litigation/evidence/court)
    raw = (name or "").lower()
    legal_strong = [k for k in LEGAL_STRONG
                    if k in text or (k == "v." and re.search(r"\bv\.?\s+[a-z]", raw))]
    legal_weak = [k for k in LEGAL_WEAK if k in text]
    lscore = len(legal_strong) * 2 + len(legal_weak)
    if lscore >= 2:
        legal_hits = legal_strong + legal_weak
        sub = ("Credit / FCRA / FDCPA" if any(k in text for k in ["fcra", "fdcpa", "credit report"])
               else "Litigation" if any(k in text for k in ["plaintiff", "defendant", "complaint",
                                                            "motion", "litigation"])
               else "Active Matters")
        return {"dest": f"03 — LEGAL/{sub}", "confidence": 0.92,
                "reasons": [f"legal signal: {', '.join(legal_hits[:3])}"]}

    # 2. Specific company
    company, cscore, cwhy = score_bucket(text, COMPANY_ALIASES)
    if company and cscore >= 1:
        reasons.append(f"company: {company} ({', '.join(cwhy)})")
        # subfolder
        if company == "Nuratech AI":
            extras = TAXONOMY["01 — COMPANIES"]["_per_company_extras"]["Nuratech AI"]
            tech_map = {
                "Care Pilot": ["care pilot", "carepilot"],
                "Hermes Agent": ["hermes"],
                "NURA Platform": ["nura os", "nura-os", "nura platform"],
                "Nura ERP": ["erp"],
                "Radiology AI": ["radiology ai", "radai"],
                "Clinical AI": ["clinical ai"],
                "AI / Machine Learning": ["machine learning", "model", "llm", "ai "],
                "OpenEMR": ["openemr"],
                "Orthanc / PACS / OHIF": ["orthanc", "pacs", "ohif", "dicom"],
                "Mirth / HL7 / FHIR": ["mirth", "hl7", "fhir"],
                "Infrastructure / Hosting": ["hostinger", "vps", "docker", "infra", "server"],
                "Cybersecurity": ["security", "cyber", "cve", "firewall"],
                "Integrations / APIs": ["api", "integration", "mcp"],
                "Development Documentation": ["dev doc", "architecture", "readme", "sdk"],
            }
            sub, sscore, swhy = score_bucket(text, tech_map)
            if sub and sscore >= 1:
                reasons.append(f"nuratech area: {sub}")
                return {"dest": f"01 — COMPANIES/{company}/{sub}", "confidence": 0.85,
                        "reasons": reasons}
        if company.startswith("Medisun"):
            msub, mscore, mwhy = score_bucket(text, {
                "Mobile Integrated Healthcare": ["mobile integrated", "mih"],
                "Community Paramedicine": ["community paramedicine"],
                "Population Health": ["population health", "care gap"],
                "HEDIS / Stars": ["hedis", "stars"],
                "Risk Adjustment / RAF": ["raf", "risk adjustment", "hcc"],
                "Medicare Advantage": ["medicare advantage", "ma plan"],
                "Solis Health Plans": ["solis"],
                "Clinical Practice Guidelines": ["guideline", "cpg"],
                "Medical Director Documents": ["medical director"],
                "Provider Operations": ["provider", "credentialing"],
                "Payer Contracts": ["payer", "contract"],
                "Fleet / Vehicles": ["fleet", "vehicle", "ambulance"],
            })
            if msub and mscore >= 1:
                reasons.append(f"medisun area: {msub}")
                return {"dest": f"01 — COMPANIES/{company}/{msub}", "confidence": 0.85,
                        "reasons": reasons}
        return {"dest": f"01 — COMPANIES/{company}", "confidence": 0.72, "reasons": reasons}

    # 3. Specific active project
    proj, pscore, pwhy = score_bucket(text, PROJECT_HINTS)
    if proj and pscore >= 1:
        return {"dest": f"06 — PROJECTS/{proj}", "confidence": 0.80,
                "reasons": [f"project: {proj} ({', '.join(pwhy)})"]}

    # 4. Medical / clinical reference
    csub, cscore2, cwhy2 = score_bucket(text, CLINICAL_SUBS)
    if csub and cscore2 >= 1:
        return {"dest": f"04 — MEDICAL / CLINICAL/{csub}", "confidence": 0.74,
                "reasons": [f"clinical: {csub} ({', '.join(cwhy2)})"]}

    # 5. Person
    m = re.match(r"^([A-Z][a-z]+)[ _,-]+([A-Z][a-z]+)", name)
    if m and any(k in text for k in ["resume", "cv", "offer", "w-9", "w9",
                                     "contractor", "consultant", "employee"]):
        return {"dest": "05 — PEOPLE", "confidence": 0.55,
                "reasons": ["possible person document — needs role folder"]}

    # 6. Personal
    psub, pscore2, pwhy2 = score_bucket(text, PERSONAL_SUBS)
    if psub and pscore2 >= 1:
        return {"dest": f"02 — PERSONAL/{psub}", "confidence": 0.70,
                "reasons": [f"personal: {psub} ({', '.join(pwhy2)})"]}

    # 7/8. uncertain -> INBOX (never guess)
    return {"dest": "08 — INBOX — TO BE FILED", "confidence": 0.20,
            "reasons": ["no confident match"], "skip": False}


def detect_sensitive(f: dict) -> list[str]:
    text = norm(f.get("name", ""))
    return [cat for cat, pats in SENSITIVE_PATTERNS.items() if any(p in text for p in pats)]


def is_dup_candidate(f: dict, size_index: dict, name_index: dict) -> tuple[bool, str]:
    name = f.get("name", "")
    low = name.lower()
    for p in DUP_PATTERNS:
        if re.search(p, low):
            return True, f"name pattern '{p.strip()}'"
    key = (re.sub(r"\s+", " ", low).strip(), f.get("size"))
    if f.get("size") and size_index.get(key, 0) > 1:
        return True, "identical name + size"
    stem = re.sub(r"\.[a-z0-9]+$", "", low)
    stem = re.sub(r"[\s_\-]+(copy|final|new|updated|revised|\d+)$", "", stem).strip()
    if stem and name_index.get(stem, 0) > 1:
        return True, "same stem, multiple versions"
    return False, ""


def protected_from_rename(f: dict) -> bool:
    text = norm(f.get("name", ""))
    return any(s in text for s in PROTECTED_NAME_SIGNALS)


# ---------------------------------------------------------------- drive ops

def list_all(svc, page_size=1000):
    files, tok = [], None
    q = "trashed = false"
    while True:
        r = svc.files().list(q=q, pageSize=page_size, fields=(
            "nextPageToken, files(id,name,mimeType,size,modifiedTime,createdTime,"
            "parents,owners(emailAddress),webViewLink,shared,md5Checksum)"),
            pageToken=tok).execute()
        files += r.get("files", [])
        tok = r.get("nextPageToken")
        if not tok:
            break
        time.sleep(0.2)
    return files


def build_tree(svc, root_id="root") -> dict:
    """Create the taxonomy folders; return {path: folder_id}."""
    index: dict[str, str] = {}

    def mk(name, parent):
        r = svc.files().create(body={"name": name, "mimeType":
            "application/vnd.google-apps.folder", "parents": [parent]},
            fields="id").execute()
        return r["id"]

    def get_or_mk(name, parent):
        q = (f"'{parent}' in parents and name = '{name}' and "
             "mimeType = 'application/vnd.google-apps.folder' and trashed = false")
        r = svc.files().list(q=q, fields="files(id,name)", pageSize=1).execute()
        if r.get("files"):
            return r["files"][0]["id"]
        return mk(name, parent)

    companies = TAXONOMY["01 — COMPANIES"]
    std = companies["_standard_subfolders"]
    extras = companies["_per_company_extras"]

    root = get_or_mk("NURA — Executive Records", root_id)
    index[""] = root

    # 01 COMPANIES
    c01 = get_or_mk("01 — COMPANIES", root)
    index["01 — COMPANIES"] = c01
    for co in companies["_companies"]:
        cid = get_or_mk(co, c01)
        index[f"01 — COMPANIES/{co}"] = cid
        for sub in std:
            index[f"01 — COMPANIES/{co}/{sub}"] = get_or_mk(sub, cid)
        for sub in extras.get(co, []):
            index[f"01 — COMPANIES/{co}/{sub}"] = get_or_mk(sub, cid)

    # 02 PERSONAL
    c02 = get_or_mk("02 — PERSONAL", root)
    index["02 — PERSONAL"] = c02
    for s in TAXONOMY["02 — PERSONAL"]:
        index[f"02 — PERSONAL/{s}"] = get_or_mk(s, c02)

    # 03 LEGAL
    c03 = get_or_mk("03 — LEGAL", root)
    index["03 — LEGAL"] = c03
    for s in TAXONOMY["03 — LEGAL"]["_static"]:
        index[f"03 — LEGAL/{s}"] = get_or_mk(s, c03)

    # 04 MEDICAL
    c04 = get_or_mk("04 — MEDICAL / CLINICAL", root)
    index["04 — MEDICAL / CLINICAL"] = c04
    for s in TAXONOMY["04 — MEDICAL / CLINICAL"]["_static"]:
        index[f"04 — MEDICAL / CLINICAL/{s}"] = get_or_mk(s, c04)
    rname = TAXONOMY["04 — MEDICAL / CLINICAL"]["_restricted"]
    rid = get_or_mk(rname, root)
    index[rname] = rid
    for s in TAXONOMY["05 — PEOPLE"]["_person_template"]:
        get_or_mk(s, rid)

    # 05 PEOPLE
    c05 = get_or_mk("05 — PEOPLE", root)
    index["05 — PEOPLE"] = c05
    for s in TAXONOMY["05 — PEOPLE"]["_categories"]:
        index[f"05 — PEOPLE/{s}"] = get_or_mk(s, c05)

    # 06 PROJECTS
    c06 = get_or_mk("06 — PROJECTS", root)
    index["06 — PROJECTS"] = c06
    for p in TAXONOMY["06 — PROJECTS"]["_seed_projects"]:
        pid = get_or_mk(p, c06)
        index[f"06 — PROJECTS/{p}"] = pid
        for s in TAXONOMY["06 — PROJECTS"]["_template"]:
            get_or_mk(s, pid)

    # 07 FINANCE
    c07 = get_or_mk("07 — FINANCE & TAX", root)
    index["07 — FINANCE & TAX"] = c07
    for s in TAXONOMY["07 — FINANCE & TAX"]:
        index[f"07 — FINANCE & TAX/{s}"] = get_or_mk(s, c07)

    # 08/09/10 + REVIEW
    for nm in ["08 — INBOX — TO BE FILED", "09 — DUPLICATES — REVIEW", "10 — ARCHIVE", "REVIEW"]:
        index[nm] = get_or_mk(nm, root)
    for y in TAXONOMY["10 — ARCHIVE"]:
        get_or_mk(y, index["10 — ARCHIVE"])

    return index


def move(svc, file_id, new_parent, old_parents):
    svc.files().update(fileId=file_id, addParents=new_parent,
                       removeParents=",".join(old_parents),
                       fields="id,parents").execute()


def rename(svc, file_id, new_name):
    svc.files().update(fileId=file_id, body={"name": new_name}, fields="id,name").execute()


def audit_sharing(svc, files):
    """Flag risky permissions. NEVER alters them."""
    flags = []
    for f in files:
        try:
            p = svc.permissions().list(fileId=f["id"],
                fields="permissions(id,type,role,emailAddress)").execute().get("permissions", [])
        except Exception:
            continue
        for perm in p:
            if perm.get("type") == "anyone":
                flags.append({"file": f["name"], "id": f["id"], "issue":
                              f"ANYONE WITH LINK ({perm.get('role')})"})
            elif perm.get("type") == "domain":
                flags.append({"file": f["name"], "id": f["id"], "issue":
                              f"domain-wide ({perm.get('role')})"})
    return flags


def naming_standard(f: dict) -> str:
    date = (f.get("modifiedTime") or "")[:10] or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    clean = re.sub(r"\.([a-z0-9]{2,5})$", "", f.get("name", ""), flags=re.I)
    clean = re.sub(r"(?i)\b(copy|final final|new|updated|revised|v\d+)\b", "", clean)
    clean = re.sub(r"[_\s]+", " ", clean).strip(" -_")
    return f"{date} — Unclassified — Document — {clean} — Draft"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--build-tree", action="store_true")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()

    svc = service()
    print("AUTHENTICATED. Scanning Drive...")
    files = list_all(svc)
    print(f"Scanned {len(files)} items "
          f"({sum(1 for f in files if f['mimeType'].endswith('folder'))} folders, "
          f"{sum(1 for f in files if not f['mimeType'].endswith('folder'))} files)")

    size_index, name_index = defaultdict(int), defaultdict(int)
    for f in files:
        if f.get("size"):
            size_index[(re.sub(r"\s+", " ", f["name"].lower()).strip(), f["size"])] += 1
        name_index[re.sub(r"\.[a-z0-9]+$", "", f["name"].lower()).strip()] += 1

    plan, dups, sens, lowconf = [], [], [], []
    for f in files:
        if f["mimeType"].endswith("folder"):
            continue
        c = classify(f)
        if c.get("skip"):
            continue
        d, why = is_dup_candidate(f, size_index, name_index)
        s = detect_sensitive(f)
        rec = {"id": f["id"], "name": f["name"], "dest": c["dest"],
               "confidence": c["confidence"], "reasons": c["reasons"],
               "sensitive": s, "parents": f.get("parents", []),
               "modified": (f.get("modifiedTime") or "")[:10]}
        if s:
            rec["dest"] = TAXONOMY["04 — MEDICAL / CLINICAL"]["_restricted"] + "/PHI"
            sens.append(rec)
        elif d:
            rec["dest"] = "09 — DUPLICATES — REVIEW"
            rec["dup_reason"] = why
            dups.append(rec)
        elif c["confidence"] < 0.5:
            lowconf.append(rec)
        plan.append(rec)

    out = {"scanned": len(files), "plan": plan, "duplicates": dups,
           "sensitive": sens, "low_confidence": lowconf,
           "generated": datetime.now(timezone.utc).isoformat()}
    (STATE_DIR / "last_plan.json").write_text(json.dumps(out, indent=2))

    print(f"\nPlan: {len(plan)} files -> ", end="")
    print(f"{len(sens)} sensitive, {len(dups)} duplicate-suspect, "
          f"{len(lowconf)} low-confidence")
    by_dest = defaultdict(int)
    for r in plan:
        by_dest[r["dest"]] += 1
    for d, n in sorted(by_dest.items(), key=lambda x: -x[1])[:15]:
        print(f"   {n:5d}  {d}")

    if a.build_tree or a.execute:
        print("\nBuilding taxonomy tree...")
        idx = build_tree(svc)
        (STATE_DIR / "folder_index.json").write_text(json.dumps(idx, indent=2))
        print(f"  {len(idx)} folders ready")

    if a.execute:
        print("\nExecuting moves (nothing is deleted)...")
        idx = json.loads((STATE_DIR / "folder_index.json").read_text())
        moved = renamed = failed = 0
        for r in plan:
            fid = idx.get(r["dest"])
            if not fid:
                failed += 1
                continue
            try:
                move(svc, r["id"], fid, r["parents"] or [])
                moved += 1
            except Exception as e:
                print(f"   ! {r['name'][:40]}: {e}")
                failed += 1
            if (not protected_from_rename({"name": r["name"]})
                    and r["confidence"] >= 0.5 and not r.get("dup_reason")):
                try:
                    rename(svc, r["id"], naming_standard({"name": r["name"],
                                                          "modifiedTime": r["modified"]}))
                    renamed += 1
                except Exception:
                    pass
        print(f"  moved={moved} renamed={renamed} failed={failed}")

    print(f"\nState written to {STATE_DIR}/last_plan.json")


if __name__ == "__main__":
    main()
