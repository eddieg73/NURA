# NURA / HERMES — MEDICAL DATA, API, CLI, MCP & DATASET CATALOG (2026-08-04, founder canonical v1.0)

**A governed registry of free/open/registration/research medical data sources for CDS, laboratory intelligence, radiology, emergency medicine, model evaluation, and knowledge retrieval. The registry must be maintained continuously — endpoints, licenses, versions, and terms change.**

## 1. NON-NEGOTIABLE GOVERNANCE RULES
1) Research datasets ≠ point-of-care clinical authorities. 2) No ingestion until license/DUA/commercial terms/provenance/intended use/population/limitations/update cadence are recorded. 3) No PHI to any API/CLI/MCP/model/dataset without a signed agreement + approved security architecture. 4) Community MCP servers = untrusted code until source review, dependency/secret scanning, sandbox testing, and legal review. 5) Use LOCAL laboratory reference intervals/units/specimen/assay/age/sex/pregnancy/collection time before interpreting labs. 6) Adverse-event databases = signal detection only, never causation/incidence/autonomous treatment. 7) Human review required for diagnosis, prescribing, ordering, final radiology interpretation, disposition, regulated actions. 8) Record source/model/prompt version + retrieval timestamp + citation for every clinical output.

## 2. STATUS LABELS
FREE-OPEN · FREE-KEY (free key/registration) · FREE-DUA (training/credentialing/DUA required) · ELIGIBILITY (qualifying orgs) · LICENSED · RESEARCH-ONLY · COMMUNITY (full review required) · PRODUCTION-CANDIDATE (validated + governed + contractual).

## 3. CORE BIOMEDICAL KNOWLEDGE APIs
**FREE-OPEN:** PubMed/NCBI E-utilities (build the PubMed MCP with query sanitization + citations + caching) · PubMed Central Open Access (article licenses vary — preserve each) · NCBI Bookshelf (secondary reference, not current guidance) · ClinicalTrials.gov API v2 (REST/OpenAPI/JSON/CSV/FHIR — research context, not efficacy proof) · MedlinePlus Connect (patient education mapped from ICD/SNOMED/LOINC/RxNorm) · NIH RePORTER (grant mapping) · Europe PMC (complement) · Crossref (DOI/citations — not medical authority) · OpenAlex (research mapping). **FREE-KEY:** Semantic Scholar (discovery only).

## 4. DRUG / MEDICATION / LABELING / SAFETY
**FREE-OPEN:** RxNorm API (normalization) · Prescribable RxNorm · RxClass · RxTerms · RxNav-in-a-Box (LOCAL install — offline/privacy!) · DailyMed (SPL labeling — warnings/dosage/contraindications) · FDA Drug Shortages · UNII/GSRS · MED-RT (NLM terms) · ChEMBL (research, not prescribing) · PubChem (toxicology + chemical intelligence). **FREE-KEY/limited:** openFDA Drug Label · Drugs@FDA · NDC Directory · FAERS (SIGNAL DETECTION ONLY — never causality/incidence) · FDA Recalls/Enforcement. **Mixed:** DrugBank Open portions (commercial API generally licensed) — do NOT classify full DrugBank as free.

## 5. TERMINOLOGY / CODING / INTEROP
LOINC (FREE with terms) · SNOMED CT US (free in eligible jurisdictions, license applies) · UMLS Metathesaurus (FREE-DUA/license) · ICD-10-CM/PCS (FREE-OPEN) · WHO ICD-11 API (FREE-KEY/terms) · UCUM · HL7 FHIR R4/R5 · US Core IG · SMART on FHIR · CDS Hooks · CQL · FHIRPath · HAPI FHIR · Firely .NET SDK · SUSHI/FSH · Inferno (conformance testing).

## 6. PUBLIC HEALTH / EPIDEMIOLOGY / SURVEILLANCE
CDC data.cdc.gov (Socrata API) · CDC WONDER (query restrictions) · FluView · NNDSS (aggregate) · Environmental Public Health Tracking · PLACES · data.gov · WHO GHO · WHO Disease Outbreak News (feeds) · Our World in Data (attribution; verify against primary stewards) · HealthData.gov/HHS.

## 7. LABORATORY DATA
**Terminology/infrastructure:** LOINC · UCUM · UMLS · FHIR Observation/DiagnosticReport/Specimen · HL7 v2 ORU/OML/ORM (Mirth/HAPI) · LIVD (IVD→LOINC maps) · SHIELD/FDA lab-interop resources.
**Datasets:** MIMIC-IV (FREE-DUA — research, artifacts possible) · MIMIC-IV-ED · eICU · AmsterdamUMCdb · HiRID · PhysioNet waveforms · NHANES (population, not patient ranges) · UK Biobank (PAID — not free) · All of Us (controlled) · Synthea (synthetic — testing only) · SMART Health IT synthetic.
**The Laboratory Knowledge Gateway (build this):** LOINC normalization · UCUM validation/conversion · assay/lab-specific reference ranges · age/sex/pregnancy/specimen/method-aware interpretation · delta checking · critical-value rules · hemolysis/lipemia/icterus flags · duplicate/impossible-value detection · temporal trending · med+diagnosis context · closed-loop critical-result notification · human review. **No public API replaces the performing laboratory's validated reference interval or critical-value policy.**

