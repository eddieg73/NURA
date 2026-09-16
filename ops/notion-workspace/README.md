# NURA — NOTION WORKSPACE CONSOLIDATION

**Master workspace page:** `3d8a9b14-e498-8125-a630-f2fcc2bd2354`
https://www.notion.so/3d8a9b14e4988125a630f2fcc2bd2354
One workspace at the workspace root, listing every project and every canonical database.

**Result: 33 databases → 28 live.** Canonical set verified intact by row count.

---

## The canonical set (use these)

| Concept | Database ID | Rows |
|---|---|---|
| Executive Projects | `9547910e-8975-44b8-b511-2108abfa0d11` | 18 |
| Master Tasks & Commitments | `d3ff0c00-c629-43dc-b82c-06a28866fcb1` | 78 |
| Organizations & Current Roles | `c20a9b14-e498-8333-b554-01413da172df` | 9 |
| Medisun Completed Work Register | `8aca9b14-e498-8200-8d00-0149672c0a5f` | 27 |
| Prehospital & Aeromedical Evidence | `c28d624e-b827-4065-b1fd-200cdf7dd561` | 6 |
| 🧠 Founder Evolution Diary | `a5dfe5bd-c416-4f4c-b3e9-d6119279ad88` | 10 |
| Hermes ↔ ChatGPT — Agent Handoffs | `3cda9b14-e498-8178-8581-c358f57305a1` | 27 |
| MIH Evidence & Policy Registry | `298d6119-62cf-4233-8717-9a3c1c687080` | 15 |
| Nura ERP Build Backlog | `e80e33c7-d5a3-4f4b-a3e5-0c19133a605d` | 45 |
| People | `d3da9b14-e498-82df-b0d8-014512d331ec` | 6 |
| To Do List DB | `384a9b14-e498-8041-a6cf-fc6849b4fc40` | 13 |
| Flutter Delivery Board — Active | `22260907-f18c-4768-95de-052942bdb055` | 10 |

The two competing "Executive Command Centers" were the root cause of most duplication:

- **LIVE** — `613e14da-104a-470e-af85-799d66eb8ebc` "NURATECH AI — Executive Command Center" (workspace root)
- **backup** — `3d6a9b14-e498-81e2-bab7-fc22b42127e9` "Archive — … Backup 2026-09-09"

Canonical databases were chosen **per-DB by row-level content**, not by which page they sat under.

---

## ⚠️ THE CRITICAL LESSON

**Never consolidate a Notion database on a row-title diff alone.**

The first pass compared row titles and proved several copies held "no unique rows." That was **wrong as a
safety proof**: in Notion a project page can **parent** a database, so the copies sat at the top of **nested
trees**. Trashing them cascaded into live content:

> Trashing `e90a9b14` (the Executive Projects copy) cascaded and took down the **MIH project page**
> and the **Prehospital & Aeromedical Evidence Board** (`cdca9b14`).

Everything was restored (`notion_cascade_recover.py`) and the check is now **child-content-aware**
(`notion_child_audit.py`). That audit is what caught the remaining hazards.

**Rule: before trashing any database, walk every row and check for `child_page` / `child_database`
blocks. If any exist, do not delete without tracing the subtree.**

---

## Removed (4 — verified zero nested content)

| Database | ID | Why safe |
|---|---|---|
| Master Tasks & Commitments (copy) | `752a9b14-…-817c7145b742` | 57 rows, strict subset of canonical 78; no children |
| 🧠 Founder Evolution Diary (copy) | `e3ba9b14-…-81d0f6304ba0` | 10 rows identical; no children |
| Flutter Delivery Board | `2c2be702-…-d5520e1dafee` | 0 rows; superseded by "— Active" |
| Time Tracking (one of two empties) | `77a2851a-…-32fc18143850` | 0 rows |

All row content is preserved in `audit/notion_superseded_manifest.json`. Notion trash retains them 30 days.

## Kept and relabelled "⛔ SUPERSEDED — … (nested content)" (4)

These hold **nested children**, so deletion cascades. They are left live and clearly labelled:

- `e90a9b14-e498-83f9-ae0b-810a94157b95` — Executive Projects
- `116b71cd-76a4-4eef-a1d0-81068e3c6cf4` — Organizations & Current Roles
- `44a69385-45ef-47ab-a787-aa6274472081` — Medisun Completed Work Register
- `cdca9b14-e498-821f-9a92-814495237c4f` — Prehospital & Aeromedical Evidence Board

Removing these safely is a **human-reviewed, top-down job** after confirming each nested child exists in
the live tree. It is not automatable with acceptable risk.

---

## Still needs a human

1. **Skill Registry ×3** (`70986afe`, `10cf4335`, `ee46997c`) — appear in search, all return 404; the
   integration has no access. Open or delete them manually.
2. **The four "⛔ SUPERSEDED" trees** — top-down removal, human-reviewed.
3. **Aamuyhteenvedon keskus** (Finnish, 100+ rows, `d13a9b14-…`) — unexplained; flagged, untouched.

---

## Supabase — NOT provisioned

The user believed Supabase was available. It is **not**:

- no `SUPABASE_*` credentials in any env file
- no `supabase` CLI
- no running instance or container
- no project URL or ref anywhere in the repo

