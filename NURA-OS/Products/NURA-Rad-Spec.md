# NURA RAD — CORE CLINICAL INTELLIGENCE SPECIFICATION (2026-08-04, founder canonical)

**Product:** NURA Rad — the AI-assisted diagnostic radiology platform · **The JARVIS lane** · **The radiologist signs everything**

## 1. PRIMARY SYSTEM OBJECTIVE
Analyze every image and series in a diagnostic imaging study → a complete preliminary radiologic interpretation for review by a licensed radiologist. For every study: technical-quality assessment · confirmation every image/series was processed · normal + abnormal findings · primary radiologic diagnosis · ranked differential · must-not-miss · supporting imaging evidence · findings against each diagnosis · clinical decision support · recommended correlation/additional evaluation · urgency classification · draft findings + impression · explicit uncertainty/limitations. **The radiologist remains responsible for final interpretation, approval, amendment, and signature.**

## 2. MANDATORY COMPLETE-STUDY READING (never key images only)
Process: every study/series/image · every CT slice · every MRI sequence · every radiographic view · every US frame/selected cine · every prior comparison study · every structured measurement · all relevant DICOM metadata.
**Completion verification before interpretation:** expected vs received series · expected vs received images · successfully processed · failed · unsupported · missing series · duplicates · completion status. **If any clinically relevant image cannot be processed → state: "Incomplete AI analysis — radiologist review required." Never silently omit failed images.**

## 3. PRIMARY DIAGNOSIS
One primary diagnosis when the evidence supports a leading diagnosis — fields: {name · anatomic_location · laterality · severity · acuity · supporting_findings[] · findings_against[] · confidence_band · clinical_significance · urgency · requires_immediate_review}. Distinguish: definitive vs most-likely vs probable vs possible vs indeterminate vs requires-correlation. **Never convert uncertainty into false certainty.**

## 4. RANKED DIFFERENTIAL
1st/2nd/3rd most likely + additional plausible considerations. Per diagnosis: relative likelihood · supporting + conflicting imaging features · clinical info needed · lab correlation · prior imaging · recommended confirmatory study · potential urgency · evidence source. **Example:** RLL pneumonia (focal air-space opacity + air bronchograms + parapneumonic effusion + fever/cough) → 1 bacterial, 2 aspiration, 3 organizing, 4 less-likely pulmonary infarction; MUST-NOT-MISS: PE with infarction if acute pleuritic pain/hypoxemia/high risk.

## 5. MUST-NOT-MISS (danger listed separately from probability)
ICH · acute ischemic stroke · PE · aortic dissection · tension pneumothorax · bowel perforation · mesenteric ischemia · ectopic pregnancy · testicular torsion · spinal/cauda compression · unstable fracture · acute arterial occlusion · critical device malposition. **Never rank a dangerous-but-unlikely diagnosis above a more likely one merely because it's dangerous.**

## 6. CLINICAL DECISION SUPPORT (recommendation only — never an automatic order)
**Imaging:** contrast study · CTA · MRI · US · dedicated views · short-interval follow-up · prior comparison. **Clinical correlation:** symptoms · physical findings · trauma mechanism · surgical/cancer/infection history · medications · pregnancy. **Lab correlation:** renal function · WBC · troponin · D-dimer · LFTs · lipase · tumor markers · UA · pregnancy testing. **Procedure/specialty:** surgery · IR · neuro · oncology · pulm · ortho · breast workup. **Follow-up:** none · routine · short-interval · dedicated · tissue diagnosis · prior comparison · urgent evaluation.

## 7. IMAGING EVIDENCE FOR EVERY CONCLUSION (traceability)
Every diagnosis references: study · series · image/slice number · anatomical location · bounding box · segmentation · measurement · view · sequence · DICOM ID. **Example:** "Left temporal intraparenchymal hemorrhage — Series: Axial noncontrast CT brain — Images 42-58 — 3.4×2.6×2.9 cm — 13.4 mL — mild edema — 3 mm midline shift." **A radiologist clicks a finding → navigates to the supporting image.**

## 8. REQUIRED OUTPUT CATEGORIES
Technical Quality · Study Completeness · Comparison · Normal Findings · Abnormal Findings · Primary Diagnosis · Ranked Differential · Must-Not-Miss · CDS · Incidental Findings · Measurements · Recommendations · Limitations · Preliminary Impression · Urgency. **Normal studies state WHICH anatomy was assessed — not just "no abnormality detected."**

## 9. TRAINING DOCTRINE (learn radiology, not visual similarity)
Data: original images · final reports · radiologist annotations · primary + differential diagnosis · pathology · surgical findings · follow-up imaging · clinical outcomes · labs · procedure results · tumor response · corrected reports · radiologist disagreements · false pos/neg · normal + technically limited studies. **The training unit = complete study + clinical indication + relevant priors + final report + confirmed diagnosis/outcome + structured annotations. An isolated labeled image is NOT sufficient for comprehensive radiology reasoning.**

## 10. TRAINING DATA HIERARCHY
**L1 unlabeled** (pretraining/anatomy/modality/quality/features — not diagnostic) → **L2 image labels** (classification/detection) → **L3 localized annotations** (boxes/points/segmentations/measurements/laterality/severity — precision + explainability) → **L4 final reports** (image-language alignment, draft generation, reasoning) → **L5 confirmed clinical outcomes** (pathology/surgery/labs/follow-up/treatment response/specialist diagnosis = the strongest ground truth).

