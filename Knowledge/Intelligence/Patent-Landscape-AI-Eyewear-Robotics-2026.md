# Patent Landscape & Whitespace Map — AI + Eyewear/Optics + Surgical Robotics (2026)

**Purpose:** competitive intelligence + design-around + whitespace discovery for NURA capability capture.
**Rule (non-negotiable):** read to understand the *state of the art*, find the *gaps*, and design our **original** solution in the open whitespace. Do NOT reproduce a claimed method. Any proximity/FTO question → LEXA/Atty Stavrou. Data = public patent publications (Patsnap, WIPO, IFI, ipCapital, Google Patents, USPTO Gazette).

---

## LANE 1 — AI / LLM / Agentic (the substrate)
**Landscape (real numbers):**
- LLM field: **19,964 patent families**, growth stage (no plateau). Filings: 393 (2021) → 771 → 3,657 → **8,559 (2024)**; 2025-26 understated by 18-mo publication lag.
- Top-5 filers = only **26%** of the 100 largest → open, multi-player field, NOT a monopoly. A focused entrant can take a defensible niche.
- Leaders by volume: **Microsoft** 1,320 fam (NLP/neural, 9.6× momentum) · **Google** 1,186 (34× momentum, more AI-architecture) · Tencent 800 · Baidu 677 · Alipay 538. Fast risers: Qualcomm, NVIDIA, Intuit, DeepMind (11×), GDM (15×).
- Global GenAI: **56,000+ new families in 2024-25** (> prior decade combined). GenAI = 8.7% of all AI patents. **LLMs now out-file GANs ~3:1** (14,100 vs 5,245 in 2025); diffusion 3rd. SoftBank = largest single GenAI holder (~3,000, mostly 2025).
- **Agentic AI:** 3,146 families since 2019; nearly **tripled in 12 months** (2025=1,109). Moat-builders are NOT the labs: Oracle (93), May Mobility (109), Gatik (82), State Grid/China (72), Morgan Stanley (31), Citigroup (25), ABB, IBM, Salesforce, Microsoft, Intel. OpenAI/Anthropic/Mistral **<10 published each** (publication lag only — will surface 2026-27). China 59.2% / US 21.1%.

**Whitespace map (where we can claim):**
1. **Agent memory / long-horizon state** — "lighter coverage than the others; a relative opportunity." → NURA's multi-session clinical context is literally this.
2. **The integration layer — the big one.** Domain-specific agent applications (healthcare intake, compliance, claims, care-gap) are filed **in isolation by operators but rarely cross-claimed against the underlying agent architecture.** Stated directly: *"If your invention sits at the integration point and you can claim both the technical method AND the domain-specific application, you have a defensible position."* → This is NURA's entire model (agent architecture × clinical application).
3. **G16H (healthcare informatics) LLM IP is UNDER-SERVED** — <900 records in a 19,964-family LLM corpus; healthcare-specific LLM IP not yet filed at scale (regulatory caution). Best-positioned entrants = those with **medical-device/health-IT portfolios + clinical validation data**. → NURA has both.
4. US active surface for an agentic claim ≈ **900–1,000 refs** (665 US + 120 PCT + CN/EP inbound), not the global 3,146 — far smaller to design around if we operate US-only.
- Watch: Oracle/Morgan Stanley agent-orchestration cluster; Chinese universities/Zhejiang/Tsinghua/Peking as license/acquire vector.

**Design-around notes:** generic orchestration/tool-calling/multi-agent coordination are HEAVILY filed (Microsoft/Oracle/Salesforce/Intel/Citi). Avoid re-claiming those; claim the clinical-integration + memory + safety-gating layer instead.

---

