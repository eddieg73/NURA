# NURA Executive Records Manager — Google Drive Organizer

**Status:** implementation COMPLETE + tested (30/30). **Execution BLOCKED on Google OAuth.**

Owner: Hermes (CTO / Executive Records Manager) · Created 2026-09-10

---

## Why it hasn't run yet

Drive access requires a Google OAuth token. Verified state:

```
setup.py --check  ->  NOT_AUTHENTICATED: No token at /opt/data/profiles/nura/google_token.json
--auth-url        ->  ERROR: No client secret stored. Run --client-secret first.
```

Google API libraries **are** installed (`googleapiclient`, `google.oauth2`, `google.auth`).
The only missing input is your Google Cloud OAuth client. Nothing else blocks execution.

---

## Unblock — 3 steps (~5 minutes, one time)

1. **Create the OAuth client**
   - https://console.cloud.google.com/apis/credentials
   - Credentials → Create Credentials → OAuth 2.0 Client ID
   - Application type: **Desktop app** → Create
   - Enable the **Google Drive API**: https://console.cloud.google.com/apis/library/drive.googleapis.com
   - If the app is in *Testing*, add your account as a test user:
     https://console.cloud.google.com/auth/audience

2. **Download the JSON** and send me the file path. I run:
   ```bash
   python3 <skill>/scripts/setup.py --client-secret /path/to/client_secret.json
   ```

3. **Approve the URL I send back.** The browser will land on `http://localhost:1`
   and fail — that is expected. Copy the **entire** redirected URL and send it to me.

Then I run the organizer.

---

## Run order (safe by construction)

```bash
cd /opt/data/drive-organizer
python3 drive_organizer.py --dry-run      # plan only — writes state/last_plan.json  (DEFAULT)
python3 drive_organizer.py --build-tree   # create the folder taxonomy
python3 drive_organizer.py --execute      # moves + renames
```

The engine is idempotent: `get_or_mk` reuses existing folders, so re-running never duplicates the tree.

---

## Doctrine enforced by the engine

| Rule | Implementation |
|---|---|
| **Never delete** | No `files().delete()` call exists anywhere in the code. Only `update(addParents/removeParents)`. |
| **Never alter sharing** | Permissions are only ever **read** (`permissions().list`) — never written. |
| **Never guess** | Confidence < 0.5 → `08 — INBOX — TO BE FILED`. |
| **Duplicates preserved** | Name-pattern / name+size / same-stem detection → `09 — DUPLICATES — REVIEW`. |
| **PHI isolated** | Sensitive detection wins over all other routing → `RESTRICTED — PHI / PATIENT RECORDS`. |
| **Evidence chains intact** | `protected_from_rename()` skips court/filed/executed/recorded/notarized/CMS/AHCA/contract files. |
| **Priority order** | Legal → Company → Project → Clinical → Person → Personal → INBOX. |

---

## Classification priority (as specified)

1. Legal matter (litigation / evidence / court)
2. Specific company
3. Specific active project
4. Medical / clinical reference
5. Person
6. Personal
7. General reference
8. Inbox / Review if uncertain

## Sensitive categories detected

PHI / patient information · SSN / tax ID · banking / financial account ·
credentials / passwords · DEA / NPI / licensing · legal privileged ·
employment records.

## Duplicate signals

`(1)` suffixes · "Copy" · "Final Final" · "New" · "Updated" · "Revised" ·
`rev\d` / `v\d` · "Draft" · "Old" · "Backup" · "Duplicate" · "Untitled" ·
identical filename+size · same stem with multiple versions.

---

## Test results (offline, no Drive needed)

```
python3 test_engine.py     ->   30 passed, 0 failed
```

Covers: taxonomy integrity · classifier routing (13 real-world filenames) ·
duplicate detection · sensitive detection (6 categories) · rename protection ·
naming standard.

---

## Files

| File | Purpose |
|---|---|
| `taxonomy.json` | The full 01–10 folder taxonomy (machine-readable) |
| `drive_organizer.py` | The engine (auth, scan, classify, dedupe, move, report) |
| `test_engine.py` | Offline test suite — 30 assertions |
| `state/last_plan.json` | Written by `--dry-run` (the plan) |
| `state/folder_index.json` | Written by `--build-tree` (path → folder ID) |

---

## Reporting output (produced on `--dry-run`)

The run emits: total files reviewed · files moved · files renamed · folders created ·
potential duplicates · files needing manual review · sensitive documents identified ·
questionable sharing permissions · orphaned/abandoned projects · major organizational
problems · and an **EXECUTIVE ATTENTION REQUIRED** list.

---

## Open design decisions for Eddie

1. **`REVIEW` vs `08 — INBOX`** — both exist. Spec says low-confidence → INBOX;
   the instruction list also names a `REVIEW` folder. Currently: low confidence → INBOX,
   flagged-but-unclear → REVIEW. Confirm or collapse into one.
2. **Legal matter folder format** `[Year] — [Client/Party] — [Matter Name]` is templated
   but not auto-created — matter identity needs your input; guessing would misfile evidence.
3. **`05 — PEOPLE` person folders** `[LAST], [First] — [Role/Org]` need real rosters.
   The engine currently stops at the category level rather than inventing names.
