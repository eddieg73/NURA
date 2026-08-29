# NURA HARNESS ENGINEERING (2026-08-09 — the four production layers, implemented!)

## Layer 1: Tool-Context Optimization (MCP + Code Execution)
**The standard adopted:** the agent writes code-snippets → queries the tools/APIs → filters/transforms INSIDE the sandbox → returns ONLY the final-filtered result.
**The NURA-implementation:**
- The `execute_code`-lane = the execution-sandbox (the hermes_tools: web_search/web_extract/terminal + the in-script filtering!)
- The pattern (the NURA-standard!): probe → reduce (the .head()/.slice()/.grep!) → return-small (the ≤2KB-result-window!)
- The evidence: today's API-probes (the Firecrawl-7-site-sweep → the 640-char-verdicts! · the GitHub-searches → the star+desc-only!) — the token-bloat-avoided!
- The MCP-lane-design: the 25+ lanes carry the SCHEMAS; the sandbox carries the FILTERING — the context stays lean!

## Layer 2: Tiered Memory (the 3-tier, confirmed!)
**The NURA-stack IS the 3-tier architecture:**
- Tier-1 (loaded-at-boot!): SOUL.md (the identity + the doctrine!) + USER.md (the founder!) + MEMORY.md (the durable-state, 7.9K/8K!)
- Tier-2 (search-first!): the mem0-store (the semantic-recall!) + the session_search (the past-session-retrieval!) + the vault (the canonical-docs!)
- Tier-3 (procedural!): the 500+ skills (the SKILL.md-files — the distilled-solutions!) + the skill-factory (every-fix → a skill!)
**The self-improvement-loop: RUNNING (the tunnel-guardian · the upgrade-loop · the mesh-builder = today's skills-born-from-tasks!)**

## Layer 3: Trajectory Tracing + Failure Classification
**The NURA-implementation:**
- The trace: [intent] → [reasoning] → [tool-input] → [stdout/stderr] → [reflection] — the session-logs + the observability-trace-logger skill!
- The failure-classification (the 3 buckets!):
  - PLANNING-failure: the wrong-approach (the plan-griller-catches!)
  - EXECUTION-failure: the script/API-error (the n8n-SQLITE-constraint = THIS bucket!)
  - CONTEXT-overflow: the payload-bloat (the token-efficiency-ops!)
- The NEW-artifact: the trace-classifier script (below!)

## Layer 4: Async HITL Gatekeeping
**The NURA-implementation (the freeze-resume!):**
- The tiered-approval (the constitution!): read-only-auto · chart-write-provider · orders-qualified-human · destructive-explicit!
- The channels: the Telegram (the founder's lifeline!) — the approval-payloads route there!
- The freeze-state: the .env-sealed + the audit-logs + the idempotent-ledgers (the bridge's dry-run-then-live!) — the resume-without-context-loss!
- The doctrine: the consequential-gates (deletes · creds · clinical · money · external · firewalls!) — the approved-list + the fail-closed-default!

## The verdict
The four layers are now the written engineering-doctrine — the code-execution-filtering, the 3-tier memory, the failure-classification, and the async-gates — each mapped to the running-stack with the artifacts below!
