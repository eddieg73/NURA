# xAI → NURA Team Correlation Plan

**Date:** 2026-08-19 · **Author:** Atlas (Paperclip CEO) · **Directive:** founder batch — research xAI's org, correlate every position to NURA, formulate the hiring/agent plan.
**Sources:** public reporting only (The Information org charts, TechCrunch 2026-02 all-hands, Business Insider 2025-03/2026-04, x.ai, public job postings, SemiAnalysis). No PHI, no non-public material.

---

## 1. What xAI actually is (public facts, Aug 2026)

- Founded July 2023 with the mission "understand the true nature of the universe." Merged with X Corp into **X Holdings**; since April 2026 folded closer into **SpaceX** (SpaceX SVP Michael Nicolls now xAI president) ahead of the SpaceX IPO.
- **The model:** an extremely small elite technical core × extreme compute. Year one: ~12 technical people running 5,000→100,000+ GPUs. Workforce grew past ~1,200 (early 2025) but leadership has been through repeated purges — every co-founder except Musk has left.
- **Compute:** Colossus (Memphis) — 100K H100s built in 122 days, doubled to 200K in 92 days, roadmap 1M GPUs; Colossus 2 (Southaven MS) targeting gigawatt scale. Verified-data collection was a headline Grok 4 ingredient ("massive data collection effort… significantly expanded verifiable training data").
- **Feb 2026 reorg → four primary product teams:** (1) Grok chatbot incl. voice, (2) the app's coding system (Grok Coder), (3) Imagine video generator, (4) **Macrohard** (computer-use simulation → modeling entire corporations; lead Toby Pohlen).
- **Structural lesson for NURA:** xAI is not a lab — it is an engineering entity that vertically owns data → compute → models → product → distribution. NURA already runs the same doctrine (Lattice-Wiring.md).

## 2. xAI's functional role families (from public org charts + job posts)

| Family | xAI roles observed |
|---|---|
| **Leadership** | CEO (Musk) · President (Nicolls, SpaceX) · CFO · Chief of Staff (Ross Nordeen, departed) · Engineering Leader, Enterprise |
| **Research — pre-training** | Co-founder Igor Babuschkin (ex-DeepMind) leads foundational model work; scaling/reasoning researchers (Tony Wu, Guodong Zhang promoted 2026) |
| **Research — post-training/RL** | Jimmy Ba (optimization); RL-at-pretraining-scale runs (Grok 4); reasoning, math (Szegedy-era focus) |
| **Research — IC** | "Member of Technical Staff" (MTS) — senior research engineers hired for proven compute-utilization track records |
| **Data engineering** | Verified-data collection pipelines, data quality, multimodal corpora (the Grok 4 differentiator) |
| **Infrastructure engineering** | Cluster/systems engineering, InfiniBand networking, training systems, storage |
| **Datacenter operations** | Site Ops technicians/supervisors, Site Ops II (parallel triage/repair automation across thousands of GPU nodes), Manager Operations (facilities, power generation, fiber, 24/7 uptime, MTTD/MTTR) |
| **Product engineering** | Grok app + voice · Grok Coder · Imagine · Macrohard · (per-persona product teams) |
| **Alignment / safety** | Embedded in research; interpretability and post-training safety work |
| **Enterprise / GTM** | Enterprise engineering leader, enterprise sales/support |
| **Corporate** | Security (corpsec/infosec), recruiting, legal/policy, finance |

## 3. Correlation: every xAI role → NURA equivalent → gap

