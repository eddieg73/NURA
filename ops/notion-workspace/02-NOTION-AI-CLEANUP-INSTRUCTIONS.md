# NOTION AI — CLEANUP INSTRUCTIONS
Paste the block below into Notion AI. Written 2026-09-11.
Source of truth: `ops/notion-workspace/` in github.com/eddieg73/NURA.

---

## WHY THESE INSTRUCTIONS EXIST

An audit of this workspace found 912 objects (883 pages, 29 databases) with four structural problems.
They could not be fixed by API — Notion's API **cannot re-parent pages or databases at all** (a page
move returns HTTP 200 and silently does nothing). You are being asked because **you can move things**,
which the automation cannot.

## GROUND RULES — read before acting

1. **Verify every move.** After moving anything, open it and confirm it is really in the new location.
   Do not trust a success message alone.
2. **Never mass-delete without showing me first.** For any deletion over 10 items, list what you will
   delete and wait for my confirmation.
3. **Do not touch anything in the DO NOT TOUCH list** at the end.
4. **Work one task at a time** and report after each.
5. If a page's content looks like real personal or business records, **stop and ask**.

---

# TASK 1 — Review and remove the imported Finnish template (145 pages)

**What it is:** 145 pages titled `Aamuyhteenveto – <date>` (Finnish for *"morning summary"*), plus a
database called **`Aamuyhteenvedon keskus`** ("morning summary centre"). Every one of the 145 pages was
last edited **2026-08-30, all in a single batch** — the signature of a template import.

**Before deleting anything:**
1. Open **`Aamuyhteenvedon keskus`** and read 5–6 of the `Aamuyhteenveto` pages at random.
2. Tell me: **is this a template someone imported, or my own real journal entries?**
3. If they contain my own writing, **stop** — do not delete. Report back instead.
4. If they are empty or obviously template filler, list the 145 pages and ask me to confirm.

**Then, on my confirmation:** delete the whole `Aamuyhteenvedon keskus` tree.

**Note:** this tree's parent is a page the API couldn't see, which is why 148 objects showed as
orphaned. If you can see its parent, tell me what it is — that may reveal a second workspace.

---

# TASK 2 — Deduplicate the life-category pages (20 pages → 10)

These ten categories each exist **twice**. One copy is from **2026-08-31**, the other from **2026-09-09**.

| Category | 2026-08-31 copy | 2026-09-09 copy |
|---|---|---|
| Admin | `7adc16c3-827e-4783-855c-3ab816a71eb6` | `670a9b14-e498-8321-9818-8184bfd83182` |
| Business | `fd590c21-08e8-4bc8-abb4-54e8c5c8160a` | `87ba9b14-e498-82d2-9ff9-01f7de93271e` |
| Family | `e9ba57cc-606e-4838-8fbd-27144ebb60ed` | `e0ca9b14-e498-83d6-9e38-81c5124398a0` |
| Finance | `50434541-b874-4539-9da9-c84cd9f3baa0` | `c6ba9b14-e498-82c5-8fa0-0196327f3934` |
| Fitness | `db6a3998-3c66-4157-9296-eae54254fb22` | `a80a9b14-e498-83bb-ac61-81fb24f92407` |
| Health | `a5572029-ee85-47b6-a600-8b4358077f5b` | `5b2a9b14-e498-82ad-ba48-01b7c3c308d7` |
| Hobbies | `0c0cfa2b-53e1-41a7-8bf5-b86d93920b70` | `8aea9b14-e498-82d0-b054-01a9808b5786` |
| Learning | `cc076e4f-41a1-4b3d-b5f1-08f4f1d78592` | `b49a9b14-e498-8227-8ae0-8182d2fb11dd` |
| Projects | `e8ad6430-6df8-4dd5-aaab-3dacac80be41` | `555a9b14-e498-83e4-8832-819b63046b82` |
| Travel | `5a06f179-d04f-44ad-8cfb-289cdfab3296` | `65aa9b14-e498-8311-882f-01a08d7739e1` |

**For each pair:**
1. Open both copies and compare their contents.
2. If **one is empty** → keep the other, archive the empty one.
3. If **both have content** → copy anything unique from the smaller into the larger, then archive
   the smaller.
4. If **both are full and different**, **stop and ask me** which is real.

**Report the outcome for all ten** before moving on. Do not delete until you've told me.

---

# TASK 3 — Organize the workspace root

These **14 items sit loose at the workspace root** with nothing grouping them:

```
database  Claude Tasks
database  My links
database  People
page      12-Week Plan
page      Archive — NURATECH Executive Command Center — Backup 2026-09-09
page      Meeting recap
page      NURA Health Communications Flutter App
page      NURA Provider Labs — Master Clinical Intelligence, Radiology & Imaging
page      NURATECH AI — Executive Command Center
page      NURATECH — MASTER WORKSPACE
page      Private Clinical Appendix — Cognitive Profile
page      Project — Raspberry Pi + ESP32 Daily Intel Dashboard
page      To Do List
page      🕵️ OSINT & Intelligence Command
```

