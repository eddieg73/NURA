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
    "title": "CEO DIRECTIVE (founder): WEB TEAM + NURATECH.AI REBUILD — Anduril-inspired, division pages",
    "description": ("FOUNDER 2026-08-02: hire web developers; look at Anduril's site for inspiration; add divisions "
                    "and pages to the Nuratech site. Current site = single-page template built by Meta AI (bought "
                    "from China) — REBUILD (verified: nuratech.ai = HTTP 200, ONE css bundle, zero internal links).\n\n"
                    "=== INSPIRATION (Anduril.com, extracted 2026-08-02) ===\n"
                    "Dark cinematic design · product-card grid with one-line mission tags ('First to See, First to "
                    "Act' · 'Autonomy for Every Mission') · manufacturing/proof story section · news/insights "
                    "section. Adapt to healthcare-tech (not defense): same gravity, clinical credibility.\n\n"
                    "=== SITE STRUCTURE (divisions + pages) ===\n"
                    "Pages: Home · Product (the app — EA/MEDICAL dual-mode) · Technology (Hermes/Lattice mesh · "
                    "hummingbird/GLM-5.2 · telemetry CDS) · Divisions · Careers · Contact\n"
                    "Division pages (each with mission tag + story):\n"
                    "1) NuraTech Core — The Healthcare AI OS (SaaS, standards: FHIR R4/SMART/HL7 v2/DICOM)\n"
                    "2) NURA Assurance — one books for the ecosystem\n"
                    "3) NURA Aero — EMS drones + swarm (911 civilian + military)\n"
                    "4) NURA EMS — Mobile Integrated Health (NP/PA + fly car, partnership model)\n"
                    "5) NURA Avionics Connect — panel data intelligence (pilot lane)\n"
                    "6) NURA Capital Markets (parked — light page)\n"
                    "7) NURA Glasses/Capsule (product pages — wearable AI lane)\n\n"
                    "=== ATLAS EXECUTE ===\n"
                    "1) Hire Web Developer (frontend) + Web Designer (design system) — hermes_gateway wired\n"
                    "2) Design system: Anduril-inspired (dark, cinematic, clinical-credible); founder approves "
                    "direction before build\n"
                    "3) Rebuild: multi-page site, division pages per above, product + technology pages\n"
                    "4) Compliance: healthtech marketing claims gate (healthtech-marketing-claims-review) — no "
                    "unverifiable claims on clinical pages\n"
                    "5) Deploy: current host or move to NURA infra (decision with founder)\n"
                    "Evidence: design direction mock (1 page) by 2026-08-06 · full site by 2026-08-31. No domain/"
                    "hosting purchases without founder sign-off."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Web rebuild directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
