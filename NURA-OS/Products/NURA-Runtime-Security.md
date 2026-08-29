# NURA RUNTIME SECURITY & SANDBOXING (2026-08-09 — the founder's final-four build!)

## 1. Circuit Breakers (BUILT — circuit-breaker.py!)
- The action-hashing: every tool-payload hashed (SHA-256!)
- The repetition-guard: the identical payload+stderr 3x → the hard-HALT + the alert!
- The budget-caps: the per-budget call-limits (200-calls default!) — the token/dollar caps per sub-agent = the next-tier (the config-value!)
- The state: /opt/data/profiles/nura/cron/output/circuit-breaker.json (persistent!)

## 2. Generator-Verifier (the critic-pattern — CONFIRMED LIVE!)
- The separation-of-duties: the generator (the code-writer!) ≠ the verifier (the reviewer!)
- The NURA-implementation: the github-code-review + the review-architecture + the cto-answer-verification + the requesting-code-review skills = the verifier-lanes!
- The flow: the delegate-build → the clean-verifier-audit → PASS (merge!) / FAIL (feedback-back!) — the doctrine's live!

## 3. Egress-Sandboxing (the POLICY — the config-ready!)
- The principle: the Docker-containers share the host-kernel → the egress-restriction at the container-level!
- The NURA-egress-policy: the sandbox-containers get the iptables-egress-filters (allow: the package-registries (npm/PyPI!) + the approved-APIs (the gateway-list!); block: the arbitrary-external!)
- The implementation-order: the eval-sandbox-network on the Lab/Edge (the isolated-bridge!) → the iptables-egress-rules → the verify!
- The micro-VM-lane (Firecracker/gVisor!) = the Tier-2 (the scale-trigger!)

## 4. Trajectory-Evals (BUILT — eval-bench.py!)
- The deterministic task-suite: the 5-tasks (docsgpt-health · ollama-tags · tunnel · mesh · firecrawl-key!)
- The 3-axis metrics: success-rate ✓ · step-time (the efficiency-proxy!) · the token/cost = the next-tier (the model-call-counts!)
- The results: /opt/data/profiles/nura/cron/output/eval-bench.json (the trendable!)

## The skill-tracking (BUILT — skill-tracker.py!)
- The metrics: the total-count · the sizes · the 7d/30d-activity · the top-categories!
- The results: skill-tracker.json — the growth-trend across the runs!

## The wiring (the crons!)
- The eval-bench: daily 06:00 (the morning-health-before-the-digest!)
- The skill-tracker: weekly (Monday 05:00!)
- The circuit-breaker: integrated into the failure-paths (the manual/cron-trigger!)
