import requests, json, time

tok = list(json.load(open("/opt/data/profiles/nura/home/.config/notion/auth.json")).values())[0]
H = {"Authorization": f"Bearer {tok}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
API = "https://api.notion.com/v1"
PID = "3d5a9b14-e498-8104-a64b-cd704d6b7f30"

def t(x): return {"type": "text", "text": {"content": x}}
def h2(x): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [t(x)]}}
def h3(x): return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [t(x)]}}
def bullet(x): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [t(x)]}}
def para(x): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [t(x)]}}
def callout(x): return {"object": "block", "type": "callout", "callout": {"rich_text": [t(x)]}}
def codeblock(x): return {"object": "block", "type": "code", "code": {"rich_text": [t(x)], "language": "python"}}

def append(blocks):
    r = requests.patch(f"{API}/blocks/{PID}/children", headers=H, json={"children": blocks}, timeout=30)
    return r.status_code, len(r.json().get("results", []))

blocks = [
    h2("1. Overview"),
    callout("CarePilot = the NURA Medicare Advantage / population-health + Transition-of-Care (TCM) platform. Three layers: (1) FastAPI domain engine, (2) Flutter provider frontend, (3) Playwright RPA data-ingestion layer that scrapes the live carepilot.nuratech.ai dashboard + Solis. Indexed 2026-09-08 with authoritative line counts (collected live, not estimated)."),
    para("CODEBASE: ~2,359 lines total across backend (1,029) + frontend (369) + RPA bots (535) + Solis data-plane (426). Plus the NURA repo mirror (1,020). AI = proposal-only throughout; no clinical write by AI."),
    h2("2. Backend — FastAPI domain engine (canonical /opt/data/carepilot/backend/, 1,029 lines)"),
    bullet("app.py (8) — uvicorn launcher on :8000"),
    bullet("main.py (279) — FastAPI app: ~60 routes (read + action + propose-only + n8n lab contract + TCM lifecycle). RBAC via X-Role header; propose-only gate on clinical/coding/billing."),
    bullet("models.py (153) — 25 Pydantic entities (Patient, CareGap, RiskScore, WorkTask, Claim, MedicationAlert, Hospitalization, Intervention, CasePlan, + 10 TCM: Cohort, TCMCase, TCMStep, CareTeam, TCMEvent, PostAcutePlacement, ReadmissionRisk, SDOHScreen, SLABreach, TCMBilling)."),
    bullet("store.py (143) — in-memory Store + seed (4 patients, cohorts, TCM cases, event feed, 3 integrations)."),
    bullet("engines.py (277) — 39 capabilities + TCM lifecycle (event intake, risk-stratify, readmission-risk, BH/SDOH, placement, SLA, billing, cost-avoidance, quality, executive board)."),
    bullet("hl7.py (86) — HL7 v2.x ADT parser (MSH-9 / PID-3 / PV1-3) -> TCM trigger. ADT^A01=admit, A03=discharge."),
    bullet("test_safety.py (82) — 41 assertions (safety guards, RBAC 403, propose-only, n8n contract, TCM, HL7)."),
    h3("Key safety boundary (main.py SAFETY_GUARDS)"),
    bullet("no_ai_sign · no_ai_order · no_ai_diagnosis · no_ai_med_change · no_ai_claim · no_ai_message · clinical_over_financial · med_safety_human_only"),
    h3("TCM lifecycle (the care-management engine)"),
    bullet("Event intake (Mirth ADT / eMedical / Ensure) -> open case + alert care team + seed admission checklist"),
    bullet("Cohort assignment + readmission-risk band (Low/Med/High/Very-High)"),
    bullet("Care team: case manager + community-paramedic NP (Medisun MIH) + hospital discharge nurse"),
    bullet("Post-acute placement / home-health · SLA/escalation · TCM billing (CPT 99495/99496 propose-only) · cost-avoidance · quality metrics · executive board"),
    h2("3. Frontend — Flutter provider app (canonical /opt/data/carepilot/frontend/lib, 369 lines)"),
    bullet("main.dart (66) — bottom-nav shell, 7 provider surfaces"),
    bullet("api.dart (24) — HTTP client, X-Role header drives server RBAC"),
    bullet("screens/home.dart (52) — CPHO Command Center"),
    bullet("screens/work_queue.dart (35) — Unified Work Queue"),
    bullet("screens/patient.dart (49) — Patient search + summary"),
    bullet("screens/risk.dart (30) — Risk / RAF (V28)"),
    bullet("screens/med_safety.dart (32) — Medication Safety (AI cannot close findings)"),
    bullet("screens/quality.dart (48) — HEDIS / Stars measure"),
    bullet("screens/finance.dart (33) — Medical Economics / contract performance"),
    h2("4. RPA data-ingestion layer (Playwright, /opt/data/scripts, 535 lines)"),
    bullet("carepilot-reader.py (61) — PRODUCTION reader: login -> structured JSON (active members, RAF gaps, avg RAF, cohort gaps) -> carepilot-live-metrics.json; read + propose-only."),
    bullet("carepilot_patients.py (70) — full patient scrape with pagination -> carepilot_patients_full.json"),
    bullet("carepilot_membership.py (45) — click '98 scored patients / View all' -> roster"),
    bullet("carepilot_nav.py (38) + carepilot_links.py (31) — login -> dump nav links / roster filter"),
    bullet("carepilot-probe.py (52) — non-browser path: urllib + CSRF token + POST login"),
    bullet("carepilot-navmap.py (46) + carepilot-deepnav.py (46) + carepilot-rpa-review.py (61) + carepilot-rpa-retry.py (68) — exploratory nav-walks hunting for a CarePilot-native RPA/bots section"),
    bullet("nura_carepilot_dashboard.py (94) — MA/HCC command-center: load Solis MRA CSV -> sqlite -> per-member MRA, RAF gap, coding lane (V28 ICD candidates)"),
    bullet("carepilot-inspect.sh (17) — inventory checker"),
    h2("5. Companion Solis data-plane (/opt/data/scripts, 426 lines)"),
    bullet("solis-login.py (49) · solis-pull-reports.py (103) · solis-deep.py (64) · solis-explorer.py (63) · solis-reader.py (37) · solis-kpi-probe.py (26) · solis-sections.py (37) · solis-sections-deep.py (47) — login to solis.ensuredatasolutions.com and pull the MRA/HCC report files that feed the dashboard."),
    h2("6. Repo mirror (eddieg73/NURA carepilot-platform/backend, 1,020 lines)"),
    bullet("engines.py · hl7.py · main.py · models.py · store.py · test_safety.py — the same backend synced to git (hl7.py added; app.py/__init__.py excluded from the reflection)."),
    h2("7. CTO findings (the honest review)"),
    bullet("GAP — two disconnected systems: FastAPI engine (clean, 41/41 tests, synthetic in-memory data) is NOT wired to the RPA reader (which scrapes real carepilot.nuratech.ai). No bridge. The TCM engine consumes fictional patients, not real members."),
    bullet("RBAC no-op — main.py require_any() read-side guard does nothing (dead logic). Only write routes enforce is_human_write()."),
    bullet("Redundancy — 6 RPA scripts do the same login+nav-dump (nav, links, navmap, deepnav, rpa-review, rpa-retry) from one exploratory session; carepilot-reader.py is the only production-grade one."),
    bullet("No CarePilot-native RPA/bots feature found — the exploratory bots hunted /rpa /automation /bots and found nothing; NURA's 'RPA bots' ARE these Playwright scrapers."),
    bullet("Fragile scraping — fixed time.sleep(), CSS selectors (input[name=username]), regex over text. Breaks on any UI change."),
    bullet("PHI on disk — carepilot_patients.py paginates a PHI roster to /tmp JSON; should be 0600-scoped, not open /tmp."),
    bullet("Stale counts — health reports capabilities:39 (now ~50+); store.py source='emeditical' typo; hl7.py A04 in both admit+ER sets."),
    bullet("Frontend placeholder — home.dart _gapCount() returns hardcoded 0; 'Med safety flags' hardcoded 'open'."),
    bullet("CORS allow_origins=['*'] — fine for localhost P0, must be locked before any PHI deployment."),
    h2("8. Recommended next steps"),
    bullet("BUILD THE BRIDGE — reader -> engine (shared DB / store load), so TCM board shows real members instead of synthetic. Highest ROI."),
    bullet("Consolidate the 6 redundant nav-dump bots into one maintained module (or archive)."),
    bullet("Fix RBAC require_any() + correct stale counts + emeditical typo + harden reader (stable attrs, backoff)."),
    bullet("Scope PHI on disk to a 0600 dir; make CORS config-driven before deploy."),
    para("Sources: read-in-full on 2026-09-08. Backend 1,029 lines + frontend 369 + RPA 535 + Solis 426 + repo mirror 1,020. Line counts collected live from disk."),
]
code = 'API endpoints: /health, /api/safety/boundary, /api/patients/search, /api/patients/{pid}/summary, /api/care-gaps, /api/measure/{measure}, /api/risk-scores, /api/work-queue, /api/medication-alerts, /api/referrals, /api/provider-scorecard, /api/financial-summary, /api/pharmacy, /api/utilization, /api/claims-audit, /api/risk-revenue, /api/audit, /api/ccm/candidates, /api/interventions, /api/tasks (post), /api/propose/enrollment, /api/propose/charge, /api/propose/outreach, /api/labs/*, /api/tcm/* (cohorts, cases, checklist, steps, care-team, home-health, integrations, events, ingest, hl7, stratify, readmission-risk, bh-sdoh, placement, sla, billing, cost-avoidance, quality, board)'
blocks.append(codeblock(code))

for i in range(0, len(blocks), 50):
    st, n = append(blocks[i:i+50])
    print(f"append {i}-{i+50}: HTTP {st} blocks {n}")
    time.sleep(0.3)
