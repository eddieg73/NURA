# NURA Medical Model Registry (swept 2026-08-16 — GitHub + HF + NVIDIA)

## GatorTron (UF Health × NVIDIA)
- **GitHub (official)**: `uf-hobi-informatics-lab/GatorTron` (the training scripts — trained on NVIDIA's Selene via Megatron-LM) · `GatorTronGPT` (the 20B clinical GPT) · `GatorTron-Prediction` (cancer→HF risk study, pushed 2025-11 — the ACTIVE repo)
- **HF**: `UFNLP/gatortron-base` (345M) + community fine-tunes (AnnieEl mental-health series, the breast-cancer fine-tunes)
- **NVIDIA NGC**: the catalog hosts the full GatorTron family (application-gated — the licensing lane)
- **Gate**: the base weights need the UF/NVIDIA license request; the scripts + papers = open

## ClinicalBERT / BioBERT (the encoder class)
- **`emilyalsentzer/Bio_ClinicalBERT`** — THE canonical clinical BERT (Bio + MIMIC clinical notes) — open ✓
- **BioBERT** (dmis-lab) + the ICD-10 fine-tunes (Emran) + the seizure-classification fine-tune (UPenn)
- **Clinical word embeddings** (garyw — 100/300/600d, the classic w2v clinical vectors)

## The LLM family (generative)
| Model | Where | Status |
|---|---|---|
| **Med42-8B** | HF m42-health + our Ollama | ✅ SERVING (DocsGPT + dx) |
| **MEDITRON-7B** | HF epfl + our Ollama | ✅ SERVING |
| **BioMistral-7B** | HF + our Ollama | ✅ SERVING |
| **Medalpaca 7B/13B/30B** | HF medalpaca/* | 📥 available (the fine-tune candidates) |
| **PMC-LLaMA · BioMedLM · OpenBioLLM · Asclepius** | HF | 📥 available |
| **GatorTronGPT-20B** | gated | 🔒 license lane |

## The embeddings + vision (the retrieval/perception class)
- **Clinical sentence-transformers** (the RAG embedding upgrades for DocsGPT)
- **PubMedBERT · BlueBERT · BioLinkBERT** — the PubMed-domain encoders
- **BiomedCLIP · MedCLIP · Quilt-1M · PMC-VQA** — the medical vision-language lane (the radiology vision upgrade)

## The verdict
- **GatorTron = the heavyweight we CAN'T run local yet** (20B GPT + the gated NGC weights) — the license application = the founder's 5-minute form when the GPU node exists
- **ClinicalBERT/BioBERT = open + small — PULL NOW**: the ICD coding lane (Emran's fine-tunes) + the clinical NLP lane run on the Lab CPU today
- **The generative trio = already ours** (Med42/Meditron/BioMistral serving)
- **Medalpaca family = the next pulls** when the fine-tune graduates
