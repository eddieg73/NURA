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
    "title": "NUR-95: HEDIS MY 2026 — track quality measures for Solis MA (CarePilot + OpenEMR wiring)",
    "description": ("Founder 2026-08-02: HEDIS skills built (hedis-quality-measures — MY 2026 NCQA-verified: FHIR "
                    "spec format, ECDS-only statins/lead/tobacco, SNS-E LOINC-only, hybrid phase-out by 2029). "
                    "Apply to the Solis full-risk MA panel (285 pts) for STARs.\n"
                    "FLORENCE EXECUTE:\n"
                    "1) MAP CarePilot gaps to HEDIS numerators: HbA1c control, BP control (BPD-E), statin "
                    "(SPC-E/SPD-E), breast/colorectal screening, AIS-E (incl. new 65+ RSV indicator), "
                    "depression (CDF/PHQ-9 LOINC), SNS-E (social needs — LOINC-only per MY26), 7-day "
                    "post-discharge follow-up.\n"
                    "2) DATA: ensure OpenEMR captures the LOINC valuesets (BP, A1c, PHQ-9, SDOH screens) + "
                    "medication lists — ECDS readiness is our FHIR adapter path (ties NUR-91/66).\n"
                    "3) CADENCE: monthly CarePilot gap sweep -> numerator tracking; quarterly STARs-preview "
                    "digest to founder (which measures move the rating, gaps by patient).\n"
                    "4) COMPLIANCE: value sets ONLY from NCQA VSD/Medication List Directory (free order) — "
                    "no invented codes; document adjustments per Rules for Allowable Adjustment.\n"
                    "5) Evidence: first monthly numerator report on this issue. Skill reference: "
                    "hedis-quality-measures."),
    "assigneeAgentId": FLORENCE, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{CID}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("NUR-95 ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:200])
