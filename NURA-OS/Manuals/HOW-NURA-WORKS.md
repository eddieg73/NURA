# HOW NURA WORKS — The Complete System Explained (2026-08-02)
Audience: operators, investors, and the board. Plain English. One system, one story.

## The one-sentence story
NURA is ONE master app that serves providers by talking to ALL their systems (EMRs, labs, imaging, phones, billing) — so a clinician runs their entire practice from a single voice-first screen, and the AI does the administrative work.

## The layers (how everything fits)
1. **THE APP (one master app)** — voice-first clinician app: AI Assistant · Clinical Dialer · AI Scribe · eFax · 6 dashboards (API health, vitals, tasks, signature, dictation, HIE) · imaging bundle (RIS/PACS/CRM/EMR modules). Built per the offline-AI spec (all-AI-on-device where possible; no PHI leaves the phone).
2. **THE AGNOSTIC INTERFACE LAYER (the moat)** — NURA AI Core + NextGen Connect/Mirth per-EMR adapters. Every EMR (Epic, Cerner, eCW, Athena, OpenEMR, eMedical) plugs in via FHIR R4 + SMART on FHIR + HL7 v2. EMR-specific logic lives in the adapter, NEVER in the app. Onboarding = plug in an adapter.
3. **THE AI CORE (Nura Tron)** — the clinical intelligence: evidence layer (FDA · PubMed · CDC · OpenEvidence · BioPortal), clinical language models (Bio_ClinicalBERT/ClinicalBERT/GatorTron — free lanes), model routing (DeepSeek first → Gemini → Anthropic when needed; vision cascade separate), swarm synthesis for hard questions.
4. **THE AUTOMATION LAYER (Nura Claw)** — **Hermes is ALWAYS baked into the SaaS**: every NURA customer deployment ships with the Hermes agent platform (the executive orchestration layer) — the Paperclip org (57+ named agents: Atlas CEO, Orion CTO, Iris CMO, Midas CFO, Tally, Florence, Loom, Frame, Bridge, Meridian, Echo, Ink, Nexus, Reel + SaaS division), weekly scrum, self-healing watchdogs, autonomous ops. Customers don't buy "AI tools" — they buy a practice that runs itself, with Hermes inside managing the agents, lanes, and workflows. This is the differentiator no competitor ships: **NURA = software + its own operator.**
5. **THE OPERATIONS LAYER (NURA CRM + NURA ERP)** — Perfex (leads, invoicing, RCM) + OpenEMR (clinical records) + Mirth (interop) + GHL (patient comms) — all branded NURA externally.
6. **THE MEMORY (Long-Term Memory Framework)** — Mem0 + local RAG (fastembed, zero-credit) + self-model: continuity across sessions, doctrine ledger, user model.

## The data flow (one example end-to-end)
Patient calls → AI voice receptionist (Echo) books via OpenEMR schedule → reminder via Twilio/Firebase → visit recorded → AI Scribe (Whisper → Gemma/DeepSeek SOAP) → provider approves → note saves to OpenEMR → fee sheet → Mirth DFT → Perfex invoice (sanitized) → recall scheduled → media engine sends aftercare video (Reel) → outcomes tracked in dashboards → population health turns reports into work (CarePilot Phase 2).

## The doctrine (non-negotiable)
Verification before declaration · no fabricated status · PHI stays local (never to Perfex/external lanes) · consequential actions approval-gated · fast/accurate/free model routing · failure doctrine (fix → skill → memory → cron) · human-supervised clinical autonomy · audit everything.

## Where everything lives
- Docs: /opt/data/home/nura-clinical-platform/docs/ (manuals, projects, clinical)
- Skills: 170+ skills (ops, clinical, dev, media, population health)
- Board: Paperclip :3101 (Nuratech.ai + NURA Imaging SaaS Division)
- Infrastructure: Clinic 1441409 (EHR/PACS/PHI) · Lab 1030183 (compute) · Edge 817449 (pay/CRM) · Mac Studio (future local AI)
