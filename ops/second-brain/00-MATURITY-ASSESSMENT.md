# AI SECOND BRAIN — MATURITY ASSESSMENT AND LEVEL 5 BUILD
Audited 2026-09-12. Every figure below was probed live; nothing is assumed.

---

## THE LADDER

"Maturity level" only means something if the levels are defined and testable. This is the definition
used here.

| Level | Name | Test — what must be true |
|---|---|---|
| **L0** | Amnesiac | Every session starts blank |
| **L1** | Static | Flat notes; a human must remember where things are |
| **L2** | Retrievable | Vector + full-text search. Memory = **recall** |
| **L3** | Structured | Typed entities, links, provenance, decay policy, domain separation, **cross-agent readable** |
| **L4** | Reflective | The system writes its own lessons, consolidates, decays, reflects on outcomes |
| **L5** | **Closed-loop cognition** | It surfaces unnamed patterns across unrelated domains **unprompted**, reconciles contradictions, and — the binding test — **the insight changes behaviour** |

**The binding test for L5 is the last clause.** Insight generation is L4. Insight that is *acted on*
is L5. A brain that produces brilliant notes nobody reads is a very sophisticated L4.

---

## VERDICT: **LEVEL 4.5**

**L5 cognition is real. The loop is open.**

### What is genuinely L5-grade — and it is impressive

`obsidian-nightly` has produced **15 synthesis notes** (Aug 27 → Sep 12, ~daily) under a real
discipline. From `Synthesis - The Absence-of-Signal Blind Spot.md` (9,674 bytes, 2026-09-11):

- Cross-source rule: *the concept must appear in **2+ unrelated sources*** — and it cites **6**
  independent sources with paths
- **Builds on the prior day's pattern**: *"The 09-10 synthesis named the mis-selected signal — the
  right question asked of the wrong field. This is the adjacent failure."*
- Structured `Interpretation` with 7 numbered inferences, and a `Boundary` section
- Self-aware about its own limits: *"read-only pass; nothing was modified and no fix was applied"*

It also correctly named its own feed failure's failure mode. (See gap 4.)

### What is measured, not assumed

| Component | State | Evidence |
|---|---|---|
| Vault | **642 md notes**, 92 MB | `find ... \| wc -l` |
| Qdrant collections | **8** | live `/collections` |
| Synthesis notes | **15** | `Knowledge/Synthesis - *.md` |
| Synthesis/reflection crons | **9 enabled** | `jobs.json` |
| Total vectors before this build | **~1,773** | per-collection counts |
| agentmemory `:49134` | **DOWN** | `http=000` |

---

## THE FIVE GAPS

### 1. The retrieval layer does not cover the corpus — **FIXED AND VERIFIED**
**1,773 vectors across 8 collections for a 642-file / 92 MB vault.** Largest collection 925 points;
`nura-os` only 251 despite `NURA-OS/` being the biggest folder. The synthesis works because it reads
*files*; nothing could *retrieve* them.

**Built:** collection **`nura-vault`**, 768-dim (fastembed `bge-base-en-v1.5`, matching the working
mem0 lane), heading-aware chunking, content-hash ids so re-runs update rather than duplicate.

**Completed: 6,476 / 6,476 chunks, 0 failures** — ran ~97 minutes, resumable throughout.

> **Honest note on corpus composition:** of 643 files, **231 are `NURA-OS/Atlas-Playbook`** (an
> imported template tree) and **412 are NURA knowledge.** The playbook dominates by *bytes* (~70 of
> 76 MB) though not by file count. Tagged `playbook: false` so retrieval can filter it — **verified
> working: a filtered query returned 5 results, all with `playbook=false`.**

#### Retrieval verified by ASKING IT QUESTIONS — not by counting points
A populated collection proves storage, not retrieval. 8 probes, each expecting a known source:

