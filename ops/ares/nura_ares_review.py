"""Create the NURA ARES / DARPA DP2 review page in Notion."""
import json, subprocess, sys, time
sys.path.insert(0, "/opt/data/scripts")

def run(*a):
    return subprocess.run(["python3", "/opt/data/scripts/notion_client.py"] + list(a),
                          capture_output=True, text=True)
def t(x): return {"type": "text", "text": {"content": x}}
def h1(x): return {"object":"block","type":"heading_1","heading_1":{"rich_text":[t(x)]}}
def h2(x): return {"object":"block","type":"heading_2","heading_2":{"rich_text":[t(x)]}}
def h3(x): return {"object":"block","type":"heading_3","heading_3":{"rich_text":[t(x)]}}
def para(x): return {"object":"block","type":"paragraph","paragraph":{"rich_text":[t(x)]}}
def bullet(x): return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[t(x)]}}
def num(x): return {"object":"block","type":"numbered_list_item","numbered_list_item":{"rich_text":[t(x)]}}
def todo(x): return {"object":"block","type":"to_do","to_do":{"rich_text":[t(x)],"checked":False}}
def callout(x,e="📌"): return {"object":"block","type":"callout","callout":{"rich_text":[t(x)],"icon":{"type":"emoji","emoji":e}}}
def code(x): return {"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":x}}],"language":"plain text"}}
def quote(x): return {"object":"block","type":"quote","quote":{"rich_text":[t(x)]}}
def div(): return {"object":"block","type":"divider","divider":{}}

TITLE = "🚨 NURA ARES — DARPA DPA26BZ06-DV029 (ICU-in-a-Box) — CTO Review & Capture Control"

