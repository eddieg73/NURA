# NURA Radiology AI Engine — the canonical spec (the founder's reference, 2026-08-19)
The IBM Watson Health-style architecture's the adapted to the Hostinger VPS + the B2 + the Hermes. The reference.

## 1. The high-level flow
The DICOM → the FastAPI Gateway + the Celery Worker → (1) the raw .dcm → the B2, (2) the pydicom's the metadata, (3) the preprocess (the windowing, the HU, the resampling), (4) the vision engine (the ONNX/PyTorch — the lesion/fracture/nodule), (5) the NLP engine (the RadLex + the SNOMED-CT) → the Multi-Modal Fusion → the Hermes Telegram (the formatted summary + the B2 pre-signed image link).

## 2. The storage schema (the B2)
- the b2://med-radiology-raw/{patient_id}/{study_uid}/{series_uid}/{sop_uid}.dcm
- the b2://med-radiology-processed/{study_uid}/thumbnail.png + inference_map.json
- The DICOM metadata's the JSON: the study/series UIDs, the patient (the id/age/sex), the acquisition (the modality, the body_part, the dims, the slice thickness, the pixel spacing, the rescale, the window), the storage_path.

## 3. The preprocessing's the math
The HU = (Pixel × RescaleSlope) + RescaleIntercept · the windowing's the bounds = WCenter ± WWidth/2 · the resample's the 1.0mm isotropic.

## 4. The vision's the dual-engine
- The 2D (the X-ray/mammo): the DenseNet121/ResNet50 (the multi-label's the pneumothorax/effusion/consolidation/cardiomegaly).
- The 3D (the CT/MRI): the 3D-UNet/Swin UNETR (the segmentation's the + the volumetric's the lesion's the detection).
- The output's the JSON: the findings[] (the label, the confidence, the location's the bounding box, the volume, the urgency).

## 5. The NLP's the schema
The section segmentation (the INDICATION/FINDINGS/IMPRESSION) + the negation detection ("No evidence of pneumothorax" → the Pneumothorax: False) + the entities (the term, the CUI, the RadLex ID, the status, the certainty, the location).

## 6. The Hermes Telegram's the payload
The {chat_id, command: ANALYZE_STUDY, context: {patient, modality, raw_image_url (the B2 pre-signed), vision_ai_summary, matched_guidelines (the Fleischner), instructions}} → the concise radiologist summary.

## 7. The VPS stack
The FastAPI/Python 3.11 · the Celery+Redis (the queue) · the pydicom+SimpleITK · the ONNX Runtime · the boto3 (the B2) · the python-telegram-bot/the webhook.

## 8. The dataset catalog (the training's the ammunition)
| Set | Modality | Volume | Our state |
|---|---|---|---|
| MIMIC-CXR | DICOM CXR | 377K | ⏳ (the credentialed) |
| NIH ChestXray14 | CXR | 112K | ✓ (the chxr14's the gated — the swap) |
| CheXpert | CXR | 224K | ⏳ |
| PadChest | CXR | 160K | ⏳ |
| VinDr-CXR | CXR | 18K | ✓ (the mammo's the VinDr's the grabbed) |
| LIDC-IDRI | CT | 1,018 | ⏳ |
| LUNA16 | CT | 888 | ⏳ |
| RSNA-ICH | Head CT | 25K | ⏳ |
| CQ500 | Head CT | 491 | ⏳ |
| BraTS | MRI | 2,000 | ⏳ |
| DeepLesion | CT | 32,735 | ⏳ |
| MURA | X-ray | 40,561 | ⏳ |
| LiTS | CT | 130 | ⏳ |
| CBIS-DDSM | Mammo | 1,566 | ✓ (the grabbed!) |
| INbreast | Mammo | 115 | ⏳ |
| The ontologies: the RadLex · the SNOMED-CT · the UMLS | | | ⏳ (the the RadLex's the open — the grab) |

## 9. The ours vs the spec (the gap-map)
| Spec | NURA's the |
|---|---|
| The FastAPI gateway | ✓ (the tools API + the mso-coder) |
| The Celery queue | ⏳ (the the n8n's the workflows — the the Celery's the the add) |
| The pydicom | ✓ (the installed) |
| The B2 | ✓ (the 6 buckets) |
| The vision engine | ⏳ (the TorchXRayVision's the on the Lab — the the wire's the the ONNX's the loop) |
| The NLP's the RadLex | ⏳ (the the RadLex's the open's the grab) |
| The Telegram's the interface | ✓ (the the Hermes's the native) |
| The datasets | the ~2/15 ✓ (the CBIS-DDSM + the VinDr's the mammo + the CXR's the pneumonia/COVID) |

The reference only.
