# Self-Evolution Adoption Assessment (2026-08-15)

Assessment of the two published self-evolution systems against NURA's Phase-1
architecture (experience-ledger · failure-taxonomy F01-18 · skill-confidence ·
nightly-replay — see SELF-IMPROVEMENT.md).

## 1. Hermes-Agent-Self-Evolution (NousResearch, MIT)

**What it is:** offline batch pipeline — DSPy + GEPA (Genetic-Pareto Prompt
Evolution, ICLR 2026 Oral) reads execution traces, reflects on WHY failures
happen, mutates skills/tool-descriptions/system-prompt, evaluates candidates
against a test suite + constraint gates, and opens a PR.

- GEPA vs GRPO: +6–20% accuracy with 35× fewer rollouts; ~$2–10/run; no GPU.
- Phase 1 (SKILL.md evolution) implemented; Phases 2–5 (tool descriptions,
  system prompt, code via Darwinian Evolver, continuous loop) planned.
- **Guardrails (mapped to ours):**
  - 100% test-suite pass → our "verify before declare"
  - Size gates (skills ≤15KB, descriptions ≤500 chars) → our token-budget doctrine
  - Caching compatibility → our progressive-disclosure discipline
  - Semantic-preservation checks → our "no sediment / same source of truth"
  - Human-in-the-loop PR review, never direct commits → our
    evaluator-outside-the-candidate invariant

**Verdict: ADOPT as Phase-2 candidate.** It is the mechanized form of what
Phase-1 does manually. Adoption gate: Phase-1 ledger/taxonomy must be stable for
2+ weeks first; the eval suite must exist BEFORE the evolver runs (per repo
design).

## 2. SkillClaw (arXiv 2604.08377)

**What it is:** collective skill evolution across a multi-user agent ecosystem.
Interaction trajectories → centralized evolver (Refine / Create / Skip, reasoning
jointly over successes AND failures) → nighttime validation (candidate vs
current A/B in real environments; only improvements deploy — monotonic) → sync
to all agents.

**NURA mapping:** our ecosystem is already multi-user (founder + Hermes +
Paperclip agents + the shared skills dir `/opt/data/.agents/skills`). SkillClaw's
two killer properties map directly onto NURA gaps:
- **Night-validation A/B** → upgrade our nightly-replay (AUTO-DREAM) from
  "process the lesson queue" to "candidate-skill vs current, accept only if
  measurably better."
- **Collective evidence** → Paperclip agent sessions feeding ONE shared skill
  repository instead of isolated fixes.

**Verdict: ADOPT THE PATTERN, not the code.** SkillClaw targets OpenClaw
ecosystems; a Hermes port exists per community threads but is young. Implement
the night-validation A/B loop inside AUTO-DREAM; wire Paperclip session traces
into the shared evidence base.

## 3. Sequencing (what we do first)

1. **Now:** Phase-1 stabilization — ledger + taxonomy + skill-confidence logging
   (in flight). Night-validation A/B = the next AUTO-DREAM upgrade.
2. **Gate check (2 weeks):** Phase-1 stable → clone
   NousResearch/hermes-agent-self-evolution, build the NURA eval suite, run
   Phase-1 evolution on our top-10 highest-traffic skills with PR review.
3. **Later:** Phase 2–5 as the repo ships them; Darwinian Evolver (AGPL) only as
   an external CLI, never linked into our MIT code.

## References

- github.com/NousResearch/hermes-agent-self-evolution
- GEPA: "Reflective Prompt Evolution Can Outperform Reinforcement Learning"
  (ICLR 2026 Oral, Agrawal et al.)
- SkillClaw: arXiv 2604.08377 "SkillClaw: Let Skills Evolve Collectively with
  Agentic Evolver"