It exists only in `NURATECH-AI-TECHNOLOGY-MASTER-PLAN.md` ("Data: Supabase Postgres + pgvector", listing
`patients · encounters · documents · diagnosis_candidates · icd10_codes · hcc_mappings · raf_scores · …`).

That plan's own **delta #1** flags it as unresolved:

> *"Supabase/pgvector vs Qdrant-local doctrine — plan mandates Supabase Postgres+pgvector; standing = Qdrant
> local forever (zero-credit, PHI-safe). Recommend: Qdrant remains live memory; Supabase adopted for the RCM
> product DB (new domain, not the Hermes memory lane)."*

**So Supabase is a decision, not a system.** If adopted for the RCM product DB it must be a
**HIPAA-eligible** Supabase project (BAA, regional hosting) — Supabase's free tier is not. Do not put PHI
in it before that is settled.

---

## Scripts (run order)

| Script | Purpose |
|---|---|
| `notion_workspace_audit.py` | enumerate everything visible to the integration |
| `notion_inventory.py` | per-DB row counts, last-edited, parent |
| `notion_dup_rows.py` | row-level diff between duplicate pairs |
| `notion_inspect.py` | project list + orphan investigation |
| `notion_unknowns.py` | resolve unreadable / odd databases |
| `notion_capability_test.py` | can we create at root? move a DB? rename? |
| `notion_master_build.py` | build the master workspace page |
| `notion_consolidate.py` | label links, dump manifest, trash verified leaves |
| `notion_child_audit.py` | **the safety gate** — child-page/database check before deletion |
| `notion_cascade_recover.py` | recover a cascade |
| `notion_resolve_children.py` | compare nested children between twins |
| `notion_finalize.py` | restore + relabel, verify canonical set |

## Capability findings — TESTED, not assumed

| Operation | Result |
|---|---|
| Create a page at **workspace root** | ✅ works (`parent: {type: workspace}`) |
| **Rename** a database | ✅ works |
| **Move a database** to a new parent | ❌ **not supported** — `validation_error: Parent must be a database_id when provided` |
| **Move a page** to a new parent | ❌ **does NOT persist** — see below |
| Trash / restore a database | ✅ works (`in_trash`) |
| Append / patch blocks | ✅ works (position with `after`) |

### ⚠️ The page-move trap — a 200 that lies

`PATCH /v1/pages/{id}` with `{"parent": {"type": "page_id", "page_id": <dest>}}` returns **HTTP 200**, and the
**response body itself** echoes a parent that is **not what you asked for** — the page stays where it was.

Verified 2026-09-11 by re-reading the parent at +2 s and +7 s after the call:

```
BEFORE      : parent={'type': 'workspace', 'workspace': True}
PATCH status = 200
PATCH RESPONSE claims parent = {'type': 'workspace', 'workspace': True}   <-- already contradicts the request
AFTER (2s)  : parent={'type': 'workspace', 'workspace': True}
AFTER (7s)  : parent={'type': 'workspace', 'workspace': True}
VERDICT: MOVE DID NOT PERSIST
```

**Lesson: a 2xx is not evidence of a state change. Re-read the object and compare to what you asked for.**
An earlier pass of this work assumed page moves worked from the status code alone and wrote a false
"moved in during cleanup" claim onto the master page. That claim was corrected in place.

**Consequence for organization:** because neither pages nor databases can be re-parented, the workspace
**cannot be restructured by moving things**. Organization is therefore achieved by
**(a) a single indexed master page**, **(b) renaming for clarity**, and **(c) removing genuine garbage** —
not by relocation.

---

## Workspace structure audit (2026-09-11)

**912 objects — 883 pages, 29 databases.** Top-level groups by size:

| Items | Group |
|---|---|
| 284 | NURATECH AI — Executive Command Center *(live ops hub)* |
| 226 | To Do List tree |
| 148 | orphaned tree under an inaccessible ancestor (`e13a9b14`) |
| 106 | NURA Health Communications Flutter App |
| 74 | Archive — Backup 2026-09-09 |
| 17 + 12 | orphaned fragments |
| 15 | loose at workspace root (now 14 after removing Notion's default page) |

Depth reaches 8 levels.

### Root cause of the clutter

1. **Two competing Executive Command Centers** — the live one and the 09-09 backup (see above).
2. **An imported Finnish template** — 145 pages titled `Aamuyhteenveto – <date>` (Finnish for *"morning
   summary"*), every one last edited **2026-08-30 in a single batch**, sitting under a page the integration
   cannot see. Almost certainly template import, not authored work. **Left untouched — flagged for your decision.**
3. **Duplicate life-category trees** — `Hobbies, Projects, Travel, Admin, Fitness, Learning, Family,
   Business, Finance, Health` each exist **twice** (20 pages). One set edited **2026-09-09**, the other
   **2026-08-31** and carrying **non-Notion UUID formats** — a second imported template. Pick a keeper.
4. **15 loose items at the workspace root** with no organizing parent.

### What was done about it

- **Notion's default "Welcome to Notion!" page** — removed to trash.
- **Master workspace page** rebuilt as a full index: 93 blocks covering every project, every canonical
  database, every top-level area, the archive, and every outstanding cleanup item.
- **Nothing was relocated** (impossible via API). The index is the organization.
