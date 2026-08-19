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
    "title": "CEO DIRECTIVE (founder): NEW DIVISION — NURA Avionics Connect (aviation equipment integration product)",
    "description": ("FOUNDER 2026-08-02: 'Look at current Aviation equipment and see if there's anything we could "
                    "integrate with via API or RS-232 or other connection. Another division and product. Give it to "
                    "ATLAS.' Founder is a private pilot + IR flying PA-32R-300, PA-46 Malibu, stepping to turboprop "
                    "Piper and Vision Jet.\n\n"
                    "=== PRODUCT: NURA AVIONICS CONNECT ===\n"
                    "Panel data → Hermes: engine monitor telemetry · live fuel burn/W&B · briefing automation · "
                    "logbook automation · international packet prep (eAPIS/FPL).\n\n"
                    "=== INTEGRATION MAP (skills banked: aviation-pilot-ops + foreflight-integration) ===\n"
                    "1) Garmin: GTN 750/650 (WiFi flight-stream) · G1000/NXi (RS-232, ARINC 429) · G3X/G5 · GDL 50/39 "
                    "(WiFi ADS-B) · Garmin Pilot\n"
                    "2) Avidyne IFD · Aspen EFA · Stratus (ADS-B/AHRS) · Lynx NGT (ADS-B In)\n"
                    "3) FlightStream 510 class: ARINC 429 + RS-232 + WiFi bridges (Garmin autopilot + iPad) — the "
                    "realistic gateway for certified panels\n"
                    "4) RS-232: Garmin aviation serial protocol (position/COM/nav/engine sentences)\n"
                    "5) SAFETY RULE: READ-ONLY on certified avionics (FAA doctrine); control-path integration only in "
                    "EAB/experimental aircraft\n\n"
                    "=== ATLAS EXECUTE ===\n"
                    "1) Hire Avionics Integrations Lead (hermes_gateway) — owns the division\n"
                    "2) Equipment scan: founder's actual panels (PA-32R-300 + PA-46 avionics lists) → integration "
                    "path per device (API/RS-232/WiFi/ARINC) — evidence-first\n"
                    "3) PoC: engine-monitor telemetry ingest (read-only) + W&B/briefing automation\n"
                    "4) Logbook automation lane + ForeFlight packet prep integration\n"
                    "5) FAR/AIM knowledge base (vault Aviation/) = the compliance reference\n"
                    "Evidence: equipment scan + integration map by 2026-08-10; PoC by 2026-08-31. No avionics "
                    "purchases without founder sign-off."),
    "assigneeAgentId": aid, "priority": "high", "status": "todo",
}
try:
    req = urllib.request.Request(base + f"/api/companies/{cid}/issues", data=json.dumps(issue).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print("Avionics division directive ->", r.status, d.get("id", d.get("issueId", "?")))
except urllib.error.HTTPError as e:
    print("ERR", e.code, e.read().decode()[:300])
