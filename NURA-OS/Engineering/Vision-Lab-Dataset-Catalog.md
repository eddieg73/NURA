# NURA Vision & Lab Dataset Catalog (surveyed 2026-08-16)

Mapped to the NURA ML stack. All sources open/credentialed (PhysioNet credentialed access for MIMIC — free registration).

## The learning datasets (added 2026-08-16 — what each teaches the machine)
| Domain | Datasets | Teaches |
|---|---|---|
| **Clinical reasoning** | **MedQA (USMLE-style) · MedMCQA · PubMedQA** | Diagnostic Q&A benchmarks — the eval set for the fine-tune |
| **Instruction/training** | **MedAlpaca · UltraMedical · ChatDoctor** | The fine-tuning corpora (already the Kaggle notebook's data source) |
| **ECG/waveforms** | **PTB-XL (21K ECGs) · MIT-BIH arrhythmia · MIMIC-IV-Waveform** | The cardiac lane — local ECG classifiers |
| **Derm** | **HAM10000 · ISIC archive** | The lesion classifier training set (beyond the vision lane) |
| **Ophthalmology** | **EyePACS · APTOS (diabetic retinopathy)** | DR screening — the RPM-adjacent opportunity |
| **Pathology** | **Camelyon16/17 · TCGA slides** | Slide AI (the future lab lane) |
| **Report↔image pairs** | **OpenI · IU X-Ray** | Report-generation (the radiology NLP + vision fusion) |
| **Genomics/labs** | **gnomAD · ClinVar · PharmGKB · TCGA** | The lab/genomics knowledge lane |
| **PhysioNet suite** | eICU · Sleep-EDF · the MIMIC family | ICU + sleep + waveform research |
| **Gated-but-free** | UK Biobank · N3C (applications) | Population-scale (the long-term lane) |

## The 6-modality map (founder directive 2026-08-16: CT · PET-CT · MRI · US · MAMMO · NUCLEAR MED)
| Modality | Top datasets | Size / notes |
|---|---|---|
| **CT** | LIDC-IDRI (lung nodules) · DeepLesion (32K lesions) · RSNA PE · MosMed (COVID) · TotalSegmentator sets | Nodule detection + whole-body organ segmentation |
| **PET-CT** | **AutoPET FDG** (1,014 whole-body studies, manual lesion masks, TCIA/fdat, nnU-Net format) · **AutoPET PSMA** (597 studies) · DeepPSMA | World-standard lesion-segmentation corpus — SUV-normalized PET + aligned CT |
| **MRI** | BraTS (brain tumor + masks) · fastMRI (raw k-space) · IXI · ADNI/OASIS (Alzheimer) | Segmentation + reconstruction research |
| **US** | BUSI/BUID (breast) · TN3K/DDTI (thyroid) · EchoNet (cardiac video) · FETAL_PLANES | Breast/thyroid = the founder's lanes; cardiac + OB covered |
| **MAMMO** | **CBIS-DDSM** (1,566 patients, 10,239 DICOM, 163GB, CC BY 3.0, mass+calc ROIs) · INbreast · VinDr-Mammo · BCDR · CSAW (~500K, Karolinska) · EMBED (Emory) | The screening corpus — matches the Dimensions unit's domain |
| **NUCLEAR MED** | **PPMI** (Parkinson's Progression Markers Initiative — DaTscan SPECT, 1000s of subjects, longitudinal) · the AutoPET family covers PET-NM · myocardial perfusion SPECT (limited open) | SPECT/general-NM open data is the scarcest modality — PPMI is the flagship; PET = AutoPET |

## VISION (radiology AI — feeds the PACS annotation module + TorchServe segmentation)
| Dataset | Size | Best for |
|---|---|---|
| **UMIE** (HF: lion-ai/umie_datasets) | 1M+ images, 20+ datasets unified, RadLex ontology | The STARTING POINT — pretraining/foundation work, classification + segmentation, one clean format |
| **MIMIC-CXR** (PhysioNet) | 377K chest X-rays, DICOM + 227K reports | Report generation, NLP+vision fusion — the flagship |
| **CheXmask** | 657K anatomical segmentation masks over 5 CXR sets (ChestX-ray8, CheXpert, MIMIC-CXR, PadChest, VinDr) | Lung/heart segmentation, cardiothoracic ratio, auto-contouring |
| **CheXpert** | 224K (Stanford) | Disease classification benchmarks |
| **ChestX-ray14** | 112K (NIH) | Weakly-supervised detection |
| **BraTS** | Brain tumor MRI + masks | MR segmentation (future neuro) |
| **MSD (Medical Segmentation Decathlon)** | 10 organs/tasks | Cross-anatomy segmentation models |
| **TCIA** | The Cancer Imaging Archive — CT/MR hub (DeepLesion, LIDC, hundreds) | CT lung/lesion work, the DEXA/mammo-domain studies |
| **ISIC** | Skin lesion dermoscopy | Dermatology/aesthetics lane |

## LAB (lab intelligence — feeds CORA, coding-agent, lab-trend analytics)
| Dataset | Content | Best for |
|---|---|---|
| **MIMIC-IV (Hosp module)** | Hospital-wide labs, micro, meds, diagnoses | The flagship lab dataset — trends, panels, abnormality detection |
| **Symile-MIMIC** | 11,622 admissions: CXR + ECG + 50 common blood labs, multimodal | **The fusion goldmine** — labs+ECG predicting imaging; the lab-intelligence model |
| **NHANES (CDC)** | National lab measures + surveys | Population reference ranges; the CDC MCP lane already queries this (diabetes, hypertension, obesity datasets live) |
| **eICU** | 200K ICU admissions with labs | Critical-care lab dynamics, deterioration models |

## NURA wiring (where each feeds)
- **Coding-agent / RAF**: MIMIC-IV diagnoses+labs → condition extraction benchmarks
- **Radiology AI (blueprint §5)**: UMIE + CheXmask for the PACS annotation sidecar (TorchServe)
- **Lab intelligence**: MIMIC-IV + Symile → the hermes-laboratory-intelligence lane
- **CDC MCP**: live government data without downloads (mcp__cdc__cdc_query)
- **Access notes**: MIMIC = credentialed PhysioNet (free, needs the data-use agreement — a founder click when we start training); UMIE/CheXmask = HF, immediate; CDC = keyless live
