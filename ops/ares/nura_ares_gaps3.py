"""Round-3 gap analysis: link the program page to the review, append gaps to the review page."""
import json, subprocess, sys, time, requests
sys.path.insert(0, "/opt/data/scripts")
from notion_client import headers

PROGRAM = "3d8a9b14-e498-81cc-bc8d-c70b6db8d464"
REVIEW  = "3d8a9b14-e498-81ff-ab87-edc497410ac2"
REVIEW_URL = "https://www.notion.so/" + REVIEW.replace("-", "")

def run(*a):
    return subprocess.run(["python3", "/opt/data/scripts/notion_client.py"] + list(a),
                          capture_output=True, text=True)
def t(x): return {"type":"text","text":{"content":x}}
def h2(x): return {"object":"block","type":"heading_2","heading_2":{"rich_text":[t(x)]}}
def h3(x): return {"object":"block","type":"heading_3","heading_3":{"rich_text":[t(x)]}}
def para(x): return {"object":"block","type":"paragraph","paragraph":{"rich_text":[t(x)]}}
def bullet(x): return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[t(x)]}}
def num(x): return {"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":[t(x)]}}
def todo(x): return {"object":"block","type":"to_do","to_do":{"rich_text":[t(x)],"checked":False}}
def callout(x,e="📌"): return {"object":"block","type":"callout","callout":{"rich_text":[t(x)],"icon":{"type":"emoji","emoji":e}}}
def code(x): return {"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":x}}],"language":"plain text"}}
def div(): return {"object":"block","type":"divider","divider":{}}

# ---- 1. link the program page to this review (Reference field was empty) ----
resp = requests.patch(f"https://api.notion.com/v1/pages/{PROGRAM}", headers=headers(),
                      json={"properties": {"Reference": {"url": REVIEW_URL}}}, timeout=25)
print("Reference link set:", resp.status_code, resp.json().get("properties", {}).get("Reference"))

