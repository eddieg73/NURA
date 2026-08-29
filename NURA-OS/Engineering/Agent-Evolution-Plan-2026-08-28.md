# NURA Agent Evolution Plan (CTO + CAO) — 2026-08-28

Date: 2026-08-28 · Owner: Eddie (founder) · Planner: Hermes (CTO + CAO)
Status: LIVE — baseline captured, engine operational, daily loop wired.

## A. Why (the honest diagnosis)
`hermes-dojo` was dead-letter: the SKILL.md existed but `scripts/` was empty, the
self-evolution repo was missing, and no evolution cron was armed. "Continuous
self-improvement" was aspirational, not operational. This plan replaces it with a
WORKING evidence-driven loop.

## B. Baseline (measured from the real session store — not theory)
Source: `/opt/data/profiles/nura/state.db` (992 MB, 144k messages).
Engine: `/opt/data/profiles/nura/scripts/evolution_engine.py`.
Report: `/opt/data/profiles/nura/state/evolution_baseline.json`.

7-day window:
- user_messages: 1424, corrections: 686 → **correction_rate 48.2%** (the #1 metric to attack)
- total_tool_calls: 8255
- top hard-fail tools: `unclassified` 136 (behavioral) + `read_file` 3 (mechanical)

**Interpretation:** the dominant failure class is NOT tool bugs — it's behavioral
(precision, scope-discipline, verification discipline). Mechanical tool failures are
near-zero (read_file: 3). So the highest-ROI improvement is **verification + scope
discipline on consequential outputs**, not fixing broken tools.

## C. The improvement loop (measure → identify → fix → verify → report)
1. **MEASURE** — `evolution_engine.py` scans the real session store daily; writes
   `state/evolution_baseline.json`. (Replaces the dead dojo monitor.py.)
2. **IDENTIFY** — the correction-rate metric + top failure class tells us WHERE to
   invest. Correction rate is the north star; per-tool failures are tactical.
3. **FIX** — two levers, executed by the dev team (subagents) or direct:
   - **Behavioral** (dominant): route consequential outputs through the existing
     `cto-answer-verification` + `requesting-code-review` gates (independent-model
     critique + evidence-before-declare). These skills already exist — they were
     under-enforced, not missing.
   - **Mechanical** (rare): patch the specific failing skill/script.
4. **VERIFY** — re-run the engine; correction rate must drop (or error class change)
   before declaring an improvement.
5. **REPORT** — daily evolution digest to the home channel (delta only).
6. **PERSIST** — every fix lands as a skill/patch (procedural memory compounds),
   and the result is logged to `state/evolution_history.json` (append).

## D. Instruments (operational)
- Engine: `/opt/data/profiles/nura/scripts/evolution_engine.py`
- History: `/opt/data/profiles/nura/state/evolution_history.json` (append, one entry per day)
- Daily job: cron `agent-evolution-daily` (armed 2026-08-28) — measure + report + flag.
- Verification gates: `cto-answer-verification` (routine vs consequential tiers),
  `requesting-code-review` (independent reviewer for code), `anti-hallucination`.

## E. Rules (best practice)
1. Never "improve" without a measured baseline — no baseline, no change claim.
2. The correction rate is the true north-star metric; tool call counts are supporting.
3. Every fix must be evidenced (re-measured) before it's called an improvement.
4. Skills/procedures are the durable home of a fix — never just "I did it this once."
5. Report the delta, not the dump; stay token-frugal (the founder's rule).
6. Same-failure-twice => the fix didn't take => force a deeper pass (governing skill).

## F. First execution (this session, already done)
- Built `evolution_engine.py` (works, baseline captured).
- Corrected the dead dojo understanding (it was aspirational).
- Captured the 48.2% correction-rate baseline.
- Wired the daily cron (`agent-evolution-daily`).
- Dispatched the dev team to audit the improvement stack (completed 2026-08-28).
- **Dev-team audit result:** 9 of 10 improvement skills are doctrine/spec-only (enforceable by following); the ONE true dead-letter was `hermes-dojo` (referenced scripts/repo at wrong path).
- **Fixed the dead-letter:** the dojo scripts actually live at `/opt/data/hermes-dojo/scripts/` (relocated repo) and RUN cleanly (monitor.py analyzed 651 sessions / 7,800 tool calls with real tool-level attribution). Patched the skill to point at the working paths (analyze + track). The skill is now runnable, not aspirational.
- **Folded tool-level signal into the daily loop:** the daily wrapper now emits BOTH behavioral (correction-rate) AND mechanical (dojo per-tool failure) signals.

## G. Actionable findings (from dojo monitor, 2026-08-28)
### Skill gaps — recurring tasks with NO governing skill (high-value to fix: this is the compounding gap)
- `deployment`: requested 258× (no skill)
- `docker-management`: requested 231× (no skill)
- `database-operations`: requested 208× (no skill)
- `api-integration`: requested 60× (no skill)
- `git-operations`: requested 16× (no skill)
- `unit-testing`: requested 6× (no skill)

These are the top "same-failure-twice" candidates: I keep doing these repeatedly without a compiled playbook, so I re-derive each time — exactly what a SKILL should capture.

### Tool-level failures (0% success — fixable)
- `mcp__provider_labs__email_ingest`: 111/111 fail — the known lane-down (gws/GoogleOAuth unset) — already flagged SILENT in memory.
- `mcp__runpod__list_gpu_types`: 401 invalid API key.
- `browser_navigate`/`browser_vision`: os error 2 (browser not wired).
- `mcp__github__create_repository`: permission denied (fine-grained PAT has no repo-create — by design).

### Behavioral inefficiency
- 949 retry loops, esp. `skill_view` called 6× in rapid succession → repeatedly loading instead of acting. Directly tied to correction rate.

## H. Next steps (ranked, by ROI on the correction rate)
1. **Create the 4 missing skills found by the gap analysis** — but as UMBRELLAS: e.g. one `deployment-ops`, one `database-operations`, one `docker-ops` umbrella skill that captures the compiled playbook + pitfalls, so the 258×/231×/208× re-derivation stops. (There may be existing fragmented skills that should fold under these umbrellas — union, don't duplicate.)
2. **Fix the retry-loop habit** — patch the behavior so skill_view/terminal aren't re-loaded mid-task; each is loaded once and applied.
3. **Re-measure in 7 days** — expect correction rate to trend below 48.2%.

## I. Open items / next
1. Run the behavioral fix sprint: wire `cto-answer-verification` into consequential
   deliveries as a HARD gate (not optional).
2. Re-measure in 7 days; expect correction rate to trend below 48%.
3. Optionally rebind self-evolution (GEPA) once the repo is cloned — lower priority
   than the behavioral gate since our failures are behavioral, not model-prompt-level.
