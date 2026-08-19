import json, re, urllib.request, urllib.error

def envval(name):
    env = open("/opt/data/profiles/nura/.env").read()
    m = re.search(rf"^{name}=(.+)$", env, re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""

key = envval("API_SERVER_KEY")
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key, "Authorization": "Bearer " + key}
cid = "999ff375-6128-41cf-b6c8-06b98673a29b"

req = urllib.request.Request(base + f"/api/companies/{cid}/agents", headers=hdr)
d = json.loads(urllib.request.urlopen(req, timeout=10).read())
agents = d if isinstance(d, list) else d.get("agents", [])
atlas = next((a for a in agents if (a.get("name") or "").lower() == "atlas"), None)
aid = atlas["id"] if atlas else None
if not aid:
    print("ATLAS NOT FOUND"); raise SystemExit(1)

issue = {
    "title": "CEO DIRECTIVE (founder): HIRE FORENSIC PATHOLOGIST (MD) for Medical Legal Review Division — Attorney Alex Stavrou cases",
    "description": ("FOUNDER 2026-08-02: create/hire a MEDICAL FORENSIC PATHOLOGIST to review Attorney Alex "
                    "Stavrou's cases; wire up what the division needs.\n"
                    "HIRE (Atlas): FORENSIC PATHOLOGIST CONSULTANT — licensed MD, board-certified (AP/CP + "
                    "forensic pathology preferred), FL-licensed or licensable, capital-case experience "
                    "preferred. Scope: autopsy report review, cause/mechanism/manner opinions, wound "
                    "analysis, expert reports + testimony support for Stavrou cases (capital murder + "
                    "medical-forensic matters).\n"
                    "TERMS: per-case retainer · NDA + attorney-client/work-product privilege · evidence-gate "
                    "(30-day) · founder signs (AI never signs) · quiet engagement (no public mention).\n"
                    "TOOLING (wired by Hermes same-day): sealed case workspace /opt/data/legal-cases/ (0700, "
                    "OUTSIDE RAG/vault), case intake script (OCR hook + manifest), legal research lanes "
                    "(CourtListener/FL dockets/eCFR/FL Admin), clinical lanes (DailyMed/openFDA/PubMed), "
                    "report template (medical-legal, evidence-cited), audit trail.\n"
                    "GATES: shortlist 2026-08-08 · engaged 2026-08-14 · first case review complete by "
                    "2026-08-28.\n"
                    "DIVISION CHARTER: vault Legal/Medical-Legal-Review-Division.md · skill "
                    "forensic-medical-review."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Forensic pathologist directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
