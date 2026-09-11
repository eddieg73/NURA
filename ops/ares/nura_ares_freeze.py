"""Record the Rev-A baseline FREEZE decision in Notion."""
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
h2("21. FREEZE RECORD — Rev-A Architecture Baseline (Executed 2026-09-11)"),
callout("Eddie authorised the freeze. The Rev-A architecture baseline is now CONFIGURATION-CONTROLLED. Changes require a recorded decision. Baseline mass adopted at 16-17 kg dry; the 15 kg figure is retained only as an aspiration.", "🔒"),

h3("21.1 What is now frozen"),
code("""FROZEN ITEM                                      BASELINE VALUE
Core architecture                                3 engines on 1 shared substrate
Barometric Environment Manager                   SINGLE, first-class subsystem
System altitude target                           25,000 ft / 7,620 m
Chassis envelope                                 400 x 300 x 220 mm  (~26.4 L)
DRY OPERATIONAL CHASSIS MASS                     16-17 kg   <<< FROZEN BASELINE
  Gate 1  core electronics + monitor + vent      8.60 kg   (cap 9)
  Gate 2  ECLS pump + dry cartridge hardware     4.60 kg   (cap 5)
  structure allowance                            2.60 kg
  15 kg figure                                    ASPIRATION ONLY - not a commitment
Consumables                                      OUTSIDE device mass (O2/LOX, blood, drugs, batteries)
Mounting                                         2x NATO litter-rail QD clamps
Defibrillation                                   DOCK/INTERFACE ONLY (Rev-B path)
Qualification language                           "leverage prior qualification evidence"
Sharing of actuators                             AIME NEVER actuates; governor holds veto
Medic setup time target                          ~2 minutes to autonomy"""),

h3("21.2 Rationale for the mass decision"),
bullet("Gates 1+2 total 13.20 kg — already 0.80 kg past the 14 kg implicit budget inside a 15 kg chassis, before any structure."),
bullet("A 2.60 kg structural allowance is not optional for a MIL-SPEC sealed, litter-clamped device."),
bullet("Setting 15 kg as a committed specification invites a DARPA reviewer to price a device that cannot be built; 16-17 kg is defensible on capability grounds and leaves real margin."),
bullet("Gate 1 margin is only 0.40 kg and Gate 2 margin only 0.40 kg — the frozen baseline protects those margins rather than spending them on a headline number."),

h3("21.3 Consequential changes"),
bullet("All ARES documents must now use 'leverage prior qualification evidence' — the phrase 'inherit airworthiness' is retired."),
bullet("The 25,000 ft target is system-level and must be carried into the V&V matrix, the SOW and the BEM test protocol."),
bullet("The 15,000 ft figure from the reference monitor is NOT the ARES ceiling; it is a design input for the acquisition module only."),
bullet("Consumable mass must never be presented inside device mass in the proposal or in any partner discussion."),
bullet("The BEM altitude-chamber VT-accuracy protocol is now a required V&V item (sea level / 8k / 16k / 22k / 25k ft; adult + paediatric; PEEP 0 and 20; FiO2 0.21 and 1.0; acceptance criteria stated before test)."),

h3("21.4 Handoff artefact"),
para("A consolidated markdown handoff document was produced for ChatGPT containing the full verified state: reference device data, the altitude finding with citation, the frozen architecture, all three mass gates, the Rev-A physical design, the scope-cut list, the federal critical path, the SBIR entity analysis, the 20-page Technical Volume skeleton, the DARPA questions, and the open decisions."),
code("""File             : /opt/data/ARES-RevA-Baseline-Handoff.md
Length           : ~32 KB, 17 sections
Repo             : eddieg73/NURA -> ops/ares/
Supersedes       : all earlier ARES notes
Status           : Rev-A baseline FROZEN; not built; masses are estimates"""),

h3("21.5 Still outstanding (unchanged by the freeze)"),
bullet("SAM.gov registration status + UEI — remains the possible true blocker; Eddie to confirm."),
bullet("Proposing entity (Wyoming recommended) — counsel to confirm before SAM registration."),
bullet("Principal Investigator + staffing model — may be a harder gate than the DP2 evidence."),
bullet("Cost model / topic-specific ceiling verification — the $3.3-5.7M vs $1.8M gap is unresolved."),
bullet("Triage/allocation posture — absent from every document; recommend raising with DARPA."),
bullet("Oxygen architecture decision (cylinders vs LOX vs concentrator) — determines the whole SWaP story."),
bullet("Partner outreach — NOT authorised, NOT performed. No external contact has been made by Hermes."),

div(),
para("Freeze executed 2026-09-11 by Hermes CTO at Eddie's instruction. Rev-A baseline is configuration-controlled from this point."),
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
