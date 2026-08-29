# Why We Do Things — NURA Doctrine (2026-08-02)

The reasons behind the operating rules. If a decision looks odd, this page explains it.

## 1. One master agnostic app (the PRIME DIRECTIVE)
Providers shouldn't care which EMR they run. ONE NURA app interfaces with ALL EMRs (Epic/Cerner/eCW/Athena/OpenEMR/eMedical) via FHIR R4 + SMART + HL7 v2 adapters. RIS/PACS is a BUNDLE module, not a capital business. Why: the market converged on one-AI-layer (Abridge/DAX validated the category); we win on price ($100-150 vs $400-800), on the operator (Hermes baked in — nobody else ships it), and on born-agnostic adapters.

## 2. Hermes ALWAYS baked into the SaaS
Every customer deployment ships the agent platform (57-agent org). Provider = captain, NURA = crew. Why: the moat isn't the scribe — it's the practice that runs itself.

## 3. Everything goes in Obsidian; secrets never do
The vault = durable knowledge surface (feeds RAG — 540 chunks). EXCEPTION: live credentials live ONLY in .env 0600. Why: the vault is indexed into vector memory — a secret in the vault is a permanent leak. Notion = target store, gated on page-share.

## 4. Verify before declare (no bullshit)
Every "connected" claim requires live probe output. Untested = labeled untested. Why: this session proved it — Twilio tokens 401'd across 8 combinations; lanes probed before wired. Trust is built on receipts.

## 5. Free-first, quality-gated
Free lanes first (OpenRouter :free, HF inference $0) → DeepSeek (default) → Gemini → Anthropic only when needed. ~$9 cap. Why: the product must survive without burning capital; quality gate prevents free-lane garbage.

## 6. Failure doctrine
Every fixed error → memory + skill + cron if recurring (twice = FAIL). Why: compounding learning is the product. The AGI-loop skills (uncertainty evaluator, memory-graph synthesis) formalize this.

## 7. Approval gates
Reversible dev = auto. Production deploys, external communications, financial actions, patient mutations = authorization. Fail closed. Why: consequential actions need the human; the operator charter gives autonomy within the guardrails.

## 8. Org routing: Atlas owns org moves
Hire/strategy/launch route via the Paperclip CEO; specialists implement underneath. Why: one accountable brain per domain; the board is the decision surface (NUR-80/85/89 pattern).

## 9. Trading: the method, not the story
FXAlexG's Set & Forget = sound swing-trading craft (multi-TF confluence, 1% risk) — we adopted the METHOD; his income story is courses (Coffeezilla-verified). $1,000 account = learning with 1% hard cap; paper before live; board approves every phase. Why: discipline is the only edge that survives.

## 10. Content: educational, evidence-linked, compliant
Peptide/supplement content = educational framing + PubMed/openFDA citations + PA review + marketing-claims gate. Why: credibility is the brand; one bad claim kills the trust the whole platform builds.

## 11. Don't replicate
Dify? No (we built it all). NotebookLM? No public API (DIY RAG + voice). Duplicated skills get consolidated (11 deleted this session). Why: one brain, one writer, lean stack — every addition must clear the redundancy test.