## 8. RADIOLOGY & IMAGING
**Datasets:** TCIA (CT/MR/PET/pathology/radiomics; collection licenses vary) · ChestX-ray14 (weak labels — benchmark only) · MIMIC-CXR (FREE-DUA) · CheXpert (registration) · PadChest · RSNA/SIIM challenges · VinDr-CXR/Mammo · CBIS-DDSM · LIDC-IDRI (lung CT nodules) · BraTS · Decathlon · KiTS · fastMRI · OASIS · ADNI (approved research — not free) · OpenNeuro (per-dataset licenses) · MIDRC · NLM Open-i · Grand Challenge (never assume commercial rights).
**Tools/APIs:** TCIA REST APIs · NBIA Data Retriever · tcia_utils · DICOMweb (QIDO/WADO/STOW) · Orthanc REST · DCMTK · dcm4che · GDCM · pydicom · highdicom (SR/SEG) · OHIF · MONAI/MONAI Label · 3D Slicer · nnU-Net · TotalSegmentator (license conditions) · SimpleITK/ITK · ANTs · FSL · FreeSurfer · OsiriX Lite (proprietary) · Weasis.
**Production safety:** AI = preliminary/prioritization/quantification/segmentation/CDS only unless cleared · preserve original DICOM + metadata · store AI results as SR/SEG/secondary capture · record model/weights/preprocessing/threshold/series/timestamp · radiologist final approval · track FN/FP/discrepancy/subgroup/drift · separate research vs production-cleared models.

## 9. PHYSIOLOGY / ECG / WAVEFORM
PhysioNet (mixed) · MIT-BIH Arrhythmia · PTB-XL (12-lead) · MIMIC-IV Waveform (FREE-DUA) · Sleep-EDF · WFDB (CLI) · NeuroKit2 · BioSPPy · pyEDFlib/MNE-Python.

## 10. GENOMICS / PRECISION MEDICINE
ClinVar · dbSNP · Gene · GEO · SRA · GTR · gnomAD (public research) · CIViC · cBioPortal · GDC (controlled+open) · PharmGKB (mixed licensing) · CPIC guidelines (public; implementation needs validated genotype workflow).

## 11. PATHOLOGY / CANCER
TCGA/GDC (open+controlled) · Cancer Digital Slide Archive · CAMELYON · PANDA · CPTAC · Human Protein Atlas (terms) · QuPath · OpenSlide.

