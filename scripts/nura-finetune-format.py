#!/usr/bin/env python3
"""NURA fine-tune formatter: the 100K patient records → the clinical-reasoning pairs.
The case (the dx + the key labs + the meds) → the assessment (the condition + the plan)
in the SOAP-shaped alpaca format for the Med42 LoRA.
Output: the JSONL pair file (the Kaggle upload).
"""
import csv, json, random
from collections import defaultdict

BASE = "/opt/data/finetune-data/patient-records"

def load_rows(name):
    with open(f"{BASE}/{name}") as f:
        return list(csv.DictReader(f))

print("loading...")
patients = {r["patient_id"]: r for r in load_rows("patients.csv")}
dxs = load_rows("diagnoses.csv")
labs = load_rows("lab_results.csv")
meds = load_rows("medications.csv")
outs = load_rows("outcomes.csv")

dx_by_patient = defaultdict(list)
lab_by_patient = defaultdict(list)
med_by_patient = defaultdict(list)

for r in dxs:
    dx_by_patient[r.get("patient_id", "")].append(r)
for r in labs:
    if r.get("is_abnormal", "").lower() == "true" or r.get("flag"):
        lab_by_patient[r.get("patient_id", "")].append(r)
for r in meds:
    med_by_patient[r.get("patient_id", "")].append(r)

print(f"patients {len(patients)}, dx {len(dxs)}, abnormal labs {sum(len(v) for v in lab_by_patient.values())}, meds {len(meds)}")

pairs = []
for pid, p in patients.items():
    dx_list = [d.get("diagnosis") or d.get("icd10") or d.get("condition") or "" for d in dx_by_patient[pid]][:4]
    lab_list = [f"{l.get('test_name','')} {l.get('value','')} {l.get('unit','')} (abn)" for l in lab_by_patient[pid]][:6]
    med_list = [f"{m.get('medication','')} {m.get('dose','')}" for m in med_by_patient[pid]][:5]
    if not dx_list:
        continue
    age = p.get("age") or "?"
    sex = p.get("sex") or p.get("gender") or "?"
    case = f"{age}{sex}, conditions: {'; '.join(dx_list)}."
    if lab_list:
        case += f" Notable labs: {'; '.join(lab_list)}."
    if med_list:
        case += f" Medications: {'; '.join(med_list)}."
    # the assessment = the structured SOAP-shaped summary from the dx + the meds
    assessment = ("S: chronic conditions on record. "
                  f"O: dx {len(dx_list)}; abnormal labs {len(lab_list)}; meds {len(med_list)}. "
                  f"A: {'; '.join(dx_list)}. "
                  "P: continue the current regimen; monitor the flagged labs; review at the next visit.")
    pairs.append({"case": case, "assessment": assessment})

random.seed(3407)
random.shuffle(pairs)
print(f"pairs: {len(pairs)}")
with open("/opt/data/finetune-data/nura-clinical-pairs.jsonl", "w") as f:
    for p in pairs[:30000]:
        f.write(json.dumps(p) + "\n")
print("wrote nura-clinical-pairs.jsonl (30K pairs)")
