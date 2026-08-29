# NURA — THE WORLD'S FIRST SYNTHETIC CLINICIAN PLATFORM (v2.0, 2026-02-24)
Confidential product/business plan. THIS FILE = adopted deltas only (deduped against NURATECH-MASTER-MANIFEST.md, OFFLINE-AI-MEDICAL-COMPANION.md, NURATECH-AI-TECHNOLOGY-MASTER-PLAN.md, NURA-IMAGING-MASTER-PLAN.md).

## PRIME DIRECTIVE (founder 2026-08-02): ONE master agnostic app
**The product = ONE master app that serves providers by interfacing with ALL EMRs.**
- Single NURA app (voice-first, 6 dashboards, agents, scribe, dialer, fax, imaging bundle) for every provider — regardless of their EMR.
- **Agnostic interface layer** = the NURA AI Core + NextGen Connect/Mirth per-EMR adapters (Epic, Cerner, eClinicalWorks, Athena, OpenEMR, eMedical, athenahealth...): FHIR R4 + SMART on FHIR + HL7 v2 per adapter; EMR-specific mapping isolated in the adapter (never in the app).
- RIS/PACS/CRM/EMR-adjacent modules = **bundle components inside the app** (SaaS division DIV-1), NOT separate products with separate financials.
- Provider onboarding = plug-in an adapter, not a new system. This is the moat: **any practice, any EMR, one NURA.**

## Positioning (NEW, adopt)
NURA = world's first true **synthetic clinician** — a parallel AI agent for clinicians integrating multiple systems from one unified platform, with an autonomous AI physician always by the side. Voice-first ("Hey NURA"), 6 specialized dashboards, multimodal reasoning, proactive 24/7 monitoring (OpenClaw EMH), multi-system integration (Epic/Cerner/labs/imaging/pharmacy/HIE).

## Competitive gap (NEW, adopt for positioning)
- vs **Sully.ai** (6 separate agents, text, reactive): NURA = one platform, voice-first, proactive, multimodal.
- vs **Nuance DAX** ($500–1,200/mo, documentation only): NURA = full workflow + reasoning at $100–150/mo (5–10× cheaper).
- vs **Epic/Cerner** (comprehensive, not intelligent): NURA = AI layer on top.
- Pricing: Tier1 Solo $100 · Tier2 Group $125 · Tier3 Health System $150 per provider/mo; add-ons: analytics +$25, custom AI +$50, pro services $10–50K.

## 6 dashboards (adopt — maps to Mission Control + app)
1 API Integration (connection health) · 2 Vital Signs (real-time, NEWS2/qSOFA/MEWS) · 3 Task Management (unified inbox) · 4 Progress Notes Signature (batch sign) · 5 Progress Notes Dictation (ambient SOAP) · 6 HIE (query/reconcile/consent).

## Multimodal stack (adopt — ties to our lanes)
Imaging: Vision Transformer on MIMIC-CXR · Labs: trend/delta checking · Vitals: NEWS2/qSOFA/MEWS · ECG waveforms · H&P: GatorTron + ClinicalBERT (our clinical-bert-inference-lanes!) · Genomics: CPIC/PharmGKB (Phase 6+).

## Implementation roadmap (adopt as the master build sequence — 10 phases, 128 wks)
P0 safety (CDS Hooks 2.0, critical labs, med rec, imaging results, consent, cyber) → P1 FHIR R4 + SMART on FHIR + bidirectional sync → P2 voice (Whisper + ElevenLabs) + NLU (GatorTron/ClinicalBERT) + multi-LLM orchestration + OpenClaw EMH → P3 6 dashboards → P4 AI agents (pharmacist/coder/consultant/scribe/nurse/receptionist) → P5 clinical workflows (eRx, orders, care coord, quality, chronic disease, pediatrics) → P6 advanced (imaging, labs, vitals, genomics, population health, predictive) → P7 EMR expansion (18 EMRs, Redox/Particle/Health Gorilla) → P8 production (latency <500ms, 99.9%, HIPAA audit, FDA 510(k) path, DEA EPCS, CLIA) → P9 clinical validation (MIMIC-IV 10K retrospective, RCT) → P10 launch.

## Success metrics (adopt for the board scorecard)
Doc time 2–3h→<30min · chart closure <2h · prior auth <24h · coding +11% · medication errors <1/100 orders · sepsis mortality −20% · readmissions <10% · NPS >70 · provider count 1K (m12) → 10K (m24) → MRR $50K→$1M → ARR $12M (m24).

## Funding (adopt for Atlas/Midas)
$1.616M over 25.5 mo to production-ready · $3.366M over 3.5 yr to market-ready · seed ask $5M (18 mo) · team 10 eng + 3 clinicians + 2 PM.

## SPECIALTY DOCTOR NETWORK (founder 2026-08-02 — NUR-67)
**Paperclip builds a DOCTOR for every specialty — a named specialty agent (synthetic clinician), each with its own connected APIs + MCP lanes for that specialty's data.**
- Model: one specialty doctor per domain (cardiology, dermatology, endocrinology, gastroenterology, neurology, OB/GYN, orthopedics, podiatry, urology, wound care, psychiatry, pulmonology, interventional radiology/cardiology, Mohs, oral-maxillofacial, general surgery, pediatrics, internal medicine, emergency/tactical...). Each doctor = agent persona + specialty skill set + its evidence/API lanes (openFDA/PubMed/terminologies + specialty registries) + template library (SOAP/H&P/consult templates per specialty).
- MoE routing: medical-specialty-router skill routes cases to the right doctor; escalation to a generalist or frontier model when needed.
- Build order (practice value): aesthetics → endocrinology/HRT/GLP-1 → primary care → psychiatry (TMS) → radiology (imaging) → then long-tail specialties.
- Delivery: specialty doctors ship INSIDE the master app (new patient → routed to the specialty doctor; specialty lane connectors = the API/MCP wiring per doctor). All skills (170+) ship with the SaaS — the specialty playbooks are the product's brain, not just the app's.

## DEDUPED (already in canon — do not re-file)
Ambient scribe/SOAP (scribes), dialer/fax (M1), AI agents roster (Paperclip corps), imaging analysis (imaging plan + Frame), RCM/coding (master plan), voice-first (voice persona), offline app (offline-ai-medical-companion), pricing tiers vs manifest. This file holds ONLY the deltas: positioning, 6-dashboards, competitive table, roadmap P0–P10, metrics, funding.