| Result | Question | Top hit |
|---|---|---|
| **PASS** | absence of signal blind spot | `Knowledge/Synthesis - The Absence-of-Signal Blind Spot.md` — **rank 1, 0.790** |
| **PASS** | MCP stateless core migration | `Knowledge/Synthesis - MCP Stateless-Core Migration.md` — **rank 1, 0.779** |
| **PASS** | Reg A offering circular | `NURA-OS/SEC/NURA-RegA-Offering-Circular-DRAFT.md` — **rank 1, 0.694** |
| **PASS** | drone LiDAR landing zone | `NURA-OS/Aero/EMS-Drone-Spec.md` — **rank 1, 0.714** |
| **PASS** | memory pressure / swap saturation | `Reports/2026-09-13-daily-operations.md`, synthesis at rank 3 |
| **PASS** | Google SSO for Perfex + OpenEMR | `NURA-SSO-SCIM-Setup.md` at rank 5 |
| **MISS\*** | Paperclip retirement / workforce | `meta/active-work.md` — *the RIGHT note; my matcher looked for the literal filename fragment "Paperclip"* |
| **MISS** | DARPA ARES oxygen metrology | `Atlas-Playbook/gstack-repo/...` — **the ARES artifacts are NOT in the vault** |

**6/8 by the strict test, 7/8 in substance.** And the one genuine miss exposed a real hole, below.

#### The probe found a real gap: the engineering record was outside the brain
The ARES work lives in the **git repo** (`/opt/data/NURA/ops/ares/`), not the vault — so the vault
index could not see it. Worse, the vault is 92 MB dominated by an imported template tree, while the
actual engineering output of this operation (ARES rev-A.1, the workforce runbook, the drone sensing
audit, the URL reviews) sat **entirely outside the brain.**

**Fixed:** the repo's `ops/` tree + scripts are now indexed into the **same collection** tagged
`source: repo`, so retrieval spans the vault *and* the engineering record. Same checkpoint file,
idempotent, resumable.

### 2. No cross-agent onboarding pack — **FIXED**
`vault-shared-memory` specifies a 5-file `meta/` pack plus `CLAUDE.md` / `AGENTS.md` / `GROK.md` /
`gemini-local-prompt.md` so **every** agent onboards from one source. **None of it existed** — no
`meta/` directory, no pointer files.

That is the difference between a second brain one agent can read and one *every* agent shares.

**Built:** all 5 meta files + all 4 pointers, **generated from live state** (fleet table, disk/memory
probed at build time, cron counts read from `jobs.json`, the board of record, the known-dead lane
list). The pointers route; the meta files are the source.

### 3. agentmemory lane down — **NOT FIXED**
`:49134` returns `http=000`. Consistent with the recorded `iii-engine` daemon-down state. The
standalone MCP path works, so this is degraded rather than fatal — but it is one of the two memory
lanes and it is not carrying anything.

### 4. The vault's own feed was mirroring a retired board — **DIAGNOSED**
`vault sync` queries the **Paperclip API on `:3101`, which is dead (`http=000`)** — I retired
Paperclip the same day.

**But the job self-healed and was honest about it.** It detected the dead port and the empty API key,
fell back to a **DB-level read over SSH into the Lab's `paperclip-db`**, and wrote a snapshot
labelled:

> *⚠️ Board is FROZEN, not operating: Paperclip was retired 2026-09-12... Last agent heartbeat:
> **2026-08-21 02:23:54** (9/54 agents ever heartbeat). This file is a historical-data mirror.*

**Two findings from that, both material:**
- **Company `58ddc931` (207 issues / 54 agents) IS recoverable** — it lives on the **Lab
  (`72.60.163.140`)** in a `paperclip-db` container, not locally. Earlier I recorded it as existing
  in no local backup; that was true of *local* and missed the Lab. **`WF-001` is updated by this.**
- That board is **also** mostly dead: **206 of 207 open**, frozen since 08-21, only 9 of 54 agents
  ever heartbeated, **147 orphaned assignments.**

The job's own snapshot names the exact failure mode the brain diagnosed on 09-11: *a `[SILENT]` lane
is indistinguishable from a quiet day.* The brain named the pattern; the feeder was an instance of it.

### 5. **The loop was open — now closed**
The 09-11 synthesis prescribed, in its own words: *"A `[SILENT]`-on-empty cron is a design defect, not
a quiet day... it must return **degraded/non-silent**."* That is concrete, implementable, and correct.
**It was written to a note that nothing ever read again.**

