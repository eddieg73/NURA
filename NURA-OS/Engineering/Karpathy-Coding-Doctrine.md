# Karpathy Coding Doctrine — adopted 2026-08-15

Source: `multica-ai/andrej-karpathy-skills` (founder's repo drop), derived from Karpathy's LLM-coding-pitfalls observations. Installed as skill `karpathy-guidelines` (software-development category). MIT.

## The four principles

### 1. Think Before Coding
- State assumptions explicitly; ask rather than guess
- Multiple interpretations → present them, don't pick silently
- Simpler approach exists → say so, push back
- Confused → stop, name it, ask

### 2. Simplicity First
- Minimum code that solves the problem; nothing speculative
- No abstractions for single-use code; no unrequested "flexibility"
- No error handling for impossible scenarios
- 200 lines → 50 = rewrite

### 3. Surgical Changes
- Touch only what you must; don't "improve" adjacent code/comments/formatting
- Don't refactor things that aren't broken; match existing style
- Unrelated dead code → mention, don't delete
- Clean up only orphans YOUR changes created

### 4. Goal-Driven Execution
- Convert tasks to verifiable goals: "fix bug" → "write a test that reproduces it, then make it pass"
- Multi-step tasks → numbered plan with per-step verify checks
- Strong success criteria let the loop run independently

## The Karpathy problem statement (the honest mirror)
> "Models make wrong assumptions and run with them without checking. They don't manage their confusion, don't surface inconsistencies, don't present tradeoffs, don't push back. They overcomplicate, bloat abstractions, don't clean up dead code. They change code they don't understand as side effects."

## Hermes application (self-audit)
- The Mirth channel saga: I assumed XML formats instead of sourcing the canonical export first → now doctrine: import converters are client-side; source the real format BEFORE hand-crafting (Skill: hermes-mirth-connect).
- "Do it all" turns: apply Goal-Driven Execution — enumerate the plan with per-step verification before sprawling.
- Pair with existing: HERMES.md think-first, anti-hallucination, systematic-debugging, requesting-code-review skills.