## 12. CLAIMS / QUALITY / PROVIDER / HEALTH-SYSTEM
CMS Data API · CMS Provider Data Catalog · Care Compare · **CMS Blue Button 2.0 (ELIGIBILITY + beneficiary auth — OAuth2/FHIR)** · BCDA (FHIR Bulk, ACO) · AB2D (Part D) · CMS Marketplace API (FREE-KEY) · NPPES NPI Registry · PECOS public · AHRQ HCUP (OFTEN PAID — don't classify free) · AHRQ QI software (free components).

## 13. SDOH / GEOGRAPHY / ENVIRONMENT
US Census API (FREE-KEY) · ACS API · CDC Social Vulnerability Index · AHRQ SDOH Database · USDA Food Access · EPA AirNow (FREE-KEY) · EnviroAtlas/EJScreen · NOAA (FREE-KEY/open) · FEMA OpenFEMA · HIFLD Open.

## 14. EMERGENCY MEDICINE (mandatory packaged skill for EVERY clinician tenant — non-removable)
Sources: local EMS/hospital/state protocols · CDC preparedness · FEMA incident management · HHS ASPR · CHEMM · REMM · Poison Control (approved access) · FDA/DailyMed/RxNorm · PubMed · ClinicalTrials.gov (context) · WHO emergency guidance · PhysioNet/MIMIC-IV-ED (research) · national trauma datasets (under agreements). **Mandatory output structure:** the Emergency Safety Review (stability-first template).

## 15. OPEN-SOURCE CDS ENGINES & RULE TOOLS
OpenCDS · CDS Hooks reference impls · CQL Engine/cqf-ruler · HAPI FHIR Clinical Reasoning · Drools (deterministic rules) · **OPA = authorization/policy, NOT clinical reasoning** · Camunda community (inspect licensing) · Temporal (durable workflows) · Node-RED (harden before production) · n8n community (review license + PHI controls) · NextGen/Mirth Connect (open core).

## 16. CLI & DEVELOPER TOOLING
General: curl · httpie · wget · jq · yq · csvkit · xsv · duckdb · sqlite3 · psql · rclone · aria2c · git/git-lfs · dvc · lakeFS · mc. NCBI: EDirect (esearch/efetch/elink/xtract) · NCBI Datasets CLI · SRA Toolkit · Biopython. Imaging: DCMTK (dcmsend/storescu/findscu/movescu/dcmdump) · dcm4che · GDCM · Orthanc REST · NBIA Retriever · tcia_utils · 3D Slicer headless · MONAI bundles · nnU-Net · ANTs · FSL · FreeSurfer. FHIR/HL7: SUSHI · FHIR Shorthand · HL7 validator CLI · HAPI · Inferno · Postman/Newman · NextGen CLI. Physiology: WFDB · MNE · EDF tools · NeuroKit2.

## 17. MCP SERVER STRATEGY (NURA builds + governs its OWN layer — no authoritative public catalog exists)
**The 30 required NURA MCP servers:** nura-pubmed · nura-pmc · nura-clinicaltrials · nura-rxnorm · nura-dailymed · nura-openfda · nura-cdc · nura-who · nura-cms-data · nura-nppes · nura-loinc · nura-terminology · nura-fhir · nura-hl7 · nura-laboratory · nura-critical-results · nura-orthanc · nura-dicomweb · nura-tcia · nura-ohif-context · nura-physionet · nura-mimic-research · nura-genomics · nura-public-health · nura-emergency-medicine · nura-poison-toxicology · nura-device-safety · nura-guideline-registry · nura-citation-verification · nura-dataset-governance.
**Standard tool contract per MCP:** name · version · steward · source_url · authentication · license · dua_required · commercial_use · phi_allowed · intended_use · prohibited_use · rate_limit · cache_policy · update_frequency · last_verified · clinical_risk_tier · required_human_review.
**Mandatory controls:** outbound-only where feasible · tenant-scoped creds · secret vault · allowlisted domains/methods · query sanitization · PHI detection/blocking · rate limits/quota · schema validation · citation+provenance capture · immutable audit · timeouts/retries/circuit breakers/DLQ · tool-level kill switch · no arbitrary shell/URL fetching · no implicit writes.

## 18. THE BUILD ORDER
**Tier 1 (build first):** PubMed · ClinicalTrials.gov · RxNorm · DailyMed · openFDA · LOINC/UCUM terminology service · FHIR · Laboratory (local reference ranges) · Orthanc/DICOMweb · TCIA (research) · Emergency Medicine skill · Citation+provenance service · Dataset governance registry. **Tier 2:** CDC/public-health · CMS/NPPES · PhysioNet connector · MIMIC research env · genomics · SDOH/geospatial · device safety/recall · guideline registry. **Tier 3 (controlled research):** imaging training pipelines · pathology · multimodal EHR-imaging linkage · federated learning · synthetic generation · bias/drift evaluation · robot/austere offline packages.

## 19. SOURCE VERIFICATION CHECKLIST (before enabling ANY source)
Official steward · active endpoint · current version · ToS reviewed · license recorded · DUA if required · commercial-use status · PHI policy · data residency · update cadence · limitations documented · research-vs-clinical classified · security review · clinical governance approval · test queries validated · failure/fallback tested · citation format implemented · kill switch tested.

## 20. AUTHORITATIVE STARTING REFERENCES
NCBI/NLM APIs · ClinicalTrials.gov API · RxNorm/RxNav · DailyMed Web Services · openFDA · CMS Developer Tools · CDC Open Data · WHO ICD + GHO · PhysioNet/MIMIC · TCIA · HL7 FHIR/SMART/CDS Hooks · LOINC/UCUM/SNOMED/UMLS under terms.

## 21. THE FINAL DIRECTIVE
**Hermes shall NOT "learn medicine" by indiscriminately scraping the Internet.** It learns through a GOVERNED KNOWLEDGE + DATASET GATEWAY that: 1) prioritizes authoritative/primary sources · 2) separates clinical authority from research evidence · 3) preserves provenance + licensing · 4) validates terminology/units/identity/context · 5) prevents PHI leakage · 6) requires human clinical review · 7) continuously evaluates accuracy/bias/drift/safety · 8) makes the Emergency Medicine skill available to every clinician regardless of specialty.

## THE NURA MAP (what's already live vs the build)
- **LIVE:** openFDA · PubMed (via the evidence lanes) · BioPortal · CDC · ClinicalTrials.gov lanes · Orthanc/Mirth/OHIF · the lab-review skill (the Laboratory Gateway's doctrine already encoded!) · the emergency-medicine skills.
- **TIER 1 BUILD QUEUE (next):** the governed MCP layer — PubMed/ClinicalTrials/RxNorm/DailyMed/openFDA/LOINC/FHIR/Lab/Orthanc/TCIA + the citation service + the dataset governance registry — the catalog is the map, the MCP layer is the machine, boss.
