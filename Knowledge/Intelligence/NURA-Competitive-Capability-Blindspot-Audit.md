# NURA Competitive-Capability & Blind-Spot Audit (2026)

**Directive:** read the field, learn how the leaders differ, absorb the *principles*, and identify what NURA is missing.
**The one rule that makes this safe:** we take **ideas, methodology, and permissive-licensed code** — never a competitor's proprietary implementation. Everything below is what we legally absorb + the gaps we close with **original engineering.**

---

## 1. How each leader does it DIFFERENTLY (the lessons)

### AI / Agents (Microsoft, Google, Nvidia, Oracle, banks)
- **Microsoft** = *application-layer* weighting (NLP G06F40 + neural G06N3) → they patent the *product integration*, not just the model. Lesson: tie the method to the business use-case.
- **Google** = *model/architecture*-heavy (G06N3), 34× momentum → they invest in the foundation itself. Lesson: don't fight on foundation (we won't), fight on integration.
- **Nvidia** = *image/video + agent platform* — the perception-to-action bridge. Lesson: the multimodal perception + agent-action coupling is valuable.
- **Oracle / Morgan Stanley / Citigroup** = *enterprise orchestration + tool-calling + multi-agent coordination* — the operational layer, not research. Lesson: **enterprise/workflow value is where the defensible claims live**, and they file fast.
- **OpenAI/Anthropic/Mistral** = few published families (18-mo lag) → they haven't fenced the *integration* yet. Lesson: **the window to file at the integration layer is open NOW.**

### Smart glasses / AR (Meta, EssilorLuxottica/Oakley)
- Meta = consumer-UX + **optics** (waveguide, in-plane eye tracking, overlay gating). They solve *ambiguity* and *overload*: (a) graceful object-disambiguation fallback, (b) **presentation-condition gating** (show overlays only when relevant), (c) thin-form optics fenced broadly. Lesson: the UX principles (uncertainty fallback, relevance gating, hands-free) transfer; the optics do NOT (FTO).
- Oakley Meta = *performance/athlete* form factor + EMG wrist control (Neural Band). Lesson: **domain-specific form factor + hands-free control** — a clinical provider variant is the open twist.

### Surgical robotics (Intuitive / da Vinci)
- Intuitive = **mechatronics** (drive shafts, wrist/cable actuation, registration) + the emerging **patient-record-based safety-mode**. They're already fusing robot × EHR × AI-risk. Lesson: the hardware is fenced; the **AI × EHR × safety** layer is the convergence seam NURA owns.

---

## 2. Principles we legally absorb (ideas, not code)
1. **Claim the method AND the domain** — the under-filed integration seam. (→ our clinical agent architecture.)
2. **Graceful uncertainty fallback** — when the AI isn't sure, ask/clarify rather than guess. (→ clinical disambiguation, provider confirmation.)
3. **Relevance-gated presentation** — show only what's contextually valid now, suppress the rest. (→ decision HUD, care-gap surfacing.)
4. **Safety-gating on state + record** — transition to a safe mode based on record/stage/risk. (→ our NEWS2/safety + provider-gate doctrine.)
5. **Agent memory / long-horizon state** — the under-claimed asset. (→ our multi-session clinical context.)
6. **Provider-in-the-loop / auditability** — the trust boundary that separates clinical software from consumer AI. (→ item-level approval, black-box logs.)

---

## 3. NURA current capability inventory (what we HAVE)
- **Agent runtime:** Hermes as one interchangeable runtime; 300+ skills; MCP lanes (clinical, GitHub, Hostinger, OpenEMR, Redis, Qdrant, FHIR); OpenRouter/sovereign-Ollama model tiers; LLM routing + MoE.
- **Clinical:** NURA Clinical OS (5-tab, RBAC-3-tier), clinical synthesis pipeline (radiology+labs+consults→impression+differential), OpenEMR FHIR truth, Mirth/OIE integration, Medplum, device telemetry CDS (NEWS2), RATCHET + RCM, population-health (CarePilot/Solis RAF/HCC).
- **Data/memory:** Obsidian vault = memory authority; Qdrant/Redis/Postgres state; B2 durable; agentic memory graph.
- **Automation:** 87 standing crons (self-improvement, incident-commander, drift-audit, autonomy-audit, self-heal, evolution-review, competitive-watch) — a real self-improvement loop already runs.
- **Embodied/robotics lane:** openpilot, drones, OMI wearable, ESP32 mesh, radiology AI, imaging/RIS-PACS.

