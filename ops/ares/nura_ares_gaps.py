"""Append the deep gap analysis (round 2) + device concept to the ARES review page."""
import json, subprocess, sys, time

PAGE = "3d8a9b14-e498-81ff-ab87-edc497410ac2"

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
def quote(x): return {"object":"block","type":"quote","quote":{"rich_text":[t(x)]}}
def div(): return {"object":"block","type":"divider","divider":{}}

b = [
div(),
h2("9. ROUND-2 GAP ANALYSIS — what BOTH the blueprint and my first review missed"),
callout("Eddie asked for a 100-year perspective. Two of the gaps below are QUANTITATIVE and change the product definition. The rest are program-level omissions that no amount of control-theory rigour in the blueprint addresses.", "🧠"),

h3("9.1 THE BIGGEST QUANTITATIVE OMISSION — oxygen logistics MASS"),
para("The blueprint tabulates oxygen VOLUMES (2,880 L for 24 h, 8,640 L for 72 h at 2 L/min sweep) and correctly demolishes the 72-hour battery. It never does the same arithmetic for OXYGEN — which is worse."),
code("""Free gas = water-volume(L) x pressure(bar)

sweep 2 L/min                         24 h        72 h
  steel cylinder @200 bar            14.4 kg     43.2 kg
  composite cylinder @300 bar        13.9 kg     41.8 kg
  LOX + dewar                         5.0 kg     12.7 kg

sweep 4 L/min                         24 h        72 h
  composite @300 bar                 27.8 kg     83.5 kg
  LOX + dewar                         8.8 kg     24.1 kg"""),
bullet("A 24-hour mission totals ~35 kg carried mass against a 12 kg target — 2.9x over."),
bullet("Gas + power = 25.7 kg, i.e. 73% of all mass. Not the pump. Not the AI. The consumables."),
bullet("LOX instead of steel saves 9.4 kg per 24 h (5.0 vs 14.4 kg) and is the only route to 72 h."),
callout("CONCLUSION: ARES is NOT a backpack. It is a litter-mounted device with a resupply tail. The 'M9 backpack pathway' DARPA asks us to demonstrate is achievable only for ~2-4 hour hops. The oxygen supply chain — not the autonomy — decides whether this program is deployable.", "🔴"),

h3("9.2 THE TRIAGE / ALLOCATION PROBLEM — absent from the blueprint, and it is the hardest question in the program"),
para("The blueprint optimises for ONE patient. The operational reality is three casualties and one device."),
bullet("AIME's resource optimizer is scoped to a single casualty's finite blood/oxygen/battery budget."),
bullet("But the moment there is one ARES and multiple casualties, something must decide WHO gets it. That decision is currently unassigned."),
bullet("If the device refuses to make it, a field medic with no ECMO training must — which is worse than the machine deciding under a pre-approved protocol."),
bullet("If the device DOES make it, we have built a machine that performs battlefield triage. That carries legal, ethical and command-authority weight no proposal has addressed."),
para("A 2126 reviewer would call this the only genuinely 'autonomous' decision in the system — allocation under scarcity — and would find its complete absence revealing. The blueprint automates control loops and calls it autonomy."),
todo("DECISION: define ARES's allocation posture — human-directed only (device never selects a patient), vs protocol-governed recommendation (device advises, medic/med authority decides), vs autonomous under pre-approved triage criteria. Expect DARPA to ask."),

h3("9.3 AI-SPECIFIC FMEA — the safety governor does not catch the dangerous failure mode"),
para("The blueprint's governor enforces numeric limits: dose, flow, pressure, rate, sensor plausibility. It is well designed. But it defends against UNSAFE COMMANDS, not against WRONG CLINICAL REASONING that produces perfectly legal commands."),
code("""FAILURE: AIME misclassifies cardiogenic shock as haemorrhagic shock
  -> selects 'haemorrhage' policy
  -> orders fluid/blood at a rate WITHIN every configured limit
  -> safety governor sees a legal command and ALLOWS it
  -> volume overload, pulmonary oedema, death

  Nothing in the governor's ruleset is violated at any point."""),
bullet("This is the AI failure mode that matters: semantically wrong, numerically legal."),
bullet("Mitigations the blueprint does not specify: mandatory differential (never classify on one hypothesis), explicit abstention when evidence is discordant, ensemble/two-model disagreement as an automatic escalation trigger, and a pre-approved 'uncertain -> stabilise conservatively + call remote expert' policy."),
bullet("Also required: a distributional-shift detector. A combat casualty's physiology differs from every training set — the model must know when it is outside its envelope."),

h3("9.4 The perfusion estimator has a chicken-and-egg validation problem"),
bullet("The blueprint wants non-invasive perfusion-state estimation (no arterial line) — a DARPA preference, and the right goal."),
bullet("But you cannot VALIDATE a perfusion estimator without ground truth, and ground truth means an arterial line."),
bullet("So development REQUIRES the invasive reference the product claims to eliminate. The dev plan must fund arterial-instrumented animal work expressly as a ground-truth channel, then demonstrate the estimator tracks it within stated error."),
bullet("Oscillometric NIBP is least reliable exactly where ARES operates — profound shock and low flow. The proposal cannot assume it away."),

h3("9.5 Blood supply chain — never addressed"),
bullet("Phase II requires surviving ≥50% estimated blood-volume loss over 6 h. For an adult that is ~2.5-3 L of blood product."),
bullet("The blueprint lists 'blood, artificial/freeze-dried products, crystalloid are permitted' but never says WHERE blood comes from, how it stays at 4 °C, how it is typed/crossmatched, or who donates."),
bullet("In LSCO the answer is a walking blood bank and whole blood — a doctrine, a training requirement, and a logistics chain that ARES must be designed around, not assumed to have."),
bullet("This is arguably the single biggest constraint on the product's real-world utility and it is invisible in the blueprint."),

h3("9.6 Termination and futility logic — the device has no stop rule"),
bullet("A machine that sustains physiology indefinitely against finite consumables must decide when to stop, degrade to comfort care, or declare futility."),
bullet("The blueprint specifies graceful degradation of SYSTEMS (resource depletion, battery reserve) but nothing about the CLINICAL decision to withdraw."),
bullet("Withdrawal-of-support is one of the most consequential acts in medicine. Automating it — or failing to specify who performs it — is a regulatory and ethical gap, not a detail."),

h3("9.7 Physical/environmental constraints nobody listed"),
bullet("NOISE: 150-380 W of pumps, blowers and gas flow is an acoustic signature. In a contested environment, a whining pump is a detection beacon. Silent/stealth operation is a military requirement commercial ECMO never considers."),
bullet("THERMAL: the same power dissipates as heat inside a sealed case in a desert or an aircraft cabin. Waste-heat rejection is a real design driver, not an afterthought."),
bullet("AEROMEDICAL QUALIFICATION: rotary-wing vibration, altitude/pressure effects on gas exchange and bubble risk, G-loads, and MIL-STD-810H environmental qualification are absent."),
bullet("REVERSE LOGISTICS: batteries, O2, drugs, disposables and cannula spares must reach the edge. Sustainment is not in the cost model."),

h3("9.8 Regulatory and accountability gaps"),
bullet("DoD USE IS NOT FDA: the blueprint analyses only the commercial FDA pathway. Military use of an investigational device on service members follows DoD authority (waivers/IRB/combat-use provisions). Both pathways must be mapped — they are different gates."),
bullet("LIABILITY: if autonomous ARES harms a soldier, who is accountable — medic, commander, manufacturer, DoD, or the AI developer? The blueprint has an IP section and no accountability section."),
bullet("ANTI-TAMPER: a captured ARES is intelligence and potentially a weapon. Sealed/crypto-erase on tamper is a DoD expectation absent from the cybersecurity section."),
bullet("SUSTAINMENT OVER A 20-30 YEAR LIFECYCLE: chip obsolescence, membrane suppliers, battery chemistry changes, single-source risk. The Army penalises programs that cannot be sustained."),

h3("9.9 The incumbent comparison the proposal must make"),
bullet("Haemorrhage is the #1 cause of preventable death, but the intervention that saves those lives is EARLY WHOLE BLOOD — not ECMO. ECMO does not close a hole in an artery."),
bullet("ARES addresses organ-failure SEQUELAE — the later phase. That is exactly what DARPA targets, and it is correct. But the proposal must quantify the addressable cohort: casualties who survive initial resuscitation AND develop multi-organ failure AND face delayed evacuation."),
bullet("Without that number the cost-effectiveness case ($5M+ device vs a $200 blood transfusion) is unanswered, and reviewers will ask."),

h2("10. THE 100-YEAR VIEW — is this even the right primitive?"),
callout("A 2126 reviewer would say: you are automating a Rube Goldberg machine instead of eliminating the need for it. Extracorporeal circulation is a 20th-century hack — it takes blood OUT of the body, exposes it to plastic, inflames it, requires anticoagulation, and then puts it back. The durable intellectual property is NOT the pump-lung.", "🔭"),
para("But the conclusion is not 'stop'. It is an architecture decision:"),
num("The pump, oxygenator and cannula are the DISPOSABLE layer. They will be replaced by implantable/wearable artificial organs, printed tissue, or nanoscale oxygen carriers within 25-50 years."),
num("The AUTONOMY LAYER is modality-independent: physiologic state estimation, safety-bounded reasoning, an independent safety governor, resource-aware optimisation, and degraded-mode operation survive every substrate change."),
num("THEREFORE the proposal should explicitly claim the intelligence layer as the durable deliverable and treat the ECMO circuit as the current substrate — and say so in the IP and transition sections."),
num("This also answers the internal question 'what if we lose the award?' — the same autonomy + safety-governor + resource-reasoning stack is the product for every future organ-support modality, and for RATCHET, LOM and the rest of the NURA stack."),
para("The one thing a 2126 reviewer would say NURA got RIGHT: refusing to let a generative model touch an actuator. That safety-separated architecture is the part that will still be correct in a hundred years."),

h2("11. WHAT THE DEVICE LOOKS LIKE (concept render)"),
para("A four-panel engineering concept sheet was produced and delivered alongside this page: base-unit three-view with dimensions, deployment/litter-mounting with setup sequence, the single-access fluidic circuit, and the SWaP mass budget."),
code("""Form factor            : single ruggedised unit, NOT modules bolted together
Envelope               : 420 x 300 x 180 mm  (~22.7 L)
Durable mass           : 10.1 kg  (battery + oxygen = mission load)
Mount                  : 2x NATO litter-rail QD clamps  -> rides with the casualty
Display / control      : 8" sunlight-readable + 5 glove-operable physical keys
Patient interface      : ONE dual-lumen <=15 Fr central venous cannula (IJ or femoral)
Fluidics               : pump -> oxygenator -> safety governor -> therapeutic
                         manifold -> RETURN limb (so the membrane never alters a dose)
Gas                    : cylinder | LOX | concentrator  (LOX for >12 h)
Power                  : 2x hot-swappable 4 h battery bays
Setup by a field medic : ~2 minutes, then autonomous

Files: /opt/data/ares_concept.html  (source)
       /opt/data/ares_render.png     (rendered sheet)"""),

h2("12. CONSOLIDATED OPEN DECISIONS (round 2 additions)"),
todo("Define ARES's triage/allocation posture (device never selects vs advises vs autonomous under protocol)."),
todo("Decide the gas architecture: cylinders (heavy) vs LOX (light, supply chain) vs concentrator (doubles power). This determines the whole SWaP story."),
todo("Accept that ARES is litter-mounted with a resupply tail, and stop promising an M9 backpack beyond short hops."),
todo("Fund arterial-instrumented animal work as the ground-truth channel for the perfusion estimator."),
todo("Specify the AI-specific safety mitigations: mandatory differential, abstention, ensemble disagreement escalation, distributional-shift detection."),
todo("Map the DoD (non-FDA) approval pathway alongside the commercial one."),
todo("Write the liability/accountability position before counsel asks."),
todo("Quantify the addressable casualty cohort and the incumbent comparison (blood vs ECMO)."),
todo("State the triage question to DARPA explicitly — it is better to raise it than to be asked."),

div(),
para("Round-2 analysis by Hermes (CTO), 2026-09-11. Concept renders are engineering targets at concept fidelity, not measured device performance."),
]

for i in range(0, len(b), 90):
    out = run("append", PAGE, json.dumps(b[i:i+90]))
    try: n = len(json.loads(out.stdout).get("results", []))
    except Exception: n = "ERR " + out.stdout[:150]
    print(f"chunk {i//90+1}: {n} blocks")

time.sleep(1)
rb = run("children", PAGE)
try: print("page total blocks:", len(json.loads(rb.stdout).get("results", [])))
except Exception: print("children:", rb.stdout[:200])
