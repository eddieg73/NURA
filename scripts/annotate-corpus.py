#!/usr/bin/env python3
"""NURA corpus annotator — cleaning + clinical entity annotation (spec 2.2).
Pipeline: PHI scrub -> acronym normalization -> entity annotation (Diagnosis, Medications,
Symptoms, Procedures, Treatment Plan) -> annotated JSONL + stats."""
import json, re, sys
from pathlib import Path

IN = Path("/opt/data/home/nura-clinical-platform/data/training/nura-corpus.jsonl")
OUT = Path("/opt/data/home/nura-clinical-platform/data/training/nura-corpus-annotated.jsonl")
STATS = Path("/opt/data/home/nura-clinical-platform/data/training/annotation-stats.json")

# --- 1. PHI scrub (de-identification) ---
PHI_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),
    (r"\b\d{9}\b", "[MRN]"),
    (r"\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b", "[PHONE]"),
    (r"\b\d{1,2}/\d{1,2}/\d{4}\b", "[DOB]"),
    (r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b", "[DATE]"),
    (r"\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b(?: reported| states| complains| denies)", "[NAME]"),
]

# --- 2. Terminology/acronym normalization ---
ACRONYMS = {
    "HTN": "hypertension", "T2DM": "type 2 diabetes mellitus", "DM2": "type 2 diabetes mellitus",
    "SOB": "shortness of breath", "CP": "chest pain", "HA": "headache", "N/V": "nausea and vomiting",
    "U/A": "urinalysis", "BP": "blood pressure", "HR": "heart rate", "RR": "respiratory rate",
    "HgbA1c": "hemoglobin A1c", "A1c": "hemoglobin A1c", "GFR": "glomerular filtration rate",
    "LFTs": "liver function tests", "CBC": "complete blood count", "CMP": "comprehensive metabolic panel",
    "NSAID": "nonsteroidal anti-inflammatory drug", "SSRI": "selective serotonin reuptake inhibitor",
    "SNF": "skilled nursing facility", "ED": "emergency department", "FU": "follow-up",
    "PRN": "as needed", "QD": "once daily", "BID": "twice daily", "TID": "three times daily",
    "HRT": "hormone replacement therapy", "GLP-1": "glucagon-like peptide-1 receptor agonist",
}

# --- 3. Entity dictionaries (annotation) ---
ENTITIES = {
    "Diagnosis": ["hypertension", "type 2 diabetes mellitus", "hyperlipidemia", "hypothyroidism",
                  "atrial fibrillation", "COPD", "asthma", "anxiety", "depression", "obesity",
                  "chronic kidney disease", "GERD", "migraine", "osteoarthritis", "OSA"],
    "Medications": ["metformin", "lisinopril", "atorvastatin", "levothyroxine", "amlodipine",
                    "metoprolol", "semaglutide", "tirzepatide", "testosterone", "estradiol",
                    "progesterone", "aspirin", "warfarin", "insulin", "gabapentin"],
    "Symptoms": ["chest pain", "shortness of breath", "headache", "fatigue", "dizziness",
                 "palpitations", "nausea", "insomnia", "joint pain", "weight gain", "hot flashes",
                 "night sweats", "libido changes", "edema"],
    "Procedures": ["colonoscopy", "echocardiogram", "stress test", "mammography", "MRI",
                   "CT scan", "ECG", "biopsy", "endoscopy", "cataract surgery", "liposuction",
                   "botox injection", "filler injection"],
    "Treatment Plan": ["lifestyle modification", "dietary changes", "exercise program",
                       "follow-up in", "referral to", "titration", "dose adjustment",
                       "monitoring labs", "patient education", "surgical consult"],
}

def scrub(text):
    for pat, rep in PHI_PATTERNS:
        text = re.sub(pat, rep, text)
    return text

def normalize(text):
    for acr, full in ACRONYMS.items():
        text = re.sub(rf"\b{re.escape(acr)}\b", full, text, flags=re.I)
    return text

def annotate(text):
    found = {k: [] for k in ENTITIES}
    low = text.lower()
    for cls, terms in ENTITIES.items():
        for t in terms:
            for m in re.finditer(rf"\b{re.escape(t)}\b", low):
                found[cls].append({"term": t, "start": m.start(), "end": m.end()})
    return found

def main():
    stats = {"records": 0, "phi_replacements": 0, "entities": {}}
    with open(IN) as fi, open(OUT, "w") as fo:
        for line in fi:
            rec = json.loads(line)
            raw = rec["text"]
            scrubbed = scrub(raw)
            n_phi = sum(len(re.findall(p, raw)) for p, _ in PHI_PATTERNS)
            cleaned = normalize(scrubbed)
            ents = annotate(cleaned)
            rec["text_clean"] = cleaned
            rec["phi_scrubbed"] = n_phi > 0
            rec["entities"] = ents
            rec.pop("text", None)
            fo.write(json.dumps(rec) + "\n")
            stats["records"] += 1
            stats["phi_replacements"] += n_phi
            for cls in ENTITIES:
                stats["entities"][cls] = stats["entities"].get(cls, 0) + len(ents[cls])
    with open(STATS, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"ANNOTATED {stats['records']} records | PHI scrubs: {stats['phi_replacements']}")
    print("Entities:", {k: v for k, v in stats["entities"].items() if v})

if __name__ == "__main__":
    main()
