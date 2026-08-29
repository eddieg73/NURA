# Orthanc + ThaiRIS + Vision Wet-Read Plan (founder 2026-08-02)

## Architecture (verified intent)
DICOM sources (CT/MRI/XR/US) → Orthanc (C-STORE + DICOMweb) → ThaiRIS bridge (bilingual TH/EN worklist) + HL7/Lab gate (Mirth) → Vision Wet-Read gate (Med-Flamingo/LLaVA-Med class) → Agent feed → **Clinician review gate** → draft report.

## Orthanc config (patch applied to imaging-stack/modules/orthanc/orthanc.json)
- DICOMweb plugin: Enable true, WADO-RS, StudiesMetadata Full
- HttpWebhooks → n8n `/webhook/orthanc-new-instance` (order/worklist events)
- OnStoredInstance Python hook → POST to wet-read gateway for DX/CR/CT/MR/US

## Wet-Read pipeline (built: scripts/wet-read-gateway.py)
- POST /v1/wet-read {instance_id, modality, dicom_web_uri, patient_id} → fetch DICOM (DICOMweb when Orthanc live; dry-run now) → pydicom → windowing (soft tissue/bone/lung for CT) → vision cascade (vision-proxy free-vl→gemini) → structured impression {finding, normal/abnormal, confidence, STAT flags} → draft-only + provider review
- Zero-shot triaging + STAT alerting (pneumothorax/ICH/fracture classes flagged, never final)

## Training datasets (open-access directory — access gates flagged)
- **X-Ray**: MIMIC-CXR-JPG (~377K imgs; **CITI/PhysioNet credentialed — PENDING**) · CheXpert (224K; **license — PENDING**)
- **CT**: RSNA Abdominal Trauma (Kaggle; **kaggle.json PENDING**) · CQ500 head CT (Qure.ai; 491 studies)
- **MRI**: fastMRI NYU (10K+) · **IDC** (multi-modal, DICOMweb, multi-TB — **open, deploy on Lab 1030183**)
- **US**: BUSI breast (780 imgs) · **DICOM tests**: Saga/OsiriX samples (30 studies)
- **Labs/EHR**: MIMIC-IV v3 (383K pts; **CITI PENDING**) · MIMIC-IV-Ext multimodal (paired labs+imaging+notes) · eICU (200K admissions)

## Training strategy (matches Aesthetics pipeline: Bio_ClinicalBERT Azure ML, ONNX)
Vision: Swin/ViT fine-tune on MIMIC-CXR + RSNA (Lab node) · Cross-modal: MIMIC-IV LABEVENTS paired with imaging (abnormal labs ↔ studies) · Thai: parallel EN↔TH radiology impressions corpus (ThaiRIS localization) · Fusion: LLaVA-Med/Med-Flamingo class · Compute: Lab 1030183 (32GB; RunPod serverless if GPU needed)

## Gates/sequence
NUR-100 → CTO: patch applied (Orthanc config) · wet-read gateway built (dry-run) · ThaiRIS bilingual fields → NUR-75 · dataset drops (CITI/kaggle/CheXpert) + IDC on Lab · full pipeline after NUR-68.
