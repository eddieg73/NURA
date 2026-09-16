"""File the Rev-A Architecture Baseline (corrections accepted) to Notion."""
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
def todo(x): return {"object":"block","type":"to_do","to_do":{"rich_text":[t(x)],"checked":False}}
def callout(x,e="📌"): return {"object":"block","type":"callout","callout":{"rich_text":[t(x)],"icon":{"type":"emoji","emoji":e}}}
def code(x): return {"object":"block","type":"code","code":{"rich_text":[{"type":"text","text":{"content":x}}],"language":"plain text"}}
def div(): return {"object":"block","type":"divider","divider":{}}

b = [
div(),
h2("19. ARES Rev-A ARCHITECTURE BASELINE — proposed for freeze"),
callout("Six corrections accepted. Two of them are substantive: (a) 'inherit qualification' was wrong and is replaced by 'leverage prior qualification evidence', and (b) altitude is now handled by ONE Barometric Environment Manager instead of per-subsystem patches. Both are applied below, and the mass arithmetic has been re-run against the three gates.", "✅"),

h3("19.1 Correction record"),
code("""Item                 WAS                              NOW
OEM qualification    "inherit airworthiness"          "leverage prior qualification evidence"
Altitude ceiling     accept reference's 15,000 ft     25,000 ft / 7,620 m SYSTEM target
Altitude handling    per-subsystem patches            ONE Barometric Environment Manager
Module model         3 modules in a case              3 engines on 1 shared substrate
Defibrillation       dock + interface                 CONFIRMED - dock only, not Rev-A
Chassis mass         committed <=15 kg                STRETCH; baseline 16-17 kg
Consumables          ambiguous                        explicitly OUTSIDE device mass"""),
bullet("On qualification: OEM subassembly data can reduce risk and support similarity/qualification arguments, but the INTEGRATED ARES device must still be qualified as a system — vibration, EMC, altitude, thermal, power quality, mechanical mounting, gas flow, aeromedical. The phrase 'inherit' is retired from all ARES documents."),

h3("19.2 Core architecture — one machine, not three in a case"),
code("""                       NURA ARES CORE
                             |
        +--------------------+--------------------+
        |                    |                    |
  Ventilation          Monitoring              ECLS
    engine            acquisition             engine
        |                    |                    |
        +--------------------+--------------------+
                             |
              BAROMETRIC ENVIRONMENT MANAGER
                             |
                    SHARED SENSOR BUS
        SpO2 · EtCO2 · ECG · SpHb · PVI · pressure · flow · temp
                             |
                PHYSIOLOGIC DIGITAL TWIN
                             |
                           AIME
                             |
              VALIDATED CLOSED-LOOP CONTROLLERS
                             |
                    SAFETY GOVERNOR"""),
bullet("The same barometric pressure sensor, SpO2 channel, EtCO2 channel, temperature system, clock, comms modem and battery controller feed ventilation, monitoring, ECLS, AIME and the safety kernel."),
bullet("That single-instance discipline IS the mass saving — not three modules sharing a lid."),

h3("19.3 BAROMETRIC ENVIRONMENT MANAGER — promoted by evidence"),
callout("A peer-reviewed altitude-chamber study changes this from a good idea into a validation-critical subsystem. PMID 25159349 tested the Impact 731, HAMILTON-T1 and CareFusion Revel at sea level, 8,000, 16,000 and 22,000 ft (barometric 760/564/412/321 mmHg) and found the T1 held set tidal volume within 10% ONLY at 8,000 ft; above that it delivered LARGER VT than set. Only the 731 actively compensated at all tested altitudes. The study's own conclusion: 'Altitude compensation is an active software algorithm.'", "🔴"),
bullet("Hamilton's own alarm table lists 'Performance limited by high altitude' — the manufacturer acknowledges the limitation. A 25,000 ft rating buys SURVIVABILITY, not volume ACCURACY."),
bullet("The T1's FDA 510(k) K120670 does describe automatic barometric compensation and RTCA/DO-160F high-altitude environmental testing — but environmental testing is not delivery-accuracy validation."),
bullet("ONE manager drives every correction from a single ambient-pressure source: ventilator flow and volume; capnography (Dalton's law); O2 partial-pressure interpretation; gas density; membrane-lung sweep calculations; concentrator output; cooling capacity; alarm thresholds."),
bullet("Handled per-subsystem these corrections drift apart. Handled centrally they are one validated curve with one calibration record."),
bullet("REQUIRED TEST PROTOCOL: altitude chamber; VT delivery accuracy at sea level / 8k / 16k / 22k / 25k ft; adult and paediatric; PEEP 0 and 20 cmH2O; FiO2 0.21 and 1.0; acceptance criteria stated before test. This is a proposal-strengthening glide path DARPA asks for and competitors will likely lack."),
todo("Add the altitude-chamber VT-accuracy protocol to the V&V matrix and the SOW, with the BEM as the device under test."),

h3("19.4 Three mass gates (arithmetic re-run)"),
code("""GATE 1 - core electronics + monitor + ventilator          target <=9 kg
  T1 reference + Propaq M reference (whole units)              10.40
  less duplicated display / battery / enclosure / PSU / cabling -2.60
  plus Barometric Environment Manager + shared sensor bus      +0.35
  plus shared compute backbone (AIME host + logging)           +0.45
  ----------------------------------------------------------------
  GATE 1                                                        8.60  PASS (+0.40)

GATE 2 - ECLS pump + dry cartridge hardware               target <=5 kg
  pump + drive, membrane lung, cartridge shell,
  heat exchanger, valves/sensors, retention                     4.60
  ----------------------------------------------------------------
  GATE 2                                                        4.60  PASS (+0.40)

GATE 3 - complete dry operational chassis            stretch <=15 kg
  sealed IP55 enclosure, litter-rail clamps,
  sealed thermal path, fasteners and gaskets                    2.60
  ----------------------------------------------------------------
  GATE 3 = 8.60 + 4.60 + 2.60                                  15.80  MISS (-0.80)

OUTSIDE ALL GATES (mission consumables - never hidden in device mass):
  O2 / LOX, blood products, drugs, mission batteries"""),
callout("Honest reading: the stretch does not close. Gates 1 + 2 total 13.20 kg, already 0.80 kg past the 14 kg implicit budget inside a 15 kg chassis — before any structure. A 2.60 kg structural allowance is not optional for a MIL-STD sealed, litter-clamped device. RECOMMENDATION: plan the baseline at 16-17 kg and carry <=15 kg as an aspiration contingent on Gate 1 landing low. Stating 15 kg as a committed spec invites a reviewer to price a device that cannot be built.", "⚠️"),

h3("19.5 Why the defibrillation position is right"),
bullet("Internalising defib would drag high-voltage isolation, paddle/pad interfaces, capacitor charging, defibrillation waveform validation and a separate EMC campaign into the first DARPA build."),
bullet("Schedule and regulatory cost with no scored benefit — DARPA does not ask for it and every medic already carries a defib."),
bullet("Rev-A provides a DOCKING/electrical interface so the function can be added in Rev-B without redesigning ARES."),

h3("19.6 Corrected reference numbers (verified)"),
code("""HAMILTON-T1   320 x 220 x 270 mm (19.0 L) · 6.5 kg · 50 W typ / 150 W max
              72 Wh per battery · ~4 h one / ~8 h two · 8.4" display
              integrated turbine · 43 dB(A) · IP54 · -15 to +50 C
              max altitude 7,620 m (25,000 ft) · MIL-STD-810G + 461F · RTCA/DO-160G
              FDA 510(k) K120670
              alarm: "Performance limited by high altitude"

ZOLL Propaq M 226 x 264 x 178 mm (10.6 L) · 3.9 kg with battery
              73 Wh · 7.5 h monitoring · NVG-friendly display
              MIL-STD-810G (75 G shock, 1 m drop) · IP5X / IPX5 · 15,000 ft
              USAF ATL + US Army USAARL airworthiness (JECETS)
              Masimo rainbow SET: SpO2, SpCO, SpMet, SpHb, SpOC, PI, PVI

REFERENCE PAIR TOTAL: 29.6 L / 10.4 kg (before any ECLS hardware)"""),
bullet("Note for the record: JECETS (Joint Enroute Care Equipment Test Standards) is the airworthiness regime ARES should target, since it is what the USAF ATL and US Army USAARL actually certify against."),

h2("20. Rev-A BASELINE DECISIONS"),
todo("FREEZE Rev-A architecture: 3 engines on 1 shared substrate + 1 Barometric Environment Manager; no module-in-a-case framing."),
todo("Adopt 25,000 ft / 7,620 m as the SYSTEM engineering target (not 15,000 ft from a reference monitor)."),
todo("Adopt the three mass gates; restate the chassis as a 16-17 kg baseline with <=15 kg as stretch, not a committed spec."),
todo("Retire the words 'inherit qualification' from all ARES documents; use 'leverage prior qualification evidence'."),
todo("Add the BEM altitude-chamber VT-accuracy protocol to the V&V matrix and SOW."),
todo("Keep defibrillation as a dock/interface only; document the Rev-B path."),
todo("State explicitly in the proposal that O2, blood, drugs and mission batteries are consumables outside device mass."),

div(),
para("Rev-A architecture baseline by Hermes CTO, 2026-09-11. Corrections accepted from Eddie + ChatGPT review. Altitude evidence: PMID 25159349; Hamilton T1 tech specs and FDA 510(k) K120670; ZOLL Propaq M spec sheet. ARES masses remain engineering estimates — no prototype exists."),
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
