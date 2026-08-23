# 05 — MEDIA ENGINE (nura-media)

Autonomous, local-first media production controlled by Hermes. Replaceable providers, no hard deps.

## Pipeline (the contract the orchestrator must satisfy)
`script → (image/video/avatar/voice providers) → edit/render (FFmpeg/OpenCut) → QA (ffprobe/typed)`
`→ generation ledger → store (B2) → approval → publish`.

## MVP (verified `MEDIA-MVP-PASS` 2026-08-23)
`apps/orchestrator.py` proves the chain on CPU, zero cost: script (model_gateway, provider-review
flagged) → render (FFmpeg 1280x720, caption card) → QA (duration 2.0s, has_video, render_ok) →
generation_ledger (asset_id, output_sha256) → store (B2 dry-run). Run:
`python3 /opt/data/nura-media/apps/orchestrator.py`.

## Provider router (local-first, commercial fallback — NEVER a hard dependency)
- Avatar: heygem / musetalk → fallback heygen · Video: wan / ltx / hunyuan → fallback higgsfield
- Editor: opencut / ffmpeg → fallback capcut · Image: flux → fallback
- Cost order: existing local compute → ephemeral GPU worker → free API quota → paid → human.
- Score = quality - cost - latency + reliability + local_preference. Failed provider → retry →
  change params → change model → change provider → degrade → human exception queue.

## Storage / ledger (the durable record — `infrastructure/media_schema.sql`)
- `generation_ledger` (asset_id, job_id, provider, model, prompt, seed, input/output_hash,
  generation_time, cost, license, storage_uri, status) — reproducible.
- `media_model_registry` (license, commercial_use, VRAM, quality/speed/cost/reliability, enabled) —
  no model auto-published without benchmark + license review.
- `media_job` (queue, priority, status, attempt, error) — dispatch via Celery+Redis; durable in Postgres.
- `authorized_identity_registry` — **no voice/face/avatar cloning without documented authorization.**

## Gate for medical content
`research → script → evidence validation → generate → technical QA → clinical QA → human clinical`
`approval → publish`. Hermes may autonomously prepare; **may not bypass the approval gate.**
No PHI in media prompts. Commercial services used only for premium/quality gaps (not commodity B-roll).
