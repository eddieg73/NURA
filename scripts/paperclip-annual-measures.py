import json, urllib.request, urllib.error

def env_file(path, names):
    try:
        for line in open(path):
            for n in names:
                if line.startswith(n + "="):
                    return line.strip().split("=", 1)[1].strip("'\"")
    except OSError:
        pass
    return None

key = env_file("/opt/data/paperclip-runtime/mcp.env", ["PAPERCLIP_API_KEY", "API_KEY"])
base = "http://127.0.0.1:3101"
hdr = {"User-Agent": "NURA-Hermes/1.0", "Content-Type": "application/json",
       "x-api-key": key or "", "Authorization": "Bearer " + (key or "")}
CID = "999ff375-6128-41cf-b6c8-06b98673a29b"
FLORENCE = "e073d73b-e5a4-4a5e-8c1f-6f1e4a1c2d3e"

issue = {
    "title": "NUR-96: Annual patient measures engine — age/vaccines/travel vs hot zones (OpenEMR + CarePilot)",
    "description": ("Founder 2026-08-02: annual measures per patient by age, vaccines, travel history, "
                    "compared with hot zones on maps.\n"
                    "BUILT (Hermes): skill annual-patient-measures (age-bucketed measure checklists anchored "
                    "to USPSTF + lifespan-vaccination-schedule + hedis-quality-measures) + scripts/"
                    "travel-risk-engine.py (parses CDC Travel Health Notices — VERIFIED LIVE 2026-08-02: "
                    "Level 3 Ebola DRC; Level 2 Chikungunya Bolivia/Costa Rica/French Guiana/Mauritius/"
                    "Seychelles/Suriname + Ebola DRC/Uganda; writes data/travel-hotzones.json).\n"
                    "FLORENCE EXECUTE (OpenEMR concierge):\n"
                    "1) OpenEMR: preventive-care alerts per age bucket (measures + immunizations due); add "
                    "travel history field (destinations + dates) to the patient record.\n"
                    "2) CARE GAPS: CarePilot gap list + annual-measure list merged into ONE preventive "
                    "checklist per patient (urgency-ordered).\n"
                    "3) HOT-ZONE COMPARISON: weekly travel-risk-engine run -> flag any patient with trips "
                    "overlapping active notices -> provider review -> travel-medicine counseling (vaccines/"
                    "prophylaxis per CDC destination page).\n"
                    "4) VERIFICATION POLICY: USPSTF/CDC-sourced only; flags cite notice level + date; "
                    "clinician decides (no auto-actions).\n"
                    "5) Evidence: first weekly hot-zone digest + sample patient checklist on this issue."),
    "assigneeAgentId": FLORENCE, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-96 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
