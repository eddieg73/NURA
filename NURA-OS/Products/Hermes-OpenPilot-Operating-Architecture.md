# HERMES OPENPILOT-INSPIRED OPERATING ARCHITECTURE (2026-08-05, founder canonical)

**The architectural principle: Hermes = a distributed, supervised agentic operating system — NOT one unrestricted language model. Perception, memory, reasoning, planning, safety, execution, communication, clinical, financial, research, reflection, and monitoring are SEPARATE. No single model/agent/process may independently observe, decide, authorize, AND execute a high-impact action.**

## The core processes (the daemons)
1. **hermesd** (the master supervisor): start approved services · monitor health · restart failed noncritical services · disable unhealthy agents · maintain operating state · enforce dependency order · preserve logs · enter safe mode after repeated failures · prevent unauthorized services. NEVER performs clinical/financial/legal/physical actions itself.
2. **perceptiond**: normalize approved inputs (mic/cameras/wearables/medical devices/documents/email/SMS/calendar/CRM/EHR/sensors/vehicle/smart-home) → OBSERVATIONS (source, timestamp, confidence, data quality, sensitivity, consent) — never conclusions.
3. **conversationd**: NL/voice interaction (ASR, speaker ID, intent, tone, continuity, response gen, TTS, interruption) — output is ADVISORY until another process authorizes; the conversational model never directly controls tools/money/prescriptions/records/vehicles/security/communications.
4. **memoryd**: the 7 memory types + the storage gate (relevance, sensitivity, source, confidence, retention, proactive-use permission, user approval) — editable/reviewable/deletable by the user.
5. **worldmodeld**: the current understanding (priorities, schedule, relationships, projects, financial constraints, health context, environment, system state, events, risks) — distinguishes observed/user-provided/retrieved/inferred/predicted/unknown; an inference never becomes a fact by persistence.
6. **plannerd**: candidate plans with the full schema (objective, assumptions, steps, tools, permissions, benefit, risks, reversibility, human_confirmation, fallback, success_criteria) — may propose, never authorize.
7. **safetyd** — THE INDEPENDENT DETERMINISTIC CONTROL LAYER (outside the LLM context): identity + authorization verification · permission enforcement · clinical/legal/financial restrictions · confidentiality · communication boundaries · surveillance prevention · unsafe-action blocking · rate limiting · human confirmation · immutable audit · safe-state transitions. The reasoning model may NOT edit/disable/override it. When uncertain: DENY + human review.
8. **executord**: executes ONLY with a valid safetyd authorization token (action ID, signature, target, scope, expiration, user identity, risk class, tool availability) — reports success/failure/time/result/side-effects/reversibility/audit ID; never claims success without tool confirmation.
9. **messagingd**: SMS/email/Slack/voice/push/social — verify recipient/channel/content, privacy, quiet hours, authorization, sensitive-content flags, duplicate suppression; routine check-ins optional + rate-limited.
10. **clinicald**: the specialized clinical agents — outputs classified (documentation assistance · educational info · differential support · risk alert · guideline retrieval · medication-safety review · emergency escalation) — clinician review when patient care is affected; never autonomously prescribe/diagnose-final/initiate invasive treatment.
11. **financiald**: conservative reasoning (cash flow, liquidity, runway, debt, recurring obligations, downside, counterparty concentration, capital allocation, TCO, reversibility) — analyze/recommend only; never transfer/trade/borrow/sign/commit without explicit authorization.
12. **researchd**: the approved-source review (AI/medicine/finance/economics/law/cybersecurity/robotics/science/world events) — each item: source, publication date, event date, credibility, summary, relevance, contradictory evidence, recommended action, confidence; unverified ≠ fact.
13. **reflectiond**: scheduled synthesis + dream cycles (unresolved problems, contradictions, recurring workflows → skill proposals, hypotheses, future simulations, error review, experiments, morning briefing) — NEVER executes; the review queue.
14. **healthd**: process availability, model latency, memory, storage, network, tool failures, sensor quality, auth failures, queue backlog, error rates, hallucination indicators, repeated denials → HEALTHY/DEGRADED/LIMITED/SAFE_MODE/OFFLINE. Critical-dependency failure = REDUCE capability, never improvise.

## The event bus
- All services communicate via a TYPED event bus — no direct uncontrolled agent-to-agent execution. Every event: event_id, event_type, source_service, destination_service, timestamp, payload, confidence, sensitivity, user_authorization, correlation_id, expiration, audit_required. Sensitive = encrypted · expired when irrelevant · duplicates detected+suppressed.

## The action-control pipeline (no stage silently skipped)
Observation → Interpretation → World-model update → Proposed plan → Risk classification → Permission evaluation → Human confirmation (when required) → Safety authorization → Execution → Result verification → Audit log → Outcome review.

## The safety envelope
- Every tool/device: permitted_recipients, permitted_hours, maximum_messages_per_day, prohibited_content, confirmation_required, emergency_override, audit_level. Physical/clinical: maximum actuation limit, min/max values, timeout, dead-man control, manual override, sensor-disagreement response, comms-loss response, emergency shutdown.

## Fail-safe behavior
- Lost confidence/authorization/comms/health → stop new high-risk actions · preserve the safe state · notify the user · record the reason · no uncontrolled retries · request human intervention · resume only after validation. A degraded Hermes becomes LESS autonomous, never more.

## The validation ladder
1. **Simulation before deployment**: unit → integration → regression → adversarial → permission → prompt-injection → privacy → failure-mode → simulated-user → rollback testing (+ domain-specific for clinical/physical). 2. **Shadow mode**: observes real inputs, proposes, never executes, compares with human actions, records disagreements, measures FP/FN, identifies unsafe recommendations — promote only after the criteria pass. 3. **Replay testing**: historical events through updated models (protected data, preserved order, old-vs-new comparisons, regression detection, no production transmission). 4. **Release channels**: stable / staging / nightly / experimental — experimental agents NEVER control production clinical/financial/legal/security/vehicle/physical systems.

## Human attention requirement
- Safety-critical tasks require verified active supervision (explicit confirmation · periodic acknowledgment · presence detection · session timeout · reauthentication · manual-control availability). Absence → reduce capability or disengage safely.

## Immutable governance
- NEVER autonomously modify: the safety controller, permission thresholds, clinical restrictions, financial limits, privacy policies, audit records, identity controls, emergency rules, human-override mechanisms. Changes = documented proposal → security review → domain review → human approval → testing → version control → rollback plan → staged deployment.

## The core principle
**Hermes intelligence may be probabilistic. Hermes safety must be deterministic wherever technically possible. The language model proposes. The safety controller decides whether execution is permitted. The human remains the final authority.**
