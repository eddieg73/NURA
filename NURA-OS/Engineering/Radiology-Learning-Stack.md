# Radiology Learning Stack — free MCP / CLI / API + datasets (2026-08-17)

Everything below is free/open — the complete image-reading curriculum for the NURA radiology lane.

## The MCP servers (found, ready to wire)
| Repo | What it does |
|---|---|
| **`NahButch/dicom-mcp`** | Read-only Rust MCP: explore CT/MR/X-ray DICOMs — list studies, view images, PDF for the doc. Anonymized, not a diagnostic device |
| **`LeviReisJs/mcp-openi-server`** | MCP + CLI + Claude-Code plugin: search the **Open-i** (NLM) medical/radiology image corpus — **no API key** |

## The CLIs / frameworks (the training + inference engines)
| Repo | Stars | What it does |
|---|---|---|
| **`Project-MONAI/MONAI`** | 8,600★ | THE healthcare imaging toolkit — the framework + MONAI Label + the Model Zoo (pre-trained) |
| **`MIC-DKFZ/nnUNet`** | 8,789★ | The self-configuring segmentation framework — the world-standard U-Net pipeline |
| **`wasserth/TotalSegmentator`** | 2,936★ | Segment 100+ anatomical structures from CT/MR — the CLI for whole-body reads |
| **`mlmed/torchxrayvision`** | 1,183★ | The chest X-ray library — datasets + pre-trained classifiers (14 pathologies) |
| **`Stanford-AIMI/CheXagent`** | 232★ | The CXR foundation model (vision-language) — generate reports + answer image questions |

## The free APIs
- **Open-i (NLM)** — the keyless image corpus search (the MCP above rides it)
- **NCI Imaging Data Commons (IDC)** — the free public imaging repository API (the TCIA datasets programmatically)
- **TCIA REST** — The Cancer Imaging Archive's API — the download lane for the 6-modality datasets

## The training datasets (beyond the 6-modality map in Vision-Lab-Dataset-Catalog.md)
| Dataset | Modality | Size |
|---|---|---|
| **VinDr-CXR / SpineXR / RibCXR / Mammo** (Vietnam) | CXR + MSK + mammo | 100K+ studies, expert annotations |
| **CheXpert** (Stanford) | CXR | 224K films, 14 labels |
| **NIH CXR8** | CXR | 112K films |
| **MURA** (Stanford) | MSK radiographs | 40K studies |
| **PadChest** | CXR | 160K films, Spanish reports |
| **RSNA challenge sets** (pneumonia, PE, cervical spine) | CXR/CT/MSK | the annual gold standards |
| **AbdomenAtlas / AMOS** | CT | 9K+ annotated abdomen CTs |

## The integration plan
1. Wire the **mcp-openi-server** → the dsh/harness lanes (keyless image retrieval)
2. Install **TotalSegmentator + TorchXRayVision** on the Lab (CPU-runnable inference!)
3. MONAI + the **Med42 fine-tune** → the NURA radiology model (the Kaggle lane)
4. The datasets → the training pipeline (the WALDO receipts on every corpus)
