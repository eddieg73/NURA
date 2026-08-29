# gstack (Garry Tan / YC) — study + adoption note (2026-08-29)

Date: 2026-08-29 · Operator: Hermes (CTO) · Source: `github.com/garrytan/gstack` (MIT)

## What it is
Garry Tan (President & CEO, Y Combinator) — **github.com/garrytan/gstack** (~130k★, 19,596 forks, 820 issues,
MIT, TypeScript, pushed 2026-08-29). *"Use Garry Tan's exact Claude Code setup: 23 opinionated tools that serve
one goal — ship."* Installs as a Claude Code skill package; requires Claude Code + Git + Bun (Anthropic-coupled).

## The headline (measured, self-reported)
60 days part-time while running YC full-time: 3 production services, 40+ shipped features, ~810× logical-code
run rate vs 2013 (11,417 vs 14 logical lines/day), 240× the entire 2013 year YTD. Thesis: one builder + the right
opinionated tooling ships like a team — the Karpathy "shipping solo" revolution.

## The reusable VALUE (what we took, not the coupling)
The **ship/verify/watch discipline**, which we ported (runtime-agnostic) into the `gstack-shipping-doctrine` skill:
- **Plan → Review** (plan-eng/ceo/design-review; the "review army" of parallel specialists).
- **Two-pass pre-merge review** (`review/checklist`): Pass 1 CRITICAL (SQL/data safety, race conditions, **LLM output
  trust boundary**, shell injection, enum completeness) + Pass 2 informational + parallel specialists
  (test-gaps, dead-code, magic-numbers, side-effects, performance, crypto). Fix-first; batch ambiguity into ONE question.
- **Pre-merge readiness gate**: evidence + explicit approval before the irreversible merge; review-staleness (7-day)
  check; warnings vs blockers; FIRST_RUN/CONFIG_CHANGED → dry-run first.
- **Land + deploy + canary verify**: a green build is NOT a live service — verify production health end-to-end.
- **Retro + document-release** (compounding lessons; the "everything documented" law).
- **guard/freeze**: destructive-command warnings + directory-scoped edits (the anti-footgun).

## Why it matters to NURA
- It validates our exact integrating thesis (one Agent-OS, no vendor lock, we own the process) with hard evidence.
- It's **MIT** → clean to adopt. We take the METHOD, NOT the Claude/Bun runtime (no-vendor-lock doctrine).
- The **LLM output trust boundary** check = our anti-hallucination law applied to code. Critical for AI-written code.
- It feeds the **sovereign Agent-OS** (CoreCoder/microsoft-agent-framework + MCP): the harness produces, the
  two-pass gate + readiness + canary make it safe to run.

## Adoption decision
ADOPT the shipping-doctrine skill (MIT, runtime-agnostic). Do NOT adopt the Claude Code runtime.
Wire the two-pass gate + readiness + canary into the NURA deploy discipline (deployment-ops skill) and the
sovereign Agent-OS harness.

## Artifacts
- Skill: `gstack-shipping-doctrine` (devops).
- Sovereign harness reference: `/opt/data/agentos-core` (CoreCoder fork; P0 proven via dock Ollama).
