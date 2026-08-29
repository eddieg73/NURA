# HERMES SKILL ECOSYSTEM — EFFICIENCY MAP (2026-08-06, founder directive: "all of them, map how it works most efficiently")

**The four installed: awesome-hermes-agent (the catalog) · obsidian-skills (the vault lane) · hermes-agent-self-evolution (the evolution engine) · MemOS (the memory research). The map = how they wire together for the MOST efficient operation.**

## THE ARCHITECTURE (the data-flow)
```
┌─────────────────────────────────────────────────────────────┐
│ 1. THE CATALOG (awesome-hermes-agent ★5.2K)                  │
│    → the discovery layer: every skill/plugin/provider indexed │
│    → the monthly review: catalog → the curation pass → the    │
│      install-queue (the url-integration-review skill!)        │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. THE SKILL LIBRARY (~/.hermes/skills — 250+ live)          │
│    ← the obsidian-skills (★44K): the vault-CLI skills — the  │
│      vault-lane upgrade (the vault ops become agent-native!) │
│    ← the third-party imports (the npx/hermes mcp catalog!)   │
│    → the P&P manual (every skill = policy + procedure!)      │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. THE EVOLUTION ENGINE (hermes-agent-self-evolution ★4.9K)  │
│    → the GEPA loop: execution-traces → the skill-optimization │
│    → the dojo's overnight improvements (accept-if-score-up!) │
│    → the failure doctrine: every fixed error → the skill      │
└────────────────────────────┬────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. THE MEMORY LAYER (MemOS ★10K — research)                  │
│    → the self-evolving memory patterns (the study-lane!)     │
│    → the current stack stays: Redis (working) · Qdrant       │
│      (associative) · postgres (relational) · vault (durable) │
│    → the MemOS patterns = the future-memory upgrades         │
└─────────────────────────────────────────────────────────────┘
```

## THE EFFICIENCY PRINCIPLES (how it all works best)
1. **The catalog feeds the library, never the reverse** — the discovery happens ONCE (monthly), the installs happen in BATCHES (never one-at-a-time!)
2. **The evolution engine owns the quality** — the GEPA + the dojo patch the skills; the human reviews the deltas (the <5%-improvement = the flag!)
3. **The vault is the shared brain** — the obsidian-skills make the vault agent-native: the same files the agents work are the files the humans read (the zero-duplication!)
4. **The memory stays layered** — the hot facts in Redis · the semantic in Qdrant · the truth in postgres · the durable in the vault — each layer does its ONE job (the MemOS-patterns = the future upgrade, never a rewrite!)
5. **The watchdogs close the loop** — the error-watchdog (hourly!) · the health-watchdog (5m!) · the drift-audit (weekly!) · the self-reflection (daily!) — the machine audits itself, the alerts land only on the NEW.

## THE INTEGRATION POINTS (the concrete wiring)
| Component | Integrates with | The efficiency gain |
|---|---|---|
| awesome-hermes-agent | the url-integration-review + the monthly curation | the discovery→install pipeline in one pass |
| obsidian-skills | the vault + the vault-shared-memory skill | the cross-agent brain goes agent-native |
| hermes-agent-self-evolution | the hermes-dojo + the GEPA | the overnight self-improvement, measured |
| MemOS | the memory-hygiene + the Qdrant/Redis doctrine | the memory-upgrade research, gated |

## THE CADENCE (the efficient operating rhythm)
- **Monthly**: the catalog review (awesome-hermes-agent → the curation pass → the batch-installs!)
- **Weekly**: the drift-audit + the URL-review (the ecosystem-changes!)
- **Nightly**: the dojo + the self-evolution (the GEPA-improvements!)
- **Daily**: the self-reflection + the error-watchdog (the silent maintenance!)
- **The rule: the ecosystem work happens in the scheduled passes, never in the interactive flow — the founder's sessions stay for the decisions, the machine does the maintenance.**
