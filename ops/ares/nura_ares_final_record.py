"""Record Rev-A.1 final corrections + DP2 readiness in Notion."""
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
def callout(x,e="📌"): return {"object":"block","type":"callout","callout":{"rich_text":[t(x)],"icon":{"type":"emoji","emoji":e}}}
def code(x): return {"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":x}}],"language":"plain text"}}
def div(): return {"object":"block","type":"divider","divider":{}}

b = [
div(),
h2("23. Rev-A.1 FROZEN — final corrections applied + DP2 READINESS metric live"),
callout("Eddie's final engineering note accepted in full. Three corrections applied, no feature additions. Rev-A.1 is accepted as configuration-controlled. The next milestone is DP2 EVIDENCE READY, not Rev-A.2.", "🔒"),

h3("23.1 Correction 1 — oxygen altitude penalty RETRACTED as a requirement"),
callout("I got this wrong and it is worth recording plainly. I derived 2.69x as the ambient-pressure ratio at 25,000 ft and applied it to O2 INVENTORY consumption. That is a category error: a volumetric ratio applied to a design whose flow is mass/molar referenced. Retagged CALCULATED / REQUIRES VALIDATION.", "⚠️"),
code("""THREE FLOW DEFINITIONS NOW MANDATORY
  SLPM  Standard L/min (0 C / 1 atm)  ->  SLPM is proportional to MOLAR/MASS flow. Mass-referenced.
  ALPM  Actual L/min at local T and P ->  ALPM = SLPM x (P_std/P_act) x (T_act/T_std)
  g/min MASS flow                     ->  the conserved quantity; what a cylinder actually loses

WHERE 2.69x APPLIES
  CASE 1  ambient volumetric blower (ALPM-constrained)        -> PENALTY IS PHYSICAL
  CASE 2  cylinder + regulator + MASS-FLOW CONTROL            -> NO PENALTY (molar-constrained)
  CASE 3  cylinder + regulator + fixed orifice                -> ARCHITECTURE-DEPENDENT, must measure
  Rev-A.1 specifies CASE 2 or 3, NOT CASE 1.

AND THE CO2 SIDE PUSHES THE OPPOSITE WAY
  Driven by PARTIAL PRESSURE. Equilibrium CO2 mole fraction RISES with altitude:
     0 ft P=760  X_eq 0.0592   |  16,000 ft P=412  X_eq 0.1092   |  25,000 ft P=282  X_eq 0.1595
  At altitude the sweep can carry MORE CO2 before equilibrium -> same removal may need LESS sweep.
  The two effects partially offset. NEITHER DIRECTION MAY BE ASSUMED.

INVENTORY SPREAD BY ARCHITECTURE -- 24 h at 80 mL/min CO2
  CASE 1 ambient blower        6,576 L   LOX 9.9 kg
  CASE 2 mass-flow control     2,441 L   LOX 4.4 kg
  CASE 3 fixed orifice         1,487 L   LOX 3.2 kg
  -> 4.4x spread. THE GAS-DELIVERY DESIGN CHOICE DECIDES THE LOGISTICS."""),
bullet("METROLOGY REGISTER now mandatory in ICD 3.4: flow reference condition for every number; sweep upstream pressure + control mode (MFC/orifice/blower); membrane inlet/outlet ABSOLUTE pressures; whether exhaust is pressure-regulated or ambient-referenced (THE DECIDING PARAMETER); FiO2 at blender outlet and membrane inlet; mass-flow measurement on the O2 supply; temperature at each point; blood-side Hb/saturation/Q/temperature."),
bullet("SIX TESTS ADDED to the bench-rig spec: M1 SLPM-ALPM verification per altitude; M2 O2 consumption vs altitude per architecture; M3 control-mode characterisation; M4 pressure-regulated vs ambient-referenced A/B (THE DECISIVE TEST); M5 CO2 removal vs molar sweep per altitude; M6 FiO2 accuracy through the full gas path."),
bullet("Pressure-regulated sweep remains strategically attractive BUT its benefit must be PROVEN (test M4), not asserted. Until then it is a hypothesis to be tested in Phase II, not an ICD requirement."),
para("Net effect: the oxygen-logistics argument, previously one of our strongest points, must now be EARNED ON THE BENCH. That is correct — and it is also an opportunity: a measured, architecture-aware oxygen model with a validated pressure-regulated sweep is a defensible technical contribution most competitors will not have. It belongs in the Phase II SOW."),

h3("23.2 Correction 2 — accounting-system language"),
bullet("RETIRED: 'DCMA accounting-system approval required' — a false universal gate."),
bullet("ADOPTED: 'Cost-reimbursement accounting-system adequacy determination / pre-award review AS REQUIRED BY THE CONTRACTING OFFICER.'"),
bullet("If cost-reimbursement is contemplated the accounting system must be adequate for that contract type, but the exact review/approval route must be CONFIRMED from the current solicitation and cognizant contracting office. Compliance row rewritten."),

h3("23.3 Correction 3 — mount interface is now a defined requirement"),
bullet("RETIRED: '2x NATO litter-rail QD clamps.' A mechanical interface cannot become a specification merely because we call it NATO-compatible."),
bullet("ADOPTED: MOUNT-01 — TARGET/UNKNOWN, added to the ICD (4a) and the compliance matrix."),
bullet("TEN UNIDENTIFIED INPUTS: exact litter model(s) + rail geometry; restraint/attachment standard; aircraft interface standard; ambulance interface standard (EN 1789); load cases (static/dynamic/crash); crash loads; vibration environment (rotary + fixed wing); retention incl. secondary; approved transport-interfaces register; compliant mounting hardware candidates."),
bullet("Until resolved, MOUNT-01 is EXCLUDED from any mass or interface commitment. Candidate regimes to research: STANAG 2040 and the aeromedical standards invoked by JECETS / USAF ATL / US Army USAARL."),

h2("24. DP2 READINESS — the top-level metric"),
callout("0 OF 5 GATES GREEN. States (four only): NO EVIDENCE -> PARTNER CLAIM -> VERIFIED DATA -> PROPOSAL-READY EVIDENCE. Until all five are PROPOSAL-READY EVIDENCE, proposal writing is SECONDARY.", "🟥"),
code("""GATE      REQUIREMENT                              STATE
G02       Portable battery-operated prototype       NO EVIDENCE   no prototype reviewed; partner required
G03       Blood flow >=2 L/min                     NO EVIDENCE   PAS 2 L/min x10d ovine is a CLAIM until raw data
G04       >=75 mL/min O2 transfer                  NO EVIDENCE   PAS ~117 -> 90-92 mL/min: public summary only
G05       >=40 mL/min CO2 removal                  NO EVIDENCE   NO public qualifying figure found for ANY candidate
G06/G07   Qualifying autonomy (Option A)           NO EVIDENCE   no candidate has public qualifying evidence -> NURA'S WEDGE"""),
bullet("CLASSIFICATION DISCIPLINE: literature claims not supplied as raw data by the partner are PARTNER CLAIM, never VERIFIED DATA. That is the difference between 'the paper says' and 'we can submit it'."),
bullet("Live board: 00-DP2-READINESS-BOARD.png | machine-readable: 00-DP2-READINESS-SCOREBOARD.csv"),

h2("25. EXECUTION ORDER (each unblocks the next)"),
num("Confirm Wyoming proposing entity, UEI and SAM status."),
num("Submit the DARPA interpretation questions while direct clarification remains available."),
num("Lock the SBIR-eligible PI and the seven missing technical/regulatory roles."),
num("Contact the A/A+ extracorporeal partners — NDA + bench access (Artifact 09)."),
num("Determine whether newly generated pre-submission bench evidence can satisfy DP2; if yes, execute Option-A qualification immediately."),
num("Complete the real NIST 800-171 / SPRS gap assessment and POA&M."),
num("Resolve topic cost ceiling, contract type and accounting-system requirements."),
num("Run PDR with ICD, Life Cartridge architecture, mass/volume reconciliation, FMEA, traceability matrix and VERIFIED partner hardware data."),
callout("SEQUENCING DEPENDENCY: item 5 gates item 4's value. If DARPA says bench-generated data cannot satisfy DP2, the Option-A rig is not an eligibility pathway and the partner strategy must carry the whole gate. This question should go to SBIR_BAA@darpa.mil BEFORE the rig is funded.", "🔗"),

h2("26. FREEZE RULE (in force)"),
para("Any architecture change requires ONE of four triggers:"),
bullet("New DARPA requirement · Verified partner constraint · Bench/test result · CAD/PDR finding"),
bullet("Every change gets a configuration-control record showing impact on: MASS · POWER · SAFETY · SCHEDULE · REGULATORY · DP2. No undocumented drift. No feature additions."),

div(),
para("Rev-A.1 final corrections by Hermes CTO, 2026-09-11. All oxygen figures CALCULATED / REQUIRES VALIDATION. Vendor reference data verified against manufacturer datasheets and FDA records. No partner contacted; no DARPA question submitted; no prototype exists."),
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