## 11. RADIOLOGIST FEEDBACK LOOP (structured, governed)
Capture: accepted/modified/rejected/added diagnosis · changed differential · missing finding · wrong laterality/measurement/urgency/recommendation · final language · signature · addendum. **Pipeline:** AI preliminary → radiologist review → structural corrections → quality/adjudication → deidentification → training-eligibility decision → curated training set → OFFLINE retraining → validation → controlled release. **The production model never retrains itself automatically after every case.**

## 12. MODEL ARCHITECTURE (one app, specialized models internally)
Universal Study Controller → DICOM Validation · Study Completeness · Technical Quality · Modality/Anatomy Classifier · Series/Protocol Classifier · Organ Segmentation · Abnormality Detection · Disease Classification · Measurement · Prior-Study Comparison · Multimodal Radiology Foundation Model · Differential Engine · CDS Engine · Report Generation · Critical Finding Engine · Report Consistency Validator.

## 13. KNOWLEDGE TO LEARN
Normal anatomy + variants · imaging physics + artifacts · normal postoperative · disease/trauma/oncology/infection patterns · vascular emergencies · degenerative · congenital · device positioning · treatment response · measurement standards · staging · structured reporting · differentials · recommendations · critical-result communication · **when images are insufficient for a diagnosis.**

## 14. DATA VOLUME
Thousands = early prototypes/narrow findings. A broad multi-modality reader: **hundreds of thousands to millions of studies** · multiple institutions/scanners/regions/populations · normal + abnormal · rare + common · longitudinal · expert-reviewed labels. **Diversity > volume — a million poorly labeled images < a smaller adjudicated dataset.**

## 15. DATASET INTAKE REQUIREMENTS
Classify each: modality · anatomy · protocol · institution · scanner manufacturer/model · age group · sex · study date · diagnosis · label quality · annotation type · report availability · outcome availability · license · commercial-use permission · research-only limitation · deidentification status · training/validation eligibility.

## 16. DATABASE RELATIONSHIPS
Patient Pseudonym → Study → Series → Image → ROI → Finding → Primary Diagnosis → Differential → Final Radiologist Diagnosis → Clinical Outcome. **The AI conclusion stays linked to the exact image evidence, report, and final outcome.**

## 17. MODEL EVALUATION (beyond classification)
**Coverage:** % images/series processed · failed-image rate · incomplete-study detection. **Diagnostics:** primary + top-3 accuracy · sens/spec/PPV/NPV · calibration · critical false-negative rate. **Localization:** box/segmentation accuracy · laterality · anatomical location · measurement error. **Reporting:** missing/hallucinated finding rate · impression accuracy · recommendation appropriateness · contradiction rate · radiologist edit distance. **Workflow:** time saved · turnaround · critical-study prioritization · acceptance/correction rate · missed critical finding rate.

## 18. RADIOLOGIST REVIEW REQUIREMENTS
Review every original image + every AI finding · navigate to supporting images · accept/modify/reject findings · add missed findings · modify primary · reorder differential · add must-not-miss · modify recommendations · change urgency · edit the complete report · approve + sign. **The AI accelerates the first read — never restricts the radiologist's judgment.**

## 19. FINAL OUTPUT EXAMPLE
Study completeness (742 images / 9 series, all processed) · technical quality (diagnostic, mild respiratory motion) · primary diagnosis (acute segmental PE right lower lobe) · supporting findings (intraluminal filling defects, wedge opacity, small effusion) · ranked differential (1 PE with small infarction, 2 flow artifact, 3 peripheral pneumonia) · must-not-miss (right-heart strain) · CDS (correlate hemodynamics/biomarkers, echo if indicated, immediate review) · preliminary impression · **STATUS: AI-generated preliminary interpretation. Radiologist review and signature required.**

## 20. NON-NEGOTIABLE PRODUCT RULES
Every image processed or explicitly failed · every study completeness-checked · every abnormal study gets a primary where supported · every reasonable alternative ranked · every dangerous alternative in must-not-miss · every conclusion links to supporting images · every recommendation subject to radiologist approval · every final report reviewed + signed by a radiologist · every correction captured for governed training · learn from confirmed outcomes — NOT images alone · no live-model self-retraining without validation/release control · no likely-normal study bypasses radiologist review · no incomplete study presented as fully analyzed · no confidence score as diagnostic certainty · no AI report as final before signature.

## 21. FINAL PRODUCT DEFINITION
**NURA Rad = an AI-assisted diagnostic radiology platform that reads every image in a complete study, identifies and localizes normal + abnormal findings, proposes a primary diagnosis, generates a ranked differential, identifies must-not-miss conditions, provides clinical decision support, and drafts a preliminary radiology report — learned from images LINKED to expert reports, annotations, confirmed diagnoses, pathology, procedures, follow-up imaging, and outcomes — every study presented to a licensed radiologist for review, correction, approval, and final signature.**

**The shorthand: Every image read. Every finding localized. One primary diagnosis. A ranked differential. Clinical decision support. Radiologist final approval.**