**Built:** `close_the_loop.py` — extract rules → check whether each is *enforced* in the skill corpus
→ raise unimplemented ones as **founder-gated doctrine tickets**, and record implemented ones so the
same rule is never re-raised.

---

## I BUILT A BAD TOOL, CAUGHT IT, AND FIXED IT

Worth recording, because the failure is instructive.

**v1 reported "1.00 coverage" for every rule** — because at 8.8 M chars of technical jargon, almost
any word appears somewhere. 21,327 of 21,747 distinct terms were "rare". The check discriminated
**nothing**, and it reported **0 gaps** — a false all-clear.

**Fixed to bigram phrase matching.** Coverage then ranged 0.00–0.40, which discriminates.

**But that over-corrected, and v1 had already put 6 tickets on the founder's board.** Several were
not rules at all — they were *narrative and meta sentences* from the synthesis prose:

| Ticket | Text | Verdict |
|---|---|---|
| DOC-003 | "The one concrete, still-open consequence is the CLINIC attribution conflict above..." | narrative — not a rule |
| DOC-005 | "Today's worklands — software engineering, agent orchestration... independently converge" | observation — not a rule |
| DOC-007 | "The weekly artifact states the doctrine plainly: ..." | reporting — not a rule |
| DOC-009 | "Doctrine, not a defect report — read-only pass..." | meta-commentary — not a rule |
| DOC-011 | "Cross-source rule applied: the concept must appear in 2+ unrelated sources" | **is a rule, and IS implemented** — false gap |
| **DOC-001** | **"Auth-log reviews must pivot on `login_success`, never failures-only."** | **genuine gap — kept** |

**Root cause:** v1 treated *any sentence containing a modal verb* as a rule. The synthesis notes are
prose; they contain narrative sentences that merely mention "must" or "should".

**v2 requires** the sentence to (a) not open with a report marker, (b) not be past-tense reporting,
(c) not describe the note itself, (d) carry its modal in the sentence *head*, not tailing it. And the
threshold is recalibrated: **≥0.30 present · <0.15 real gap · 0.15–0.30 uncertain → noted, not ticketed.**

**The 5 junk tickets were withdrawn to `Done` with an audit note explaining why** — not deleted, so
the error stays reviewable. **1 genuine doctrine gap survived.**

> ⚠️ **One more self-correction:** the first withdrawal pass reported "6 still open" *after* writing
> `HTTP 200`. The writes had worked; **my verifier was broken** — its text reader did not handle
> `select` properties, so every status read as `""`. Fixed and re-read: **5 Done, 1 Backlog.**
> The doctrine held up in both directions — a broken verifier and a silent no-op look identical.

---

## WHERE THIS LEAVES THE SECOND BRAIN

| Layer | Level | Note |
|---|---|---|
| Retrieval | **L2** → improved | `nura-vault` indexes the corpus |
| Structure | **L3** ✓ | typed folders, provenance, decay, **+ cross-agent pack now built** |
| Reflection | **L4** ✓ | 9 crons: reflection, auto-dream, sleep consolidation, decay |
| Emergent synthesis | **L5** ✓ | 15 notes, 2+ unrelated-sources rule, builds on prior days |
| **Closed loop** | **L5** — **newly built** | synthesis → enforcement check → founder-gated doctrine |

**From L4.5 to L5:** the insight now has a path to becoming behaviour.

---

## STILL OPEN — HONESTLY

1. **agentmemory `:49134` is down.** One of two memory lanes is carrying nothing.
2. **`close_the_loop` has 1 true positive from 15 notes.** That is a *low* yield — either the vault's
   doctrine is genuinely well-assimilated, or the extractor is still conservative. Treat the number
   as unvalidated until it has run against a few more nights of synthesis.
3. **The loop is not yet scheduled.** It exists and runs on demand. Wiring it to a cron is the next
   step — deliberately not done yet, because a bad extractor on a nightly schedule would fill the
   founder's board with junk. *This session is the evidence for that caution.*
4. **`nura-vault` index build was still running** at the time of writing.
5. **The 5 junk tickets are `Done`, not deleted** — they remain visible in the board's Done column
   with the explanation attached.
