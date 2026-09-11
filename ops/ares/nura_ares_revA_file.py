"""File Rev-A industrial design + entity/affiliation analysis + Technical Volume skeleton."""
import json, subprocess, sys, time
PAGE = "3d8a9b14-e498-81ff-ab87-edc497410ac2"
def run(*a):
    return subprocess.run(["python3","/opt/data/scripts/notion_client.py"]+list(a),
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

b = [
div(),
h2("15. ARES Rev-A INDUSTRIAL DESIGN — ventilation + monitoring + ECLS in one chassis"),
callout("Direction adopted (Eddie + ChatGPT): do NOT co-locate a HAMILTON-T1 and a ZOLL monitor in a case — DARPA excludes 'system of systems'. Use them as reference architectures, then collapse the duplicated housings, batteries, screens, processors, alarms and sensors into ONE ARES chassis.", "✅"),

h3("15.1 Verified benchmarks (manufacturer datasheets, not estimates)"),
code("""HAMILTON-T1  (ventilation reference)
  320 x 220 x 270 mm  = 19.0 L   6.5 kg
  50 W typ / 150 W max | 72 Wh | 8.4" display
  integrated TURBINE (no compressed air) | 43 dB(A)
  MIL-STD-810G + 461F | IP54 | -15 to +50 C | 25,000 ft | RTCA/DO-160G

ZOLL Propaq M  (monitoring reference - adopted)
  226 x 264 x 178 mm  = 10.6 L   3.9 kg with battery
  73 Wh | 7.5 h monitoring | NVG-friendly display
  MIL-STD-810G (75 G shock, 1 m drop) | IP5X / IPX5 | 15,000 ft
  USAF ATL + US Army USAARL AIRWORTHINESS (JECETS): ACM rotary wing, Safe-to-fly fixed wing
  Masimo rainbow SET: SpO2, SpCO, SpMet, SpHb, SpOC, PI, PVI

T1 + Propaq M carried separately = 29.6 L / 10.4 kg"""),
bullet("Propaq M adopted over the X Series: 1.4 kg lighter, 1.4 L smaller, and it carries military airworthiness certification the X Series does not."),
bullet("Naive co-location of both in one shell = 320 x 264 x 471 mm = 39.8 L. That is a Pelican case, not a carryable platform. Integration must happen at SUBSYSTEM level."),

h3("15.2 Rev-A specification (TARGET, not achieved)"),
code("""Core chassis       : 400 x 300 x 220 mm  (~26.4 L), excl. bulk O2 and blood products
Dry mass target    : <=12-15 kg
Prolonged config   : will exceed 15 kg once ECLS consumables + mission energy included
Shared subsystems  : one enclosure+seals, one PSU/EMI, one battery rail,
                     one display+controls, one compute+software, one alarm engine,
                     one SpO2 / one EtCO2 feed, one clock, one comms module
Shared saving      : -2.6 kg vs carrying the units separately
Litter-mounted     : remains the real product; 2-4 h backpack mode = short movement only"""),

h3("15.3 Rev-A layout (four views produced)"),
bullet("FRONT — 10-12 in unified display (physiology | perfusion | resources | governor state | AIME rationale and audit | remote link); 5 glove-operable physical keys; dedicated SAFE STATE control; venous/arterial cannula ports."),
bullet("REAR — O2/LOX bay (cylinder DISS/NIST, LOX dewar, concentrator input, blended sweep); power in (100-240 VAC / 12-28 VDC vehicle-aircraft / 400 Hz); comms (WiFi, cellular, SATCOM, Ethernet); sealed thermal path; NATO litter-rail QD clamps; defib DOCK interface only."),
bullet("SIDE — battery A and B hot-swap bays; ventilator circuit port (insp/exp limb + flow sensor); Life Cartridge slot; service/data/calibration port; carry handle."),
bullet("INTERNAL CUTAWAY — ventilation module (turbine, O2 blender, valve block, flow/pressure, PEEP) + acquisition module (ECG 3/5/12, NIBP, IBP x3, temp x2, SpO2, EtCO2, respiration, rainbow SET) converging on one feed; the ARES Life Cartridge; segregated safety governor; power + compute."),

h3("15.4 THE ARES LIFE CARTRIDGE (single replaceable assembly)"),
code("""PUMP -> MEMBRANE LUNG -> SENSORS -> HEAT EXCHANGER -> MANIFOLD
 2.5-3.5 L/min   O2/CO2 exchange   flow/DP/gas/air   temp control   drug/blood/fluid

All therapy enters the RETURN limb -> the membrane never alters a drug dose.
One disposable assembly = one part number, one shelf-life, one field-replace step."""),

h3("15.5 WHAT IS ABSORBED vs CUT"),
bullet("ABSORB (sensing + ventilation): ventilation turbine architecture; ECG/arrhythmia; SpO2; EtCO2; NIBP + IBP; temperature x2; respiration; SpHb; PVI; SpOC."),
bullet("SpHb and PVI are HIGH VALUE: the round-2 analysis established that oxygen transfer falls as haemoglobin falls, so Hb must be an input to the pulmonary controller. The ZOLL front-end already supplies noninvasive Hb and fluid responsiveness — the monitor is the perfusion state estimator's SENSOR FRONT-END, not merely a display."),
bullet("CUT: defibrillation (200 J biphasic) and transcutaneous pacing — DARPA does not require them, every medic already carries a defib, and adding therapy escalates the regulatory class markedly. Provide a DOCKING/electrical interface so the function can be added in Rev-B without redesigning ARES."),
bullet("CUT: thermal printer (data is digital). CUT: compressed-air input (turbine only, T1-class)."),

h3("15.6 VERIFIED INTEGRATION TRAP — altitude"),
callout("Both ZOLL candidates (X Series AND Propaq M) are rated to 15,000 ft. The HAMILTON-T1 is rated to 25,000 ft. A naive integration takes min() = 15,000 ft, making ARES LESS capable than the ventilator it replaces. Rotary-wing mountain CASEVAC regularly exceeds 15,000 ft. Either re-qualify the acquisition front-end to 25,000 ft, or document a 15,000 ft ceiling as a deliberate limitation.", "🔴"),
bullet("Second altitude effect: EtCO2 reads LOW at altitude per Dalton's law (stated in ZOLL's own manual). Altitude compensation must be designed into both the ventilation and acquisition paths, not retrofitted."),

h3("15.7 Why integrating ventilation is not feature creep"),
bullet("DARPA states that when partial extracorporeal oxygen support is proposed, the casualty may be assumed already intubated — and that proposals integrating with mechanical ventilation WHEN PRESENT are PREFERRED."),
bullet("Therefore a T1-class ventilator integrated directly into ARES directly strengthens the technical response to PERF-03 rather than adding unrequested scope."),

h3("15.8 Standards ARES should target (from the benchmarks)"),
bullet("Environment: MIL-STD-810G/H (temperature, shock, drop, vibration), MIL-STD-461F/G (EMI)."),
bullet("Airworthiness: RTCA/DO-160G, and JECETS as invoked by USAF ATL / US Army USAARL."),
bullet("Ground: EN 1789 (ambulance), ISO 10651-3 / EN 794-3 (transport ventilators)."),
bullet("Ingress: IP54 is the T1 floor; IP55 is the Rev-A target."),

h2("16. SBIR ENTITY & AFFILIATION ANALYSIS (resolves round-3 decision #1)"),
h3("16.1 The facts on record"),
code("""Nuratech AI LLC     (Wyoming)  - "primary legal entity supporting NURATECH AI operations and IP"
Nuratech AI 2 LLC   (Montana)  - "holding or special-purpose entity\""""),
h3("16.2 The rules that bite"),
bullet("SBIR/STTR permits ONE qualifying small business concern as the proposer. Every other entity under common control becomes an AFFILIATE."),
bullet("Affiliation rules AGGREGATE employees and revenue across commonly controlled entities when applying the size standard. Two LLCs under the same control are measured as one."),
bullet("The proposing entity must be a for-profit US small business, more than 50% owned and controlled by US citizens or permanent resident aliens, with no more than 500 employees (aggregated)."),
bullet("The proposal must state the entity's legal name and its Unique Entity ID (UEI). SAM registration is PER LEGAL ENTITY — registering the wrong one wastes the lead time."),
h3("16.3 The strategic consequence"),
bullet("The durable intellectual property the ARES strategy rests on — NURA OS, Hermes adaptation, AIME architecture, digital twin, safety-governor framework — is recorded in the WYOMING entity."),
bullet("If the MONTANA entity proposes, the background IP and the proposed work sit in different legal persons. That is a technical-data-rights and teaming problem, not a filing formality."),
bullet("Recommendation: propose through the WYOMING entity (operations + IP), with the Montana entity disclosed as an affiliate in the ownership/affiliation section. Confirm with counsel before SAM registration."),
todo("Confirm with counsel: proposing entity = Nuratech AI LLC (Wyoming); Montana LLC disclosed as affiliate; aggregated headcount and revenue verified against the 500-employee size standard; UEI obtained for the Wyoming entity."),

h2("17. TECHNICAL VOLUME SKELETON — 20-page map (proposal shape)"),
para("The program plan is not the proposal. The binding artefact is a 20-page Technical Volume in DARPA's prescribed order. This is the page allocation that protects the DP2 gate and the autonomy story."),
code("""DARPA-prescribed sequence                    pages   must answer
 1 Significance of the problem                 1.5   why this matters (hemorrhage + organ failure, LSCO)
 2 Phase-II technical objectives                1.5   what will exist at M24, measurable
 3 DP2 EVIDENCE PACKAGE (gate)                  3.0   the four thresholds + the autonomy loop   << CRITICAL
 4 Detailed base SOW                            3.0   by DARPA month 1/3/6/9/12/15/18/21/24
 5 Human / animal use + IACUC-ACURO             1.5   site, sequence, secondary review
 6 Option SOW (months 25/28/30)                 1.0   24-h integrated polytrauma model
 7 Related work + competitive landscape         1.0   MELS, PAS, commercial ECLS
 8 Relationship to future R&D / Phase III       1.5   transition + commercialization
 9 Key personnel                                1.0   PI, chief engineer, critical care lead
10 Foreign citizens / facilities / equipment    1.0   disclosures + labs
11 Technical data rights + IP assertions        1.0   background/foreground, MELS FTO
12 Subcontractors / consultants                 0.5   work share + >=50% compliance
                                                       ------------------------------
                                                       ~20 pages"""),
h3("17.1 Scope-cut list — what ARES will explicitly NOT do in Phase II"),
bullet("No autonomous cannulation (out of scope per DARPA)."),
bullet("No defibrillation or pacing in Rev-A (interface only)."),
bullet("No venous-access decision support."),
bullet("No new membrane chemistry — integrate existing oxygenator technology."),
bullet("No new pump development — integrate or license."),
bullet("No 72-hour onboard battery or oxygen (hot-swap + resupply architecture)."),
bullet("No RRT in the base period (option only)."),
bullet("No hospital-ward features — austere en-route care only."),
para("Publishing this list is a scoring instrument under a hard 20-page limit: it demonstrates scope discipline and prevents reviewers from pricing unrequested work."),

h2("18. ROUND-4 DECISIONS"),
todo("Freeze Rev-A envelope at 400 x 300 x 220 mm and the <=12-15 kg dry target as the engineering baseline."),
todo("Decide the altitude posture: re-qualify acquisition to 25,000 ft, or document a 15,000 ft limitation."),
todo("Confirm the defibrillation docking interface is the Rev-A boundary (function deferred to Rev-B)."),
todo("Approve the Life Cartridge as a single field-replaceable disposable (one part number, one shelf life)."),
todo("Adopt the 20-page Technical Volume page allocation and the scope-cut list."),
todo("Have counsel confirm the Wyoming proposing entity + affiliate disclosure before SAM/UEI."),

div(),
para("Round-4 (Rev-A industrial design, entity analysis, Technical Volume skeleton) by Hermes CTO, 2026-09-11. Vendor dimensions and masses verified against Hamilton Medical and ZOLL datasheets; Rev-A ARES figures are engineering targets only."),
]

for i in range(0, len(b), 90):
    out = run("append", PAGE, json.dumps(b[i:i+90]))
    try: n = len(json.loads(out.stdout).get("results", []))
    except Exception: n = "ERR " + out.stdout[:150]
    print(f"chunk {i//90+1}: {n} blocks")
time.sleep(1)
try:
    rb = run("children", PAGE)
    print("page total blocks:", len(json.loads(rb.stdout).get("results", [])))
except Exception as e: print("children:", e)
