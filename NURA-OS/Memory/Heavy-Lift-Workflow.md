# Heavy-Lift Workflow — GEMINI 1M lane (2026-08-03; Z.ai dropped, Gemini replaced it)

**Purpose:** the 1M-context lane for whole-thing-in-one-pass work. One brain, extra hat.

## Trigger → Flow
```
JOB NEEDS BIG CONTEXT (whole repo / whole case file / whole doc)
  → is the cheap chain enough? (DeepSeek first pass — 90% of work)
  → NO → heavy lane:
       hermes -p heavy -z "<task>" [-t terminal]   (workspace dir = the job's repo)
       → output to workspace → Hermes reviews/verifies → provider/attorney gate if clinical/legal
```

## The 3 standing jobs
| Job | Why GLM | Gate |
|---|---|---|
| App builds (nura-medical/openpilot/n8n) | whole repo in context, no chunking | code review before merge |
| MLR case files (autopsy/tox/records) | entire case = one pass, Daubert chronology | Eddie + pathologist sign |
| Reg A / contracts | circular + comps + rules in one read | SEC counsel review |

## Rules
1. One brain — GLM executes jobs, Hermes decides (scope, verification, signing).
2. No PHI/secrets to the lane; outputs stay in the Lattice (workspace/vault).
3. Cheap-first: GLM is the heavy hammer, not the default tool.
4. gateway-glm stays DOWN — the lane is invoked on demand, never a second always-on brain.

## Activation
Lane ALREADY LIVE (Gemini quota wired). Smoke test: `hermes -p heavy -z "Say ready."` → expect `ready`.
(Skill: model-selection · local-model-picks)