**Do this:**
1. Keep **`NURATECH — MASTER WORKSPACE`** at the root — it is the index for everything else.
2. **Move** these under `NURATECH — MASTER WORKSPACE`, in this order:
   - `Meeting recap`
   - `12-Week Plan`
   - `Project — Raspberry Pi + ESP32 Daily Intel Dashboard`
   - `🕵️ OSINT & Intelligence Command`
   - `Private Clinical Appendix — Cognitive Profile`
3. **Leave these at the root** (they are hubs in their own right):
   `NURATECH AI — Executive Command Center`, `To Do List`, `NURA Health Communications Flutter App`,
   `NURA Provider Labs — Master Clinical Intelligence`, `Archive — … Backup 2026-09-09`.
4. **Databases can be moved by you too** — if you can, move `People`, `Claude Tasks` and `My links`
   under the Master Workspace as well.
5. After each move, **open the item and confirm it really moved.**

---

# TASK 4 — Resolve the four superseded databases

Four databases are labelled **`⛔ SUPERSEDED — … (nested content)`**. They are duplicates of live
databases, but each sits at the top of a **nested tree** — deleting one deletes its child pages and
child databases with it. The API could not do this safely; you can, but only carefully.

**For each, in this order (top-down, one at a time):**

| Superseded ID | Live replacement |
|---|---|
| `e90a9b14-e498-83f9-ae0b-810a94157b95` — Executive Projects | Executive Projects `9547910e-8975-44b8-b511-2108abfa0d11` |
| `116b71cd-76a4-4eef-a1d0-81068e3c6cf4` — Organizations & Current Roles | Organizations & Current Roles `c20a9b14-e498-8333-b554-01413da172df` |
| `44a69385-45ef-47ab-a787-aa6274472081` — Medisun Completed Work Register | Medisun Completed Work Register `8aca9b14-e498-8200-8d00-0149672c0a5f` |
| `cdca9b14-e498-821f-9a92-814495237c4f` — Prehospital & Aeromedical Evidence Board | Prehospital & Aeromedical Evidence `c28d624e-b827-4065-b1fd-200cdf7dd561` |

**Procedure per database:**
1. Open the superseded database and list **every child page and child database** beneath its rows.
2. For each one, confirm an equivalent exists in the **live replacement**.
3. If **everything is duplicated** → delete the superseded database.
4. If **anything is unique** → tell me; do not delete, and do not merge silently.

**Known example to check first:** the superseded Executive Projects holds a *"Medisun Digital Operations
& NURA ERP Integration"* project and an *"Untitled"* child database. Confirm both are represented in the
live set before deleting.

---

# TASK 5 — Verify and finish

1. Confirm **`NURATECH — MASTER WORKSPACE`** is at the root and readable top to bottom.
2. Confirm the workspace root holds only the intended items (see Task 3, step 3).
3. Update the **⚠️ OUTSTANDING CLEANUP** section of the Master Workspace page: tick off what you fixed
   and leave anything you could not.
4. Report what you changed, with counts.

---

# 🚫 DO NOT TOUCH

- **`NURATECH AI — Executive Command Center`** and its 284 items — the live operations hub.
- **`NURATECH — MASTER WORKSPACE`** — the index. Add to it; don't restructure it.
- **The Skill Registry** — it appears unreadable to the API but contains **30+ real rows**
  (one per skill category: crm, devops, productivity, health, research, …). **Do not delete it.**
  It is real content, not a ghost.
- **`Private Clinical Appendix — Cognitive Profile`** — sensitive health data. Move it if asked; never
  share, export or summarise it.
- **Anything marked `⛔ SUPERSEDED`** — leave it alone until Task 4 says otherwise.
- **`Archive — NURATECH Executive Command Center — Backup 2026-09-09`** — a deliberate backup.
- **Master Tasks & Commitments**, **Executive Projects** (the live ones) — these are the canonical
  writes and must keep working.

---

## WHAT WAS ALREADY FIXED (no action needed)

- 33 databases → **29**. Five leaf duplicates removed; the canonical set verified intact by row count
  (18 projects / 78 tasks / 9 orgs / 27 completed / 6 evidence / 10 diary).
- Notion's default **"Welcome to Notion!"** page removed.
- A single **Master Workspace index page** built listing every project, database, area and open item.
- Links made self-describing so nothing reads as a bare ID.

## KNOWN LIMITATION — set expectations

Because the API cannot re-parent, the previous pass **could not organize by moving**. Anything in
Task 3 requires you. This is why 14 items are still loose at the root.
