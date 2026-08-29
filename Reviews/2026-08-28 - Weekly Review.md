---
date: 2026-08-28
period-start: 2026-08-24
period-end: 2026-08-28
type: review
tags: [review, weekly]
ai-first: true
---

# Weekly Review - 2026-08-24 to 2026-08-28

## For future agent
Weekly review covering 2026-08-24 through 2026-08-28, generated Friday 2026-08-28 by the obsidian-weekly cron. The week's arc: NURA Master Plan finalized, Medisun first-client scaffolding advanced, IP doctrine codified, the Aero medical drone-delivery division chartered, a UAP/disclosure intelligence sweep, and a persistent LAB-node resource-exhaustion incident. Use this as the baseline for what was true and decided at the end of the period. Infra facts carry an `as of` date where they change fast.

## What I accomplished

- **NURA Master Plan finalized** (class-A, source of truth) - full strategy plus Doximity competitive positioning: *Doximity = the physician's network; NURA = the physician's autonomous OS that owns the record* (`[[NURA-OS/Products/NURA-Master-Plan]]`).
- **Medisun (first client) scaffolding advanced** - integration flow record (56 n8n workflows classified: Memory GET/SET, Booking, ElevenLabs Voice AI, GHL/NMI/PDFMonkey live) plus the Medisun Health Group enterprise-OS spec (6-entity per-TIN/NPI spine; Perfex = non-clinical ops, OpenEMR = clinical truth, eMedical/QBO) - see `[[NURA-OS/Products/Medisun-First-Client-Integration]]` and `[[NURA-OS/Products/Medisun-Health-Group-Enterprise-OS]]`.
- **IP doctrine codified** - NURA-owned public naming, open-source foundations never publicly disclosed, Reg A described by capability not vendor; $0 sovereign lane + EMR-agnostic FHIR interop as the moat (`[[NURA-OS/Strategy/NURA-Competitive-Differentiation-and-IP-Doctrine]]`).
- **Aero medical drone-delivery division chartered** (founder directive, 2026-08-26) - swarm-capable medical payload delivery (antivenom, epi, TXA, blood toward organ transport), launch-from-EMS-vehicle + roof-dock model, mesh/lattice fleet doctrine, BVLOS regulatory gates, MVP with SITL swarm proof first. Companion `[[NURA-OS/Aero/EMS-Drone-Spec]]`; division note `[[NURA-OS/Aero/Medical-Drone-Delivery-Division]]`.
- **UAP/disclosure intelligence sweep** (weekly) - SpaceX week: Ship 40 recovered (Aug 18), Flight 14 ship-catch dropped + launch slipped to ~Sept 15, Starbase Louisiana $100B campus (Aug 25), Artemis III "as early as June 2027". Gap-fill: House adopted Burlison UAPDA as FY2027 NDAA amendment (Jul 22, 216-212). Watch items: Greer deadline Aug 29, ODNI NDA-waiver checkpoint Aug 30, PURSUE still capped at Tranche 5 (`[[NURA-OS/Disclosure-Log]]`, `[[NURA-OS/UAP-Research]]`).
- **Infra/agent-ecosystem work** - agent-platforms sweep (Hermes v0.20.5/v0.20.6, MCP 2026-07-28 stateless spec, OpenRad/Orchid/Merlin/Heimdallr radiology candidates, openpilot 0.11.2), build-queue triage for duplicate cron/script signals (`[[NURA-OS/Infra/Build-Queue-Triage-Log]]`), imaging stack notes (`[[NURA-OS/Imaging/OIE-Mirth-Admin-Fix-2026-08-23]]`, `[[NURA-OS/Imaging/NURA-Radiology-Intelligence-Build-2026-08-23]]`), B2 object-storage state (`[[NURA-OS/Infra/B2-State]]`), and research notes (OSINT techniques, Borg-Assimilation playbook, patent landscape, competitive blindspot audit).
- **Same-pass ops fixes** (evidence-first) - moltbook morning/midday/evening crons fixed (script-arg moved out of the `script` field to bare `moltbook-human-checkin.py`); emos gap audit unblocked (installed `greenlet==3.5.5` cp313 to fix ABI mismatch); `nura-backup.sh` gained `--ignore-failed-read`; `devops/backblaze-b2-storage` skill given name/description frontmatter.
- **Synthesis** - created `[[Knowledge/Synthesis - Agent Memory Consolidation]]`: vault-as-authoritative-semantic-layer thread across the Master Plan, IP doctrine, agent-platforms intel, and the reflection memory plane.

## Key decisions made

- **NURA Master Plan adopted as class-A source of truth** (2026-08-27) - locks the autonomous-OS positioning and the $0 sovereign lane + FHIR-interop moat.
- **IP doctrine adopted** (2026-08-27) - public naming stays NURA-owned; OSS we build on is internal-only and never disclosed publicly; Reg A described by capability, not vendor.
- **Aero medical drone-delivery division chartered** (2026-08-26) - founder directive; BVLOS gates and SITL swarm proof before real payload ops.
- **Medisun enterprise-OS spine** - 6-entity per-TIN/NPI structure; Perfex stays non-clinical, OpenEMR is the clinical truth, eMedical/QBO in support.
- **Single-writer / one-brain invariant reinforced** - Moltbook intel ("Eight agents do not make a distributed system", "stop giving agent runtimes unlimited concurrency") aligns review with the CTO doctrine that Hermes = brain, executors = hands, minimum-necessary scope.