## LANE 2 — Smart glasses / AR eyewear (Ray-Ban Meta, Oakley Meta)
**Meta claims (recent):**
- **Object disambiguation** (filed 11-26-25, pub 05-28-26): confidence-score loop — if the intended object is ambiguous, show candidate-object menu for the user to pick. Graceful fallback when vision AI is uncertain.
- **AR overlay filtering / object-augment gating** (filed 12-04-25, pub 06-04-26): decide WHICH digital overlays to show, weighted by presentation conditions (proximity/time/context/publisher) + suppression. The "invisible plumbing" of useful AR.
- **In-plane eye tracking** (US 2026/0236094 A1): eye-tracker built flat inside the lens — side-firing LEDs, split corrective assembly (ambient vs tracking light path), glint-based gaze, mirror to kill double-glints. **Claim 1 is broad** (any near-eye display w/ in-plane illuminator + split corrective assembly + glint gaze). ⚠️ FTO material for any glasses-form AR competitor.
- Granted: US 12,493,191 B2 (multi-directional waveguide eye tracking) · US 12,339,454 B2 (waveguide VBG to mitigate rainbow) · US 12,379,614 (waveguide + reflector → brighter image, reduces what bystanders see).
- Oakley Meta (EssilorLuxottica + Meta): **performance AI glasses for athletes**; wearable form factor; Meta Neural Band (EMG wrist control).

**Whitespace / design-around for NURA:**
- The *optics/hardware* layer (waveguide, eye-tracking, in-lens display) is **heavily fenced by Meta** — do NOT build that HW; design around or use interoperable/third-party displays.
- The **domain software layer** is open: a **provider/clinician-wearable software suite** (hands-free ambient documentation, live medical translation, clinical decision HUD, care-workflow context) — Meta is claiming consumer UX, not clinical/regulatory application. That's our lane: **clinical AR software integration**, not optics.
- "Ambiguity fallback + overlay prioritization/suppression" = strong UX patterns we should *reimplement originally* for clinical use (e.g., show only relevant patient/decision overlays, gate by clinical context).
- Live-caption/translation, camera + AI assistant, neural-band gesture control — feature reference set; build our own version for clinical workflows.

---

## LANE 3 — Surgical robotics (Intuitive Surgical / da Vinci)
**Intuitive claims (dense):** Intuitive is a top filer (2,739–2,818 families in scope). Claims span:
- **Patient-Health-Record-based instrument control + safety-mode transition** (US 2025-0017673): track instrument actuator state; on reaching a prescribed state given the patient's HR/stage, auto-transition to a **safety mode** (AI/rule-based risk).
- Registration for image-guided surgery (ICP, shape sensors, bronchial centerline); registration via reduced search space (snap instrument point to a linked-cylinder bronchial model); motor interface for parallel offset drive shafts; association processes for manipulator pairing.

**Whitespace / strategic read for NURA:**
- We are NOT building surgical mechatronics (that's an Intuitive/medical-device arms race). Don't touch the servo/actuator/end-effector claims.
- The **convergence signal** is the key: Intuitive is wiring **robotic control + patient health records + AI risk/safety mode** together. The future surgical stack = robot (hardware) × AI decision layer × EHR/clinical intelligence. **The AI + EHR + orchestration layer is where NURA plays** — via vendor APIs alongside such robots, not by copying their hardware.
- NURA's real position in this lane = **clinical decision support / surgical-workflow planning / intra-procedure risk-flagging** built on FHIR + real-time streaming, reimplemented originally.

---

## CROSS-CUTTING — THE MOAT (what "best product" actually looks like)
The patent data says our defensible position is at the **clinical-integration + agent-memory + safety-gating layer**, not in hardware or generic orchestration:
1. **Claim BOTH the technical method AND the domain (clinical) application** — that's the under-filed integration point.
2. **Agent memory / long-horizon state** — under-claimed, and it's our multi-session clinical context.
3. **G16H / healthcare-informatic AI IP** — under-served; NURA has a health-IT portfolio + clinical validation data = the best-positioned entrant.
4. **Safety-gating / provider-audit layer** — the trust boundary; aligns with our RBAC-3-tier + provider-approval doctrine.

**Hard rule:** reproduce nothing (no method/claim copy). Build original in the whitespace above. Route every "is this too close?" to LEXA/Atty Stavrou. This is capability capture via *design-around + whitespace*, not extraction.
