# NURA Clinical Model — the free training lane (2026-08-16)

**Goal:** a NURA clinical model, fine-tuned on free GPUs, serving LOCAL on the Lab Ollama. Zero OpenRouter credits, forever.

## The pipeline
```
1. make-training-data.py  → nura-training-data.jsonl (seed 7 pairs, extend with verified Q&A)
2. train-nura-clinical.py → run on Kaggle (30h/wk free T4) or Colab (free T4):
     unsloth QLoRA (r=16) on m42-health/Llama3-Med42-8B, 4-bit, max_steps 200
     → exports nura-clinical-v1-unsloth.Q4_K_M.gguf
3. Import (inference stays LOCAL):
     scp the GGUF to the Lab → /opt/med-weights/
     printf 'FROM ./nura-clinical-v1-unsloth.Q4_K_M.gguf\nSYSTEM "You are NURA...decision-support..."\n' > Modelfile-nura
     ollama create nura-clinical-v1 -f Modelfile-nura
     → the model serves on the Lab (the same lane as med42/meditron/biomistral)
```

## The rules
- PHI never enters training data (de-identified Q&A only)
- The system prompt bakes in: decision-support only, provider review, no autonomous diagnosis
- Every generated answer in production = the provider-gated doctrine (same as today)
- Evals before promotion: the new model must beat med42 on the clinical Q&A set before it replaces it (eval-bench cron)

## The free compute map
- Kaggle: 30h/week T4/P100 free · Colab: free T4 · Modal: $30/mo free · HF Spaces: free CPU evals
- The Lab: 32GB CPU — inference only (no training on the prod node)

## What's free about it (the accounting)
- Model weights: open (M42 Health license) · framework: unsloth (Apache-2.0) · data: our seed + open medical sets (UltraMedical/MedAlpaca, HF) · compute: free GPU tiers · inference: the Lab, $0
- The ONLY cost = the founder's 5 minutes on Kaggle (free account) to hit Run