# ---- 2. append round-3 gaps to the review page ----
b = [
div(),
h2("13. ROUND-3 GAP ANALYSIS — what the PROGRAM PAGE still misses"),
para("The program page (NURA ARES — DARPA ICU-in-a-Box Program, Executive Projects DB) is a strong synthesis — it correctly absorbed the corrected 23 Oct date, the consumables-first reality, the triage/allocation boundary, the wrong-but-legal AI failure mode, the perfusion-estimator ground-truth rule, blood logistics, withdrawal boundaries, survivability, the federal gate list and the accountability workstream. It is now linked back to this page via its Reference field."),
para("Twelve gaps remain. The first two are eligibility-level, not documentation-level."),

h3("13.1 WHICH LEGAL ENTITY PROPOSES? — an SBIR eligibility landmine nobody has asked"),
code("""Nuratech AI LLC      (Wyoming)  <- "primary legal entity ... operations and IP"
Nuratech AI 2 LLC    (Montana)  <- "holding or special-purpose entity\""""),
bullet("SBIR permits ONE qualifying small business as proposer. The other becomes an AFFILIATE."),
bullet("Affiliation rules AGGREGATE employees and revenue across commonly controlled entities for the size test. If both LLCs are under the same control, they are measured together."),
bullet("The durable IP the whole strategy rests on sits in the WYOMING entity. If the MONTANA entity is the proposer, background-IP ownership and the proposed work sit in different legal persons — a data-rights and teaming problem, not a paperwork problem."),
bullet("The proposal must name the entity and provide its UEI. You cannot start SAM registration without first deciding which entity it is."),
callout("This has to be decided BEFORE the SAM/UEI work, because SAM registration is per-legal-entity. Register the wrong entity and the registration is wasted.", "🔴"),

h3("13.2 NO PRINCIPAL INVESTIGATOR AND NO STAFFING MODEL"),
bullet("SBIR requires a named PI. The program page has 16 decisions and not one is 'who does the work'."),
bullet("The internal blueprint sized the program at 10–14 effective technical FTE."),
bullet("Current NURA roster: Jade (EA / content ops), Amrit (Flutter), Oussama (CRM/Perfex), Nancy (billing), Natalie (CarePilot PM). There is NO critical-care engineer, NO extracorporeal/fluidic engineer, NO embedded safety engineer, NO regulatory/quality lead, NO animal-study PI."),
bullet("The ≥50% work-share rule means this cannot simply be subcontracted away — the majority of research and analytical effort must be performed by the proposing small business."),
callout("This may be a HARDER gate than the DP2 evidence. An unstaffed program cannot spend an award, and reviewers score key personnel. Either hire, or restructure so NURA's genuinely-performed share (autonomy, state estimation, safety kernel, HIL, cybersecurity, systems integration) is defensibly the majority.", "🟠"),

h3("13.3 NO COST MODEL AT ALL"),
bullet("The program page asks 'what is the topic-specific maximum cost' but contains no internal budget, no cost volume, no work-package breakdown."),
bullet("The internal blueprint modelled $3.30M–$5.70M for 24 months plus $0.9M–$1.6M for the integrated animal option, against DARPA's $1.8M 'typical' Phase II figure."),
bullet("That $3.3M-vs-$1.8M gap is a capture-killer and it has been dropped from the program record entirely."),
todo("Reinstate a work-package cost model and reconcile it against the verified topic ceiling before any scope is promised."),

h3("13.4 NO RISK REGISTER"),
bullet("No register of technical/programmatic risks with probability x consequence x retirement date x owner."),
bullet("The internal blueprint's own master prompt designated this as required deliverable item P."),
bullet("Highest-ranked risks to register now: DP2 integrated-prototype interpretation (existential), partner bench access timing, oxygen architecture, ≥50% work share, staffing, cost ceiling, FTO/MELS."),

h3("13.5 NO PROPOSAL-SHAPE MAPPING AND NO SCOPE-CUT LIST"),
bullet("The program page is a program plan. The submitted artefact is a 20-page Technical Volume following DARPA's prescribed sequence: significance of the problem; Phase-II objectives and detailed SOW; human/animal use; option SOW; related work; relationship to future R&D / Phase III; key personnel; foreign citizens; facilities and equipment; technical data rights; subcontractors and consultants."),
bullet("Nothing maps the program plan onto that structure, and there is no explicit 'what we will NOT do' list."),
bullet("Under a hard 20-page limit, unrequested scope actively dilutes scoring. The scope-cut list is a scoring instrument, not a courtesy."),

h3("13.6 THE THREE MISSIONS ARE A SCOPE RISK"),
bullet("Modes A (backpack), B (litter-mounted), C (vehicle/aircraft docked) risk reading as three products."),
bullet("DP2 requires ONE portable, battery-operated prototype demonstrating the entry thresholds."),
bullet("State explicitly: Mode B is the DP2 submission artefact; Modes A and C are Phase-II derivative configurations derived from it — not parallel developments."),

h3("13.7 SPRS IS NOT A FORM — NURA'S OWN INFRASTRUCTURE IS THE EVIDENCE"),
bullet("NIST SP 800-171 is a 110-control assessment of the ORGANISATION'S systems, scored and posted in SPRS. DARPA states award cannot be made without a current assessment."),
bullet("The program page lists 'complete/refresh SPRS assessment' as an administrative task, unconnected to reality."),
bullet("Concrete open items that will surface in that assessment: the dashboard admin exposure with foreign-IP logins and a static credential, and the unpatched kernel CVE-2026-31431 (privilege escalation + container escape) across the fleet."),
todo("Run a real 800-171 gap analysis against the live fleet BEFORE claiming SPRS readiness. Treat it as an engineering workstream with a POA&M, not a form."),

h3("13.8 MISSING FEDERAL GATE — ACCOUNTING SYSTEM APPROVAL"),
bullet("DARPA's instructions require a DCMA Final Determination Letter for accounting-system approval if a FAR-based cost-plus-reimbursement contract type is requested."),
bullet("This is a second long-lead gate alongside SAM, and it is absent from the program page's federal critical path."),
bullet("If NURA's accounting system has never been audited for government cost accounting, either start that process or deliberately propose a contract type that avoids it."),

h3("13.9 NO PARTNER SHORTLIST, OWNERS OR DATES"),
bullet("The internal blueprint screened and ranked candidates: Geneva Foundation / AREVA MELS (A+), CMU / UPMC PAS (A+), Hemovent (A/B), Abiomed-J&J OXY-1 (B), Getinge CARDIOHELP (B), Inspira ART100 (B/C), LivaNova LifeSPARC (C)."),
bullet("The program page collapses all of this to 'identify a hardware partner that already demonstrates the physical ECLS thresholds'."),
bullet("With 42 days to close, an unnamed list produces no movement. Each target needs an owner, an NDA status and a date."),

h3("13.10 SIXTEEN DECISIONS, ZERO DEADLINES"),
bullet("Only the project itself carries a date (23 Oct). Not one of the 16 executive decisions has an owner-and-date pair."),
bullet("Decisions that gate other decisions must be sequenced explicitly: entity selection -> SAM/UEI registration (weeks) -> prime posture -> partner outreach -> bench proof -> proposal production."),
todo("Assign an owner and a due date to every one of the 16 decisions, and mark which ones are on the critical path."),

h3("13.11 NO CONTINGENCY FOR THE EXISTENTIAL BRANCH"),
bullet("The single highest-risk open question is whether DARPA requires ONE integrated prototype to have demonstrated all four DP2 items."),
bullet("The answer is unlikely to arrive before opening day (23 Sep), leaving under 30 days to close (23 Oct)."),
bullet("So the NO-GO / pivot plan must be PRE-BUILT, not improvised: (a) hardware-SBC prime with NURA as exclusive autonomy subcontractor, (b) team-combined-evidence submission if DARPA permits it, (c) deliberate stand-down and re-entry on the next cycle with a 6-month partner-integration runway."),

h3("13.12 DUPLICATION — TWO ARES PAGES NOW EXIST"),
bullet("This page (CTO Review, analysis) and the program page (programme control) cover overlapping ground."),
bullet("Recommended roles: the Program page is CANONICAL for status, decisions, owners and dates; this page is the ANALYSIS APPENDIX it cites."),
bullet("The Reference field on the program entry now points here. Neither page should restate the other's content going forward."),

h3("13.13 PORTFOLIO OBSERVATION"),
bullet("In the Executive Projects database, ARES is the ONLY one of 18 projects with a hard target date. The other 17 have none."),
bullet("ARES is also 1 of only 2 projects rated Red. Two P0 projects carry no date at all while the portfolio is flagged Red."),
bullet("This is a portfolio-level finding, not an ARES finding — raised because it is visible from here."),

h2("14. CONSOLIDATED ROUND-3 DECISIONS"),
todo("Select the proposing legal entity (Wyoming vs Montana) and confirm affiliation/size implications BEFORE SAM registration."),
todo("Name the Principal Investigator and freeze the staffing model; prove the >=50% NURA work share is substantive, not accounting."),
todo("Reinstate the work-package cost model and reconcile to the verified topic ceiling."),
todo("Stand up a risk register with owner + retirement date per risk."),
todo("Map the program plan onto the 20-page Technical Volume sequence and write the 'will NOT do' scope-cut list."),
todo("Declare Mode B as the DP2 artefact and A/C as Phase-II derivatives."),
todo("Run a real NIST SP 800-171 gap analysis against the live fleet; produce a POA&M."),
todo("Resolve the contract type to determine whether DCMA accounting-system approval is required."),
todo("Convert the partner screen into a named shortlist with owners, NDA status and dates."),
todo("Assign owner + due date to all 16 executive decisions and mark the critical path."),
todo("Pre-build the three-branch contingency for the DP2 interpretation outcome."),

div(),
para("Round-3 analysis by Hermes (CTO), 2026-09-11. Program page: NURA ARES — DARPA ICU-in-a-Box Program (Executive Projects DB)."),
]

for i in range(0, len(b), 90):
    out = run("append", REVIEW, json.dumps(b[i:i+90]))
    try: n = len(json.loads(out.stdout).get("results", []))
    except Exception: n = "ERR " + out.stdout[:160]
    print(f"chunk {i//90+1}: {n} blocks")

time.sleep(1)
try:
    rb = run("children", REVIEW)
    print("review page total blocks:", len(json.loads(rb.stdout).get("results", [])))
except Exception as e:
    print("children:", e)
print("review url:", REVIEW_URL)
