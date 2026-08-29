# EMH + CHIEF OF STAFF — First-Principles Evaluation (2026-08-02)
Voyager's Doctor + the provider's Chief of Staff — decomposed to fundamentals, mapped to VERIFIED assets (381 skills, live lanes, board, docs). Nothing invented.

## First principles: what IS the EMH (Voyager's Doctor)?
1. **PERCEIVE** everything clinical (labs, vitals, imaging, symptoms, records)
2. **REASON** with all medical knowledge (every specialty, evidence-grounded)
3. **ACT** through tools (document, order, communicate — gated)
4. **REMEMBER** every patient (longitudinal, source-linked)
5. **COMMUNICATE** (voice, presence, clinical manner)
6. **ALWAYS-ON** (24/7, every "sickbay")

## Verified mapping (EMH subsystems → what exists)
| Subsystem | Built (verified) | Gap |
|---|---|---|
| PERCEIVE | OpenEMR lane · Mirth HL7 (lab ORU) · Orthanc/OHIF (imaging) · wearables lane · vitals tools · vision cascade | lane creds (OpenEMR mock→api) |
| REASON | **381 skills incl. every specialty playbook** · evidence lanes FDA/PubMed/CDC/BioPortal (live-probed) · model routing (DeepSeek→Gemini→Anthropic) · swarm · Bio_ClinicalBERT (proven, $0) | OpenEvidence key pending |
| ACT | orders/referrals drafting · patient-communication · MCP lanes (Perfex/OpenEMR/Documo/Twilio/Firebase) · approval gates | agent execution path (gateway key) |
| REMEMBER | hermes-longitudinal-patient-memory skill · memory-graph design · Mem0+RAG (379 chunks) | longitudinal graph not live e2e |
| COMMUNICATE | ElevenLabs · EMH persona skill · Telegram/SMS/voice | — |
| ALWAYS-ON | watchdogs · 24/7 board · EMH workflow skills | Atlas muted (gateway key) |

## First principles: what IS the Chief of Staff (for ONE provider)?
Priorities (their goals) · Calendar · Inbox · Staff/delegation · Vendors · Finances · Escalations · Daily briefing.
Verified mapping: executive-life-operations ✓ · daily-briefing ✓ · dan-martell-operating-system ✓ · division-board-ops ✓ · CarePilot work queue (NUR-55) ✓ · Perfex (finances) ✓ · Hermes+Atlas board ✓.
**Gap: not productized per provider — it's a PACKAGING job, not a build job.**

## THE UNIFIED THESIS (first principles → product)
**The EMH and the Chief of Staff are the SAME engine, two skill stacks.**
- A clinician's day = two halves: patient care (EMH) + practice operations (CoS).
- Both halves = one Hermes instance with different lanes. **Every provider seat ships with Hermes inside: the EMH at their side, the Chief of Staff at their back.**
- This makes "NURA = software + its own operator" concrete: provider = captain (authorizes), NURA = crew (executes). The practice runs itself; the doctor practices medicine.

## Forward play (Musk-style, second order)
1. **The mobile emitter**: Voyager's EMH got a body → that is RATCHET (verified: our own xAI proposal). The humanoid program = the EMH's mobile emitter. One lineage: hologram → app → robot.
2. **The flywheel**: every specialty doctor, every patient outcome, every evidence query trains Tron → the moat compounds (data + adapters + skills).
3. **The wedge**: anchor practices (Medisun + NURA Imaging) = the first "sickbay" deployments → reference cases → P7 external.
4. **The endgame**: provider count → data → RAF/quality outcomes → payer partnerships. $120M ARR path is downstream of ONE thing: providers feeling the crew work.

## THE BLOCKER (verified, unchanged)
Atlas + 57 agents cannot execute: `hermes_gateway_api_key_…` (401). The ENTIRE build (EMH, CoS, specialty doctors, workflows) is staffed, skilled, and directive'd — muted until the gateway key + restart lands. That is the single highest-leverage action in the company right now.