b = [
callout("Independent verification of the ARES proposal blueprint, performed 2026-09-11 by Hermes (CTO). Verdict: the document is technically sound and its CONDITIONAL GO recommendation is correct — BUT it contains one material date error and omits three mandatory federal registration gates that are now on the critical path. Read the two red sections before anything else.", "🚨"),

h2("1. THE CLOCK (corrected)"),
para("Verified against DARPA's live topic page — not inferred."),
code("""DPA26BZ06-DV029  |  DoW SBIR 2026 BAA | Release 6
Publication : Sept. 2, 2026   (past)
Opening     : Sept. 23, 2026  ->  12 days from today (2026-09-11)
CLOSES      : Oct. 23, 2026   ->  42 days from today
Proposal window : 30 days
Submission time : 12:00 pm ET on the close date"""),
callout("CORRECTION: the blueprint states the close is October 21, 2026 in at least four places. DARPA's live page states Closes: Oct. 23, 2026. The blueprint understates the window by two days. Direction is favourable (two bonus days), but every internal deadline, Gantt bar and the compliance matrix must be rebuilt on Oct. 23.", "⚠️"),

h2("2. WHAT THE BLUEPRINT GETS RIGHT (independently verified)"),
para("I checked the load-bearing claims against primary sources. The technical content is accurate:"),
bullet("DP2 entry gate matches DARPA verbatim — portable, battery-operated extracorporeal prototype; ≥2 L/min blood flow with lung support; ≥75 mL/min O2; ≥40 mL/min CO2; plus 1 of 3 autonomy algorithms."),
bullet("The three autonomy alternatives are quoted correctly (SpO2/EtCO2 via flow+sweep+FiO2; MAP via vasopressor+fluid/blood; renal potassium control via blood flow+ultrafiltration)."),
bullet("≤15 Fr (5 mm) preferred single cannula, jugular or femoral — correct, and correctly identified as a PREFERENCE not a hard threshold."),
bullet("Phase II gas targets — ~250 mL/min preferred full O2 support, ≥125 mL/min accepted partial support with the casualty assumed intubated — correct."),
bullet("≥80 mL/min CO2, perfusion pressure (not merely cuff BP) sustained ≥24 h, ≥50% estimated blood volume haemorrhage over 6 h, >72 h duration desirable — all correct."),
bullet("'System of systems' explicitly out of scope; autonomous cannulation out of scope; field-medic-level local operator assumed — all correct."),
bullet("Patent US11654225B2 confirmed: 'Wearable modular extracorporeal life support device for mobile treatment of single and multiorgan failure', assignee The Geneva Foundation, inventors incl. Andriy I. Batchinsky, dual-lumen, lung + renal (CRRT) support, STATUS ACTIVE, expires 2041-05-13. The FTO concern is real."),
bullet("Date arithmetic in the blueprint is internally correct: 11 Sep -> 23 Sep inclusive = 13 calendar days. The error is the closing date, not the counting."),

h2("3. THE THREE OMISSIONS THAT ARE NOW CRITICAL PATH"),
callout("The blueprint's 'Administrative compliance' section covers page limits, font sizes and the ≥50% work rule — but never mentions federal registration. DARPA states plainly: 'contract award cannot be made without an active SAM Registration and current NIST Assessment.' These have weeks-long lead times. This is now more urgent than the DP2 evidence sprint.", "🔴"),

h3("Omission 1 — SAM.gov registration + Unique Entity ID (UEI)"),
bullet("MANDATORY. FAR 52.204-7 and 52.204-13 are incorporated into the BAA. All proposers must be registered in SAM and hold a valid UEI to receive an award, and must maintain active status throughout the award."),
bullet("The UEI must be provided in the proposal itself."),
bullet("Lead time is typically 2-6 weeks and can stall on CAGE code assignment or entity validation."),
bullet("ACTION: confirm whether Nuratech AI already has an ACTIVE SAM registration and a UEI. If not, start it today. I could not verify this programmatically — the SAM entity API requires a key and sbir.gov returned 403."),

h3("Omission 2 — NIST SP 800-171 DoD Assessment (SPRS)"),
bullet("MANDATORY, second gate. 'Proposers should ensure that they have ... a complete NIST SP 800-171 DoD Assessment.'"),
bullet("This is a self-assessment scored and posted into SPRS (Supplier Performance Risk System, https://www.sprs.csd.disa.mil/nistsp.htm)."),
bullet("It is a cybersecurity-controls assessment — NURA's infrastructure posture is directly relevant. Given the open dashboard-auth anomaly and the unpatched kernel CVE in the fleet, expect a real gap analysis, not a formality."),

h3("Omission 3 — DSIP + SBA registry + mandatory templates"),
bullet("DSIP registration is via a login.gov account and must be completed before submission; the blueprint names DSIP only as a portal."),
bullet("SBA Company Registry registration is required."),
bullet("Use of the DARPA Cost Proposal template is MANDATORY (stated twice in the instructions)."),
bullet("Full package is Volume 1 Cover Sheet / 2 Technical / 3 Cost / 4 Company Commercialization Report / 5 Supporting Documents / 6 Fraud-Waste-Abuse Training / 7 Foreign Affiliations — Volume 7 is now a WEBFORM; PDF is no longer accepted. The blueprint treats these as documents."),
bullet("Topic-specific technical questions for prior DARPA releases had an EXPLICIT deadline (e.g. 'September 17, 2025' for 25.4 R3), not merely the generic 7-day FAQ rule. Confirm the Release 6 technical-question deadline; it is likely to fall before opening day."),

h2("4. WHERE I AGREE WITH THE BLUEPRINT'S STRATEGIC CALLS"),
num("CONDITIONAL GO with an eligibility sprint before proposal production — correct. Polishing prose cannot fix an unproven entry gate."),
num("The DP2 gate most likely requires ONE integrated prototype to have demonstrated all four items. I concur on the grammar: 'A prototype, portable (battery operated) extracorporeal system that can: 1) ... 2) ... 3) ... and 4) ...'. Singular prototype, conjunctive list. This must be put to DARPA in writing regardless."),
num("The ≤15 Fr single-access constraint is the hardest physical problem, not the AI — correct, and the oxygen-content arithmetic (2 L/min yields ~74-110 mL O2/min at Hb 8-12 g/dL) is the right first-order framing. The 125 mL/min Phase-II floor genuinely needs ~2.7-3.4 L/min at realistic Hb."),
num("A '72-hour battery in a backpack' is the wrong architecture — correct; the 150 W model shows ~50 kg of cells for 72 h, so hot-swap plus vehicle/aircraft power is the only coherent answer."),
num("AIME must be supervisory reasoning, never a direct actuator controller, with an independent safety governor holding unconditional veto — correct and consistent with NURA's existing clinician-authority doctrine. The 'move authorisation upstream' reframe (protocol + controller envelope approved pre-deployment = advance authorisation) is the right way to satisfy DARPA's autonomy requirement without abandoning governance."),
num("Nuratech should NOT prime unless the DP2 evidence question is resolved — correct. A software company cannot prime a hardware-evidence gate."),

h2("5. MY ADDITIONS — REFRAMING THE GO/NO-GO"),
callout("The blueprint frames the problem as 'find a partner who has already crossed the DP2 gate.' That framing likely produces a dead end, because it found no partner with a proven qualifying autonomous loop. The better framing: NURA is the item-4 vendor.", "💡"),

h3("5.1 The wedge is the one thing nobody has"),
para("Public-evidence screening in the blueprint found NO candidate with a documented qualifying closed-loop capability. Items 1-3 (portable battery ECLS, ≥2 L/min, gas exchange) are demonstrably possessed by several players. Item 4 — the autonomy algorithm — is exactly NURA/AIME's domain and is precisely the gap."),
para("Therefore the outreach should not ask 'do you have all four?' It should ask 'do you have 1-3, and will you give us bench access to your hardware under NDA so we can qualify item 4 together before 23 October?' That converts a screening exercise into a technical sprint with NURA as the indispensable party — and it strengthens the NURA-prime case rather than presupposing an SBC prime."),

h3("5.2 The cheapest qualifying autonomy proof is Option A, not the haemorrhage path"),
bullet("DP2-G07 Option A (maintain SpO2/EtCO2 by adjusting blood flow, sweep gas and/or FiO2) is bench-demonstrable WITHOUT blood products, vasopressors or animals."),
bullet("A real oxygenator in a recirculating loop with deoxygenated blood analogue, plus inline gas analysis, can demonstrate a closed-loop control law and its perturbation response."),
bullet("Options B (pressure control with vasopressor + fluid) and C (extracorporeal potassium control) both require blood, drugs or animal work — slower and costlier."),
bullet("The blueprint lists Option A as a 'strong ARES candidate' but never identifies it as the fastest route to the gate. It should be the primary bench target."),

h3("5.3 Administrative critical path now outranks technical work"),
para("If SAM registration is not already active and SPRS is not populated, no amount of DP2 evidence produces an award. With 42 days to close and 2-6 week registration lead times, this is the first thing to resolve today — before the partner emails."),

h2("6. EXECUTIVE ATTENTION REQUIRED (decisions only Eddie can make)"),
todo("Confirm Nuratech AI's SAM.gov registration status and UEI. If not active — start today. This may be the true critical path."),
todo("Authorise (or reject) the NURA-prime vs hardware-SBC-prime posture. I recommend: pursue NURA-prime with the item-4 wedge, hold SBC-prime as the fallback if DARPA confirms team-combined evidence is permissible."),
todo("Decide whether to fund the rapid self-funded bench proof (the Option A closed-loop rig). This is the only lever that converts NURA from 'software subcontractor' to 'prime with a qualifying autonomy demonstration'."),
todo("Confirm the DV029 topic-specific cost ceiling. The blueprint's own model is $3.3M-$5.7M against DARPA's $1.8M 'typical' Phase II figure — that gap is a capture-killer and must be resolved with DARPA or the scope deliberately narrowed."),
todo("Authorise patent counsel to open the Geneva MELS FTO/claim chart. Patent is ACTIVE to 2041 and overlaps the proposed ARES fluidic architecture."),
todo("Approve sending the technical questions to SBIR_BAA@darpa.mil (I have them drafted — see below). DARPA guidance forbids asking them to design the solution; these are interpretation questions only."),

h2("7. QUESTIONS TO SEND DARPA (drafted, awaiting approval)"),
para("Send to SBIR_BAA@darpa.mil. Narrow interpretation questions only — no requests for engineering advice."),
num("Must DP2 items 1-4 be demonstrated on the SAME integrated portable prototype, or may a newly formed team combine documented Phase-I-equivalent subsystem evidence from different members?"),
num("Must the qualifying autonomous algorithm have directly controlled the proposed extracorporeal prototype before submission, or may it be demonstrated at bench during Phase II?"),
num("Is ≤15 Fr evaluated as a strict threshold or as a preference permitting a quantitatively justified larger cannula?"),
num("What is the topic-specific maximum base and option cost for DV029?"),
num("What is the exact technical-question submission deadline for Release 6, and the exact DSIP close date and time?"),
num("Which Release 6 DP2 technical-volume template controls if its structure differs from the general Phase II instructions?"),
num("May DP2 feasibility supporting reports and raw data reside in Volume 5 beyond the 20-page Technical Volume?"),

h2("8. STATUS BOARD"),
bullet("Blueprint technical content: VERIFIED ACCURATE"),
bullet("Blueprint closing date: CORRECTED to Oct. 23, 2026"),
bullet("Administrative gate coverage: INCOMPLETE — SAM/UEI, SPRS, DSIP, SBA registry missing"),
bullet("Partner strategy: REFRAMED — NURA supplies the missing item 4"),
bullet("Draft assets ready: DARPA questions (7), partner outreach email, DP2 evidence request list, partner scorecard"),
bullet("Blocking on: Eddie's SAM status, prime posture, bench-proof funding decision"),

div(),
para("Recorded 2026-09-11 by Hermes (CTO). Source document: NURA_ARES_Powered_by_AIME — DARPA DPA26BZ06-DV029 Proposal and Implementation Blueprint (1,264 lines). Primary verification: darpa.mil/research/programs/icu-in-a-box, patents.google.com/patent/US11654225B2, DARPA SBIR/STTR Phase II instructions, DARPA Proposer General Terms (SAM/UEI requirement)."),
]

PARENT = "613e14da-104a-470e-af85-799d66eb8ebc"  # NURATECH AI - Executive Command Center
r = run("create-page", PARENT, TITLE, "--blocks", json.dumps(b[:90]))
try:
    resp = json.loads(r.stdout)
    pid = resp.get("id") or resp.get("page_id") or (resp.get("results") or [{}])[0].get("id")
    print("PAGE:", pid)
except Exception:
    print("RAW:", r.stdout[:400], r.stderr[:200]); sys.exit(1)

for i in range(90, len(b), 90):
    out = run("append", pid, json.dumps(b[i:i+90]))
    print(f"  chunk appended: {out.stdout[:80]}")

time.sleep(1)
rb = run("children", pid)
try:
    print("total blocks:", len(json.loads(rb.stdout).get("results", [])))
except Exception:
    print("children:", rb.stdout[:200])
print("URL: https://www.notion.so/" + str(pid).replace("-", ""))
