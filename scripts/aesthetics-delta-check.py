import re
doc = open("/opt/data/home/nura-clinical-platform/docs/clinical/aesthetics/SURGICAL-SUITE.md").read().lower()
cheat = open("/opt/data/home/nura-clinical-platform/docs/clinical/aesthetics/AESTHETICS-CHEAT-SHEET.md").read().lower()
combined = doc + " " + cheat

items = {
    "procedures": ["neck/jowls", "dorsal hump", "arms", "upper abdomen", "lower abdomen", "flanks", "hips",
                   "upper back", "bra roll", "lower back", "lateral thighs", "medial thighs", "posterior thighs",
                   "knees", "lower leg", "ankles", "mini abdominoplasty", "brachioplasty", "skin biopsy"],
    "medications": ["lidocaine", "epinephrine", "lactated ringer", "clonidine", "keflex", "cephalexin",
                    "augmentin", "bactrim", "vancomycin", "tylenol", "acetaminophen", "ibuprofen",
                    "valium", "diazepam", "norco", "hydrocodone", "oxycodone", "benadryl", "diphenhydramine"],
    "equipment": ["klein pump", "infiltration cannulas", "microaire", "pal-compatible", "portable suction",
                  "canisters", "tubing", "skin punch", "surgical tray", "bovie", "lap pads", "gauze",
                  "sterile drapes", "towels", "syringes", "needles", "vicryl", "monocryl", "mastisol",
                  "steri-strips", "tegaderm", "opsite", "markers"],
}
missing = {k: [i for i in v if i not in combined] for k, v in items.items()}
for k, m in missing.items():
    print(f"{k}: {len(items[k])} checked | missing: {m if m else 'NONE — all present'}")
