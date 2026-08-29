# NURA Engineering — Performance Audit & Sovereign LLM Lane (Aug 23, 2026)

> **Doc index** — one page tying the performance audit and the free-first sovereign LLM decision together. Source of truth: Obsidian vault. Mirrors: GitHub `docs/` + Notion.

## TL;DR

Two engineering deliverables landed today, both free-first:

1. **Performance audit** of the `eddieg73/NURA` monorepo → `PERFORMANCE_AUDIT.md` + `PERFORMANCE_PLAN.md`. All actionable hotspots are in the **mesh-monitor SQLite hot path** (D-1..D-4). Verified: an unindexed latest-position query, an in-memory CSV export, connection-per-query, unbounded reads. The Flutter app and ORION backend had no real perf defects (mostly scaffolded).
2. **Sovereign LLM lane decision** — the free-first pecking order for AI inference in workflows. **Chosen: Ollama `med42` over the WireGuard mesh (`10.10.0.2:11434`) as the local clinical expert.** Colibrì remains the sovereign *emergency* fallback, not the daily driver.

## Why the sovereign LLM lane (free-first, pecking order)

The user directive: *"set a pecking order free when possible and then out for help."* Applied to LLM inference in n8n workflows:

| Rank | Lane | Model | Cost | Verdict |
|------|------|-------|------|---------|
| 1 | Ollama over mesh (`10.10.0.2:11434`) | **med42** (clinical), qwen3:8b, deepseek-r1:8b | $0, local | ✅ **Chosen** — reachable, loaded, clinical-specialist |
| 2 | Colibrì (`127.0.0.1:8000`, 35B MoE) | qwen3.6-35b | $0, local | ⚠️ **Fallback only** — slow (~0.3–1 tok/s), not clinical-tuned, bound to loopback |
| 3 | Cloud (DeepSeek/OpenAI) | — | paid | ❌ Last resort per NO-MONEY doctrine |

**Evidence the chosen lane works** (live test, 2026-08-23, HTTP 200):
```
Q: Top 2 differential diagnoses for acute chest pain in a 62yo diabetic smoker
med42: 1. Acute myocardial infarction (AMI) due to coronary artery disease, exacerbated by
       diabetes and smoking.
       2. Aortic dissection or rupture, particularly considering the patient's age and
       smoking history, which can contribute to atherosclerosis and aneurysm formation.
```

## Network topology (the wiring reality)

- n8n runs as Docker container `n8n-n8nwithpostgres-a9xuj2-n8n-1` on Lab node `72.60.163.140` (n8n 2.11.4).
- n8n **container** reaches the Lab's Ollama over the WireGuard mesh at `10.10.0.2:11434` — verified (models list + "Ollama is running" from inside the container).
- **Colibrì binds `127.0.0.1:8000` on the Lab host** — NOT reachable from the n8n container without rebinding to `0.0.0.0`. That's an approval-gated production change; keep Colibrì as Hermes' sovereign fallback instead.
- Existing n8n credential `ollamaApi` ("Ollama account", id `oVRt8MYvbyruJHZq`) already targets the mesh. The CLIN/PHYS/ASC/AUTONOMY workflows are **scaffolded placeholders** — their `chainLlm` nodes have **no model sub-node connected**, which is why they sit INACTIVE and would throw "A Model sub-node must be connected."

## Testing honest note

The lane works at the Ollama layer (proven). The n8n **wrapper** integration hit a node-version `httpRequest` gating quirk in this n8n build (2.11.4) — the code-node body built correctly but the request aborted on the outbound path. The correct production fix is to register the mesh endpoint as an n8n **credential** (Ollama lane) and attach it to a *properly-wired* langchain sub-node graph — not to force it through a raw httpRequest. This is documented as the next implementation step, not a blocker (the LLM itself is verified working).

## Related
- `docs/PERFORMANCE_AUDIT.md` — full audit (evidence, findings, prioritized table)
- `docs/PERFORMANCE_PLAN.md` — phased plan + approval gate
- `NURA-OS/Engineering/PERFORMANCE-AUDIT-and-Sovereign-LLM-Lane.md` — this index
- Colibrì: `NURA-OS/sovereign-inference-fleet` skill + `references/colibri-hummingbird-setup.md`