| xAI role | NURA equivalent | Type | Gap / action |
|---|---|---|---|
| CEO | **Atlas (Paperclip CEO)** + founder final authority | Agent | No gap — cadence exists (paperclip-ceo-control). |
| President / COO | **Hermes orchestrator** + division-board-ops + one-brain rule | Agent | Cross-division P&L discipline is manual today → add monthly lattice audit task. |
| CFO | **Assurance** (NMI/ledger) + self-hosted-accounting | Agent + **HIRE** | Reg A requires human CPA — **hire #1 (fractional CPA/audit firm), pre-filing.** |
| Chief of Staff | control-executive-assistant + paperclip-board-ops | Agent | No gap. |
| Pre-training research | Local Ollama **16 models** (med42/meditron/qwen3) + Kaggle fine-tune lane (nura-clinical-model-training-lane) | Agent | NURA does not pre-train (correct — we fine-tune open weights; no gap at our scale). |
| Post-training / RL | **MSO Coder** (RAF/HCC) + coding agent + nura-clinical-regression-suite | Agent | No RL infra — by design: deterministic CDS (NEWS2/TCCC) replaces RL scoring. |
| Research IC (MTS) | Skill-level specialist lanes (medical-specialty-router MOE) | Agent | Broad specialty coverage thin → grow specialty skill library (queue). |
| **Data engineering** | Dataset-governance registry + **6 B2 buckets** + imaging corpus + lab-intake-interpreter cron | Agent | **Gap:** dataset access gates pending (CITI credential, kaggle.json, CheXpert license) — founder action item; xref schema = this plan's Clinical-Data-Wiring-Plan. |
| Infrastructure engineering | MCP lanes (61+) + docker-manager + fleet ops (Clinic/Lab/Edge) | Agent | No gap — watchdog crons already prevent drift. |
| Datacenter operations | Fleet watchdogs (swap/docker-disk-pressure) + hostinger-cli-ops | Agent | No gap. 3 nodes vs 500K GPUs — NURA inherits the *automation-first ops* doctrine, not the hardware. |
| Product engineering (Grok app) | Flutter 5-tab app + flutter-product-builds + ONE-App architecture | Agent + **HIRE (later)** | Clinical UX needs a human beta program — **hire #3 (fractional clinical UX/QA)** after app beta. |
| Voice | **Echo voice loop** + EMH voice layer (ElevenLabs) | Agent | No gap. |
| Enterprise / GTM | CarePilot/Solis/Ensure ops + vendor-portal-access | Agent now, **HIRE later** | Enterprise sales/account mgmt = **hire #5** when revenue pipeline warrants. |
| Alignment / safety | hermes-clinical-safety-escalation + **EMH-Autonomy-Ladder** + nura-ai-evaluation-monitoring | Agent | Formal eval harness partial → complete regression suite before any ladder climb (P2). |
| Security | military-grade-hardening + agent-security-scanning + llm-security-review | Agent + vendor | Annual external pentest (vendor) — **hire #4**, mandatory before Autonomy L2. |
| Recruiting | paperclip-hiring-operations | Agent | HR compliance for W-2s needs a human when first full-time hire lands. |
| Legal / policy | SEC/Reg-A skills + outside counsel | Human (existing intent) | Monitor; outside counsel already on Reg A path. |

## 4. Hiring plan (sequenced, humans-only-where-law-or-clinical-license-requires)

1. **H1 — Fractional CPA / audit firm** (Reg A books, Assurance sign-off). *Now — pre-filing.*
2. **H2 — Medical director / physician champion** — board-level clinical oversight; owns approval of every Autonomy-Ladder level-climb and specialty-lane deployment; anchors a **contract specialty reviewer network** (radiologist wet-reads, cardiology review). *After data-wiring P1.*
3. **H3 — Fractional clinical UX / QA human** — beta program for the Flutter app. *After app beta.*
4. **H4 — External pentest vendor** (annual) — gating control for Autonomy L2+. *Before L2.*
5. **H5 — Enterprise/sales lead** — CarePilot/Solis/Ensure growth. *Revenue-gated.*
6. **H6 — Specialty reviewer network** (telehealth/contract) — reads + audits EMH drafts; mirrors the radiology-learning-stack wet-read lane. *With H2.*

## 5. What stays agent-carried (never hire for these)

Infrastructure, datacenter ops, research fine-tunes, data pipelines, product build, voice, coding, recruiting pipeline, security scanning, dashboarding — the entire **Lattice spine** is agent-carried today and this is NURA's structural advantage. The xAI correlation proves the model: xAI's 12-person core did what OpenAI scaled to thousands for; NURA's 1 founder + agent fleet is the same leverage applied to clinical data instead of GPUs.

## 6. Honest gap analysis

- **NURA cannot copy:** frontier compute (gigawatt datacenters), proprietary model research, 1,200-person depth. None of it is needed — open weights (med42/meditron/qwen3) + local Ollama + deterministic CDS cover the clinical lane at sovereign cost.
- **NURA's real gaps are human, and they are legal/clinical, not technical:** licensed clinical oversight breadth (H2/H6), CPA sign-off (H1), security attestation (H4), UX validation (H3). The machine layer is essentially complete; the credential layer is the hiring plan.
- **The xAI trait worth cloning:** *data obsession.* Grok 4's moat was verified-data collection, not raw compute. NURA's equivalent moat = the cross-referenced clinical corpus (labs ↔ imaging ↔ diagnoses ↔ HCC) in the companion plan. That is NURA's Colossus.

## 7. Lessons adopted from xAI's operating model

1. **Small core × huge leverage** — 12 people, 100K GPUs → 1 founder + agent fleet, 16 models.
2. **Vertical ownership** — data → models → product → distribution, one stack (already NURA doctrine: Lattice-Wiring.md).
3. **Data-first, compute-second** — verified corpora over raw scale → NURA: clean linked clinical data over model size.
4. **Ruthless structure evolution** — xAI reorgs without sentiment → NURA skill-consolidation doctrine (umbrella skills, prune stale lanes).
5. **Speed as a feature** — Colossus in 122 days → NURA ships v1-lanes fast then hardens (wet-read gateway pattern).

---
*Sources: theinformation.com/org-charts/xai · techcrunch.com/2026/02/11/xai-lays-out-interplanetary-ambitions · businessinsider.com/xai-org-chart-employees-elon-musk-direct-reports-2025-3 · businessinsider.com/elon-musk-reorganizes-xai-ahead-of-spacex-ipo-2026-4 · x.ai/colossus · x.ai/news/grok-4 · newsletter.semianalysis.com (Colossus 2) · xAI public job posts (Manager Operations / Site Ops, Memphis).*
