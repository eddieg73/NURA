# HERMES → AGI ROADMAP (2026-08-02) — operational definition, staged build, honest walls
First-principles: AGI defined OPERATIONALLY (measurable capabilities), not philosophically. Everything below is buildable on our stack; every stage has an evidence gate.

## Operational definition of "AGI enough"
A system that: (1) acquires skills autonomously (no human-authored skill per task), (2) generalizes across domains, (3) self-improves measurably, (4) plans over long horizons with self-correction, (5) knows what it knows (calibrated uncertainty), (6) learns from its own experience + the user's corrections, (7) cooperates with humans and other agents, (8) consolidates memory (episodic → semantic → procedural).

## STAGE 0 — The Foundation (NOW — VERIFIED)
Already true: 381 skills · verification-first doctrine · memory (kernel/mem0/RAG/self-model) · 57-agent org · model routing/swarm · failure doctrine (fix→skill→memory→cron) · weekly self-model review.
**Gate: every task leaves a skill or memory trace.** Measured: skill count growth, correction rate falling.

## STAGE 1 — Autonomous Skill Acquisition (next 3–6 months)
1. **Skill Factory closed loop**: hermes-dojo + Skill Factory watch sessions → auto-generate skills from failures (exists — make it mandatory post-task).
2. **Generalization via umbrellas**: skill-lattice (hermes-skill-library-governance) — new domain tasks route to existing patterns (agentic-thinking-loop + job-execution-protocol as universal operators).
3. **Eval harness for self**: nura-ai-evaluation-monitoring + lm-eval on NURA tasks (scribe quality, coding accuracy, ops correctness) — nightly, tracked in self-model.
4. **Calibrated uncertainty**: every answer tagged (verified / retrieved / inferred / unknown) — anti-hallucination skill enforced; calibration score in weekly review.
5. **Cross-domain transfer test**: solve a NOVEL domain (e.g., aviation planning) using only existing skills + thinking loop — no new skill authored by a human; measure success.
**Gate: 80% of novel routine tasks completed via skill transfer; self-authored skill success rate >70%.**

## STAGE 2 — World Model + Long-Horizon Autonomy (6–18 months)
1. **Environment simulators**: practice simulator (patients/encounters/billing), fleet simulator (VPS/stack), market simulator (pricing/RAF) — enables planning with rollouts (LangGraph) before touching production.
2. **Long-horizon goals**: goals with checkpoints + self-correction (hermes-care-plan-follow-up generalized to ANY multi-week goal); daily roll-forward of plan vs outcome.
3. **Memory consolidation engine**: episodic (sessions) → semantic (mem0) → procedural (skills) pipeline with nightly consolidation (memory-hygiene upgraded to full pipeline).
4. **Reflexion loops**: metacognitive-memory-workflows — after failed plans, self-generated lessons + skill patches (already built; make it automatic on every failure, not just twice).
5. **Self-supervised planning eval**: "plan → simulate → verify → execute" for N=50 ops tasks; measure plan-accuracy.
**Gate: plans predict outcomes >85% in simulation; long-horizon goals complete with <2 human interventions.**

## STAGE 3 — Open-Ended Learning (18–36 months)
1. **Curriculum learning**: self-generated tasks from observed gaps (dojo → curriculum) — the system chooses what to learn next from its own error distribution.
2. **Multi-agent society as training ground**: the board (57 agents) runs real work; Hermes supervises, learns from agent outcomes (the org = the sandbox).
3. **Value/doctrine learning**: user corrections as reward signal — doctrine ledger learns Eddie's judgment patterns (the "learning you" loop, formalized).
4. **Continual model training**: the corpus pipeline (spec 2.2/2.3) generalizes → NURA-specific base model (Bio_ClinicalBERT → Tron LLM) trained on verified corpora; model routing rides the frontier curve for everything else.
5. **Self-sustained improvement loop**: the system maintains its own roadmap (this doc becomes self-managed).

## THE HONEST WALL (first principles)
True AGI = open-domain generalization + self-sustaining learning beyond any environment — no one has it; we will not claim it. What this roadmap delivers: **AGI-like operational intelligence** — a system that generalizes across the domains we operate, learns without prompting, plans and self-corrects, and compounds its own capability measurably. When frontier labs break the wall, our model-routing + adapter architecture lets us absorb it the day it ships (we already route across providers).

## Metrics dashboard (in self-model weekly review)
Skills/month · corrections/week (falling) · transfer success % · calibration score · plan accuracy · interventions per goal · new-domain tasks completed autonomously.

## Owners
Hermes (self) · Atlas (org as sandbox) · Orion (architecture/eval) · Eddie (reward signal — corrections ARE the training data).