---

## 4. BLIND-SPOT MATRIX (ranked gaps)
| # | Blind spot | Why it matters | Severity |
|---|---|---|---|
| B1 | **Cross-domain agent memory (long-horizon)** — durable synthesis across sessions/encounters | Under-claimed in the field; it's our differentiator but only loosely wired (vault vs Qdrant vs Hermes event-references are not unified). | 🔴 High |
| B2 | **Clinical integration-layer IP strategy** (claim method+domain) | We have the data/assets but no filing/FTO posture → risk of letting others fence our lane first. | 🔴 High |
| B3 | **Safety-gating as a first-class, auditable primitive** — auto-SAFE/black-box/MD-alert is piecemeal | This is the regulatory moat; not yet a normalized, testable rule engine. | 🟠 Med-High |
| B4 | **Provider AR / hands-free clinical surface** — no software lane for a glasses-form clinician UX | Meta owns optics/HW; the *clinical software* (ambient doc, live translation, decision HUD, gated overlays) is open and we're absent. | 🟠 Med |
| B5 | **Ambiguity handling + relevance gating in our own UX** — our tools don't yet clarify-or-gate; they output | The two patterns that make real products usable (per Meta). | 🟠 Med |
| B6 | **Competitive whitespace IS alerting** — no automated patent/landscape change monitor | Rivals are tripling yearly; we need signal-on-change, silent-when-clean. | 🟡 Low-Med |
| B7 | **Surgical/robotics AI-decision layer** — we do clinical AI but not the intra-procedure risk/orchestration seam | The convergence is robot×AI×EHR — the only open piece is ours to take. | 🟡 Low-Med |

---

## 5. Original-build roadmap (close the blind spots, all clean-room)
1. **Unify agent memory** (B1): Qdrant (vector) + Postgres (state) + vault (durable human context) + Hermes event-references → one source-linked longitudinal memory graph (per `hermes-longitudinal-patient-memory`).
2. **Stand up clinical-integration IP posture** (B2): keep a live FTO/design-around file per domain; engage LEXA/Atty Stavrou for the "claim method+domain" filing plan on the integration seam.
3. **Build a safety-gating rule engine** (B3): normalize safety-mode transition (state+record+risk) as a tested primitive with black-box logging + provider approval (per RBAC-3-tier).
4. **Provider AR software lane** (B4): architect the hands-free clinical UX as a software product on interoperable displays (not Meta optics) — ambient documentation, live translation, decision HUD, gated overlays.
5. **Add clarify-or-gate UX** (B5): the ambiguity-fallback + relevance-gating patterns, reimplemented for clinical decision surfacing (provider-confirm before commit).
6. **Automate landscape + whitespace monitoring** (B6): a weekly patent/competitor change cron, silent-when-clean, patching this audit.
7. **Seize the robot×AI×EHR seam** (B7): the intra-procedure clinical-decision + risk-orchestration layer, built to integrate via vendor APIs.

---

## 6. How we'll know we're set (verification)
- A testable **longitudinal memory** that survives sessions (memory-graph evidence).
- A **claim-charted** design-around for any patented area we touch (no guesswork).
- A **safety-gate** primitive with passing tests + an audit trace.
- A **whitespace monitor** that alerts on change, silent-when-clean (no_agent).
- Each built original: no proprietary implementation copied; permissive OSS only, with attribution.

*This is capability capture via design-around + whitespace — never extraction.*