## People I worked with

- **Founder (Eddie)** - directives drove the two biggest items this week (drone division charter; Medisun-first-client gating). The `People/` folder is sparse this week; no new person notes were created. Founders' decision still pending on the provider-credit block (402) and the llama3.1:8b model-routing fix.
- Note: no meeting notes landed in `Meetings/` this period; interaction was via directives and the autonomous ops loop.

## What I learned

- **MCP 2026-07-28 stateless spec** is the largest MCP change since launch: removes the `initialize` handshake and `Mcp-Session-Id`; header-based routing (`Mcp-Method`/`Mcp-Name`) enables round-robin LB, serverless, scale-to-zero; wire-incompatible, so our 61 MCP lanes need a staged migration.
- **openpilot 0.11.2** (2026-08-12) ships an 880M-param driving model and external-GPU support (comma four + AMD RX 9060 8GB, ~$799) - directly relevant to the AV lane (Escape Hybrid + comma four + hermes-driver).
- **Radiology AI candidates** for RIS/PACS: OpenRad (~1,700 curated open-access models), Orchid (MIT DICOM orchestration), Merlin (Stanford 3D CT VLM, Nature 2026); Heimdallr (DICOM intake + TotalSegmentator) as infra candidate.
- **greenlet ABI pitfall**: the emos/playwright failure was `greenlet` shipping only `_greenlet.cpython-311*.so` while runtime is Python 3.13.5 -> ABI mismatch -> `playwright.async_api` import fails; fixed with `greenlet==3.5.5` (cp313).
- **Hermes v0.20.5+** gives cron jobs persistent memory + per-job reasoning effort; MCP 2.x SDK migration and stateless-protocol support landed.
- **Team memory candidates**: TencentDB-Agent-Memory, PlugMem (ICML 2026), agentmemory - evaluate against our mem0 + Qdrant setup for team-level shared memory.

## What to carry forward

- **LAB node (72.60.163.140 / KVM8 / 1030183) critical** (as of 2026-08-28): load ~80-84 over 8 cores, swap 94% (94% CRITICAL), top consumer `colibri qwen36` (local LLM serve). CLINIC (72.61.71.211) swap 99%. Remediation is production-node / approval-tier; recommend trim/restart of the colibri qwen process.
- **27 erroring crons persist** (as of 2026-08-28): ~9 on 402 provider-credit block, ~10 on the `llama3.1:8b does not support thinking` routing mismatch (weekly jobs; `obsidian-weekly` is one). The weekly class re-fires today. Needs a founder/intended-model decision - not auto-patched (consequential routing change).
- **Medisun first-client gated** on the Perfex REST module + API token (currently 404) - founder acquiring.
- **UAP deadlines**: Greer Aug 29; ODNI NDA-waiver checkpoint Aug 30; PURSUE capped at Tranche 5.
- **Lab-intake cron lanes down since 2026-08-26** (email=`gws` missing, fax=`DOCUMO_API_KEY` missing) - known silent drop; cron stays `[SILENT]` until creds/healing verified.
- **Local swap 100%** and **memory at 99% capacity** - both have standing watchdogs; no durable new lesson generated this pass.

## Suggested questions for future agent

1. How does "NURA = the physician's autonomous OS that owns the record" (`[[NURA-OS/Products/NURA-Master-Plan]]`) reconcile with the medical sidecar doctrine that OpenEMR is the internal clinical truth and Perfex never stores clinical data (`[[NURA-OS/Products/Medisun-Health-Group-Enterprise-OS]]`)? Is "owning the record" in tension with a decoupled external source of truth, or is the distinction layered and explicit somewhere?
2. The IP doctrine (`[[NURA-OS/Strategy/NURA-Competitive-Differentiation-and-IP-Doctrine]]`) forbids disclosing the OSS we build on, yet NURA is drafting a Reg A circular (`[[NURA-OS/SEC/NURA-RegA-Offering-Circular-DRAFT]]`). Exactly what disclosure boundary is drawn between "described by capability, not vendor" and the required technical descriptions of a securities offering?
3. The single-writer / one-brain invariant landed this week (`[[NURA-OS/Evolution/daily-2026-08-28]]`), yet the LAB overload incident (`[[NURA-OS/Reflections/daily-reflection-2026-08-28]]`) names `colibri qwen36` - the sovereign local-LLM lane - as the top resource consumer. Is the local sovereign model the intended "one brain", or an accidental concurrency/load hot spot that the one-brain doctrine should be constraining?
4. Medisun first-client integration (`[[NURA-OS/Products/Medisun-First-Client-Integration]]`) shows 56 n8n workflows with several live (GHL/NMI/PDFMonkey) but the Perfex REST module + API token is still 404-gating (`[[NURA-OS/Products/Medisun-Health-Group-Enterprise-OS]]`). What unstated path unblocks the client record without waiting on the founder's token, given the Perfex MCP (183 tools) and REST module already exist?
5. The Aero drone-delivery charter (`[[NURA-OS/Aero/Medical-Drone-Delivery-Division]]`) sets BVLOS regulatory gates and SITL swarm proof as MVP gating, but I find no explicit FAA/BVLOS regulatory timeline for medical payload delivery recorded anywhere in the vault. What grounding exists (or is missing) for that regulatory assumption?
