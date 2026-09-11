"""Record the Rev-A.1 engineering-artifact set in Notion."""
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
def callout(x,e="📌"): return {"object":"block","type":"callout","callout":{"rich_text":[t(x)],"icon":{"type":"emoji","emoji":e}}}
def code(x): return {"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":x}}],"language":"plain text"}}
def div(): return {"object":"block","type":"divider","divider":{}}

b = [
div(),
h2("22. Rev-A.1 ENGINEERING CLOSURE — decisions adopted, 10 artifacts delivered"),
callout("Eddie authorised Rev-A.1 with 16 decisions and directed a move from architecture prose to engineering artifacts. All 16 decisions are adopted and recorded; all 10 requested artifacts are produced. Baseline is configuration-controlled at 16-17 kg dry.", "✅"),

h3("22.1 Decisions adopted (1-16)"),
code(""" 1 MASS        accept 16-17 kg dry; <=15 kg aspiration only; 7-step recovery order; CAD packing <=80-85% at PDR
 2 CARTRIDGE   WET=disposable / DRY=durable FROZEN; NO routine in-use replacement in Rev-A (Rev-B)
 3 REDUNDANCY  one logical system + one operator interface WITH independent safety-critical redundancy
 4 BEM         two levels; AIME reasons FROM altitude but NEVER generates compensation equations
 5 OXYGEN      source-agnostic common interface; 4 mission configs; consumption = sweep x FiO2 x reserve
 6 SpHb/PVI    retained as state-estimator inputs; authority DOWNGRADED (no autonomous triggers)
 7 PHARMA       "never alters a dose" RETIRED; circuit PK must be MODELLED; Pharmacology Model added
 8 AI SAFETY   Policy Challenge Engine: differential -> counterfactual harm -> invariant -> MCU
 9 TRIAGE      ARES does NOT allocate; human medical/command authority; optimisation starts AFTER assignment
10 FUTILITY    no autonomous withdrawal; may predict/ conserve/ recommend/ document -- not terminate
11 PERFUSION  fund invasive ground truth to validate the noninvasive estimator; uncertainty + abstention
12 STAFFING   P0 PROGRAM GATE - 7 named/committed roles; software team cannot substitute
13 COST       integrate/licence proven hardware; differentiate on software + autonomy + safety
14 DEADLINE   internal no-fail 21 Oct 12:00 ET; 23 Oct = contingency margin, not production time
15 BRANDING   "NURA ARES powered by AIME"; never "three devices in one enclosure"
16 ARTIFACTS  10 delivered (below)"""),
bullet("On decision 14: my own verification of the DARPA topic page read 'Closes: Oct. 23, 2026'. The conservative internal date of 21 Oct is adopted as directed and is the correct risk posture."),

h3("22.2 Artifacts delivered (all 10) — repo eddieg73/NURA → ops/ares/revA1/"),
code("""00  Decisions record & index          .md   16 decisions + headline numbers + P0 items
01  Interface Control Document         .md   11 sections: electrical/gas/fluid/sensor/control/HMI/env
02  Life Cartridge wet/dry             .md + .png   frozen split + exploded drawing
03  Mass + volume roll-up              .csv  (03b cartridge mass separate)  confidence bands
04  Power budget by mode               .csv  13 subsystems x 7 operating modes
05  Oxygen budget                     .csv  63 rows: altitude x FiO2 x sweep x duration
06  Single-fault / FMEA table         .csv  20 rows, 10 critical-severity
07  Traceability matrix               .csv  14 sensor->estimator->controller->actuator chains
08  DP2 Option-A bench-rig spec       .md   14 tests, metrics, hard constraints
09  Partner data-request package      .md   10 targets, 18-item checklist, draft email, scorecard
10  DARPA compliance/evidence matrix  .csv  45 requirements, 18 open/blocker"""),
bullet("Every numeric cell carries a confidence tag: VERIFIED / PARTNER DATA / CALCULATED / ENGINEERING ESTIMATE / TARGET / UNKNOWN."),

h3("22.3 Two corrections the artifacts surfaced"),
callout("1) POWER WAS UNDERESTIMATED ~60%. Rev-A carried ~100 W nominal; the bottom-up budget is 161 W. Endurance on 4 modules at full nominal is 7.5 h, not 8 h. 2) TWO METHODS DIVERGE 3.4 kg on the dry core: 12.42 kg bottom-up vs 15.80 kg top-down. That divergence IS the current uncertainty. PDR requirement: reconcile within +/-1 kg.", "⚠️"),

h3("22.4 The oxygen finding that became ICD-critical"),
bullet("Sweep requirement at the 80 mL/min CO2 target: 1.573 L/min (STP) = 1.333 L/min ideal x 1.18 reserve."),
bullet("Ambient-exhaust sweep at 25,000 ft needs x2.69 the volumetric flow (ambient 282 mmHg vs sea level 760)."),
bullet("24 h at 80 mL/min CO2: 10,092 L at 25,000 ft ambient-exhaust vs 3,773 L at sea level."),
bullet("PRESSURE-REGULATING the sweep channel eliminates the penalty entirely (x1.00). The regulator's mass and power are trivial next to the oxygen."),
bullet("LOX crossover point is ~8-12 h. At 24 h: LOX 4.2 kg vs composite cylinder 11.0 kg."),

h3("22.5 Wet/dry cartridge — frozen"),
code("""WET (disposable, per mission)   2.22 kg   blood circuit .62 | head .11 | oxygenator .74
                                            HX surface .19 | air chamber .16 | manifold .33 | diaphragms .07
DRY (durable, in core)          counted in Artifact 03
Magnetic drive = no shaft seal crosses the boundary
  -> removes a thrombus nucleation site AND a sterility failure mode, for free"""),
bullet("NO routine in-use replacement in Rev-A. FMEA consequence: cartridge failure is mitigated by detection + conservation mode + escalation, NOT field replacement. This must be stated in the proposal so a reviewer does not assume an unqualified hot-swap capability."),

h3("22.6 Remaining P0 blockers"),
bullet("SAM.gov status + UEI (possibly the true blocker) · proposing entity (Wyoming recommended) · PI + 7 staffing roles · NIST SP 800-171/SPRS · DARPA written position on integrated-prototype interpretation · DARPA position on whether bench-generated data counts toward DP2 · oxygen architecture selection · cost model/topic ceiling · DCMA accounting gate · partner authorisation."),
callout("NOT done, by design: no partner contacted, no email sent, no DARPA question submitted, no prototype exists, no SAM registration confirmed, no cost volume, no CAD.", "🔒"),

div(),
para("Rev-A.1 engineering closure by Hermes CTO, 2026-09-11. Decisions 1-16 adopted as directed. All masses, powers and gas figures are engineering estimates or calculations at concept fidelity and are NOT specifications. Vendor reference data verified against manufacturer datasheets and FDA records."),
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
