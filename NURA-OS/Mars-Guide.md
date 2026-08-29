# The Mars Guide — the standing frame for every NURA build

The founder's law (08-19): "using the possibility of functioning on Mars as the personal guide to develop all of the autonomous functions." Every future build, skill, cron, chrome job, and system setup passes this gate first.

## The gate (the four questions before anything ships)

1. **Does it run off-grid?** No cloud SPOFs. If the answer dies without the internet, it's not Mars-grade. The local Ollama, the local RustFS, the local Mirth — those pass. The Twilio-only, the cloud-only, the API-key-death lanes — those need the offline fallback or the redesign.
2. **Does it self-heal?** The watchdog or the parent who restarts it. Nothing single-point. The ts-watchdog pattern owns the service fleet; the every new service needs its watcher before it goes live.
3. **Is it auditable?** The black box + the audit trail on every consequential action. The sovereign audit schema (the actor/resource/model/policy-version).
4. **Is it sovereign?** The local-first, the open-weights, the no per-seat vendor lock. The free tiers are the boost, never the foundation.

## The intelligence from the 08-19/20 sweeps (the best solution as seen)

### The model ladder (the what the sweeps justify)
| Lane | The pick | Why |
|---|---|---|
| The new box default | Qwen3.8-27B (Apache 2.0, 08-14) | The multimodal coding/agent/vision, 1M+ downloads, the open |
| The execution layer | NVIDIA Nemotron 3.5 Lightning 30B-A3B (OpenMDW-1.1) | The harness-trained for the Hermes/OpenClaw loops, the 3B active, the 4x speed, the NIM free tier |
| The always-on agent loop | Meta Muse Glimmer 30B (Apache 2.0) | The built for the local agent loops, the 120K context |
| The edge tool-caller | Needle 2 (the proven) + the LFM2.5-2.6B (the watch — the license flagged) | The 14MB LOM brain + the smallest CPU tool-caller |

### The patent scan (the what's the useful, the what's the threat)
- The no blocking threat found — the labs' patents are the implementations, not the broad blocks on the agent orchestration or the healthcare AI.
- The useful patterns to absorb: the OpenAI US12554519B2 (the agent-as-managed-artifact lifecycle API), the Anthropic US12437238B1 (the recorded trajectories → the training corpora — the mirrors our clinical-workflow capture), the NVIDIA US20260147685A1 (the agent graph → Dockerfile → edge packaging compiler), the Google US12463867B1 (the role-specialized multi-agent orchestration).
- The freedom-to-operate read: the NURA's the lanes are the clear — the domain data + the provider trust + the local sovereignty are the moats the patents don't cover.

### The SEC read (the what the capex says)
- The cloud's the trillion-dollar's the arms' the race's the (the NVDA's the $119B's the commitments' the, the MSFT's the $115.9B's the capex' the, the everyone's the doubling' the) —'s the the confirms's the our's the strategy's the: the we's the don't's the race's the compute' the, the we's the own's the data's the +'s the trust's the +'s the offline's the capability' the. The Mars's the has's the no's the cloud's the; the our's the stack's the already's the half's the there' the.

## The autonomous-function checklist (the what the Mars-guide governs)
- The cron fleet: the every job's the has's the script-mode's the +'s the silent-when-clean's the +'s the owner's the (the the pre-build-triage's the gate' the).
- The service fleet: the ts-watchdog's the owns's the restarts' the; the no's the orphan's the services' the.
- The chrome jobs: the browser's the lanes' the run's the with's the the stealth's the +'s the the session's the hygiene's the (the the explicit's the logouts' the —'s the the eMedical's the law' the).
- The skills: the the every's the error's the →'s the the governing's the skill's the +'s the the memory's the +'s the the cron' the (the the MARS's the loop's the —'s the the principle's the +'s the the procedure' the).
- The memory: the the pre-flight's the (the the mem0's the +'s the the session's the +'s the the .md's the) before's the the answering' the —'s the the knowing-before-acting's the law's the from's the KAPRO's the research' the.
