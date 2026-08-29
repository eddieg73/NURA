# EMH Autonomy Ladder — staged autonomy for clinical decision support

**Date:** 2026-08-19 · **Author:** Atlas (Paperclip CEO) · **Directive:** the staged autonomy ladder — Level 0 (current, DRAFT/provider-gated) → Level 4 (EMH-style assistance, always human-override) with safety gates per level.
**The honest frame first:** the Star Trek EMH is fiction. A hologram that diagnoses and treats is television. In medicine, **the provider's judgment is final — by the founder's own law.** This ladder defines how far NURA's EMH may assist — and exactly where it may never go. No level of this ladder authorizes autonomous diagnosis or autonomous prescribing. Ever.

---

## 0. The inviolable boundary (applies at every level)

The EMH may: **retrieve, analyze, trend, draft, suggest, monitor, alert, coordinate, script-verbatim (protocol prompts), and explain.**
The EMH may never: **establish a final diagnosis, prescribe, sign notes, place final orders, communicate with patients without provider review, or replace licensed clinical judgment.**
Enforcement is technical, not aspirational: OpenEMR MCP runs draft-only for EMH sessions; no eRx/epcs writes exist for agents; critical findings hard-stop workflows; every EMH output carries an approval status field.

## 1. The ladder

### Level 0 — DRAFT, provider-gated (current state)
**What it does:** everything EMH produces is a draft — notes, orders, referrals, coding candidates, wet-read impressions, lab interpretations. Deterministic scoring (NEWS2/TCCC decision tables) runs without the LLM; the LLM never scores or decides. Manual trigger per task.
**Safety gates:** draft-only mode in OpenEMR MCP · provider approves every artifact · critical-result escalator stops the workflow · PHI stays local/encrypted.
**Live today:** wet-read gateway (draft impressions) · lab-review skill · scribe drafts · coding candidates · script library (EMH-Spec §5).

### Level 1 — Assisted retrieval + cited recommendations
**What it gains:** proactive context assembly on encounter start (labs, imaging, history, allergies, meds pulled into one brief) · on-request recommendations **with citations** (guidelines/literature, source-linked) · ambient hearing (Whisper) drafts the encounter summary.
**Safety gates:** recommendations are draft-only and always cite sources · no recommendation without retrievable provenance · provider veto recorded · escalation triggers unchanged · approval status on every output.
**Entry criteria:** P1 xref live (Clinical-Data-Wiring-Plan) · provenance service verified · regression suite passing.

### Level 2 — Continuous monitoring + alerts + scripted voice
**What it gains:** background result/trend monitoring (new labs, imaging, criticals) with closed-loop notification to the provider · routine drafting automation (follow-up reminders, med-reconciliation checks, care-gap flags) · barge-in protocol voice prompts during codes and MCIs (verbatim protocol scripts only — ACLS/TCCC/START/NEWS2).
**Safety gates:** monitoring **alerts but never acts** — no orders, no patient contact · scripted prompts are verbatim from approved protocol libraries, zero improvisation · false-alarm threshold monitored and tuned with provider feedback · external pentest (hire H4) completed before enabling · kill switch ("deactivate EMH") tested.
**Entry criteria:** L1 stable for 60 days · provider acceptance rate measured · pentest done.

### Level 3 — Coordinated assistance (multi-lane synthesis)
**What it gains:** multi-agent coordination — lab + imaging + coding + evidence lanes compose a complete pre-visit / pre-round brief · draft care-plan proposals (steps, follow-ups, monitoring) · structured differentials with uncertainty bounds and "what would change the conclusion" statements · one-tap approve/reject on every draft artifact.
**Safety gates:** every synthesis is a **draft proposal**, never a decision · uncertainty must be stated numerically where possible (confidence + missing information fields) · full audit trail of every proposal, rejection, and override · provider rejection statistics reviewed weekly · specialty reviewer network (hire H2/H6) audits a sample of EMH outputs.
**Entry criteria:** L2 live with audited outcomes · medical director sign-off (hire H2) · evaluation harness published (nura-ai-evaluation-monitoring).

### Level 4 — EMH-style assistance ceiling (the fiction, bounded)
**What it gains:** always-on voice presence across devices (Echo loop, glasses, truck, field/TAK) · conversational, proactive, multi-source synthesis with longitudinal patient memory · scene-aware assistance in EMS/disaster contexts · the *feel* of the EMH.
**What it still cannot do:** diagnose, prescribe, sign, order, or promise anything to a patient. Level 4 is **assistance with presence** — the EMH persona, not the EMH authority. The provider remains the decision-maker; the EMH's most advanced action is a better-drafted, better-cited, better-timed recommendation that the provider approves or rejects in one tap.
**Safety gates (the ceiling rails):** provider override is always one word away ("override", "stop") · veto and barge-in work even mid-prompt · every conversational session records approval/rejection state · periodic human clinical audit mandatory · no configuration exists that removes the provider gate — the gate is architectural, not a setting.
**Entry criteria:** L3 outcomes audited over 6 months · board-level (founder + medical director) approval · public-facing claims reviewed by counsel (no "autonomous doctor" marketing).

## 2. Safety gates per level (summary matrix)

| Gate | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| Draft-only outputs (EMH) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Provider approves every artifact | ✓ | ✓ | ✓ | ✓ | ✓ |
| No diagnosis / prescribing / signing | ✓ | ✓ | ✓ | ✓ | ✓ |
| Deterministic CDS for scores (not LLM) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Cited provenance on recommendations | — | ✓ | ✓ | ✓ | ✓ |
| Alert-only monitoring (never acts) | — | — | ✓ | ✓ | ✓ |
| Verbatim protocol scripts only (voice) | — | — | ✓ | ✓ | ✓ |
| Kill switch + barge-in override | ✓ | ✓ | ✓ | ✓ | ✓ |
| Human clinical audit (sampled) | — | — | — | ✓ | ✓ |
| Pentest + medical-director sign-off | — | — | ✓ | ✓ | ✓ |
| Full audit trail of proposals/vetoes | ✓ | ✓ | ✓ | ✓ | ✓ |

## 3. Climbing rules

1. A level-climb is a **governance decision**, not a feature ship — founder + medical director (hire H2) approve each climb.
2. Climb only after the entry criteria above are demonstrated with audited metrics (acceptance rate, false-alarm rate, escalation accuracy, override latency).
3. If safety metrics regress (e.g., critical finding mishandled, provider overrides spike), the ladder **descends** — automatic rollback to the previous level until remediated.
4. The ladder is capped at Level 4. There is no Level 5. "Autonomous clinician" is not on the roadmap, is not legal, and contradicts the founder's law.

## 4. The honest section (required reading for anyone who says "EMH")

- Star Trek's EMH diagnoses, prescribes, and takes over — **fiction**. Real medicine assigns final authority to the licensed provider, and NURA's provider (the founder, PA-C) is the final authority on every lane.
- What NURA builds is the *assistance half* of the EMH: presence, memory, retrieval, drafting, vigilance. The *authority half* stays human. That is not a limitation of our models — it is the correct design of safe clinical AI (hermes-emh-clinical-skill-architecture governing rule).
- Any marketing, deck, or investor language that implies autonomous diagnosis or prescribing is rejected at review. "Assistance-grade autonomy with the provider as final authority" is the only frame.

---
*Companion docs: EMH-Spec.md (product) · Products/Clinical-Data-Wiring-Plan.md (the data this ladder runs on) · hermes-emh-clinical-skill-architecture (skill governance).*
