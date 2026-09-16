# PAPERCLIP SNAPSHOT — RESTORE CONTINGENCY
**Status: REHEARSED AND VERIFIED. Not executed.** Paperclip was retired on 2026-09-12 in favour of the
Hermes-native workforce. This document preserves the ability to bring the 2026-08-03 org back if that
decision is ever reversed.

---

## HEADLINE

**The snapshot IS restorable.** PostgreSQL major version matches, schema matches exactly, and the
whole restore was **rehearsed end-to-end with verified output**.

| Check | Result |
|---|---|
| Snapshot `PG_VERSION` | **18** |
| Live `PG_VERSION` | **18** (server 18.1) |
| `pg_upgrade` needed? | **No** — same major |
| Schema skew? | **None** — 157 tables both sides; migrations **182 / 182** |
| Live data at risk? | **Effectively none** — live holds 186 rows across 5 tables, **0** in companies/agents/issues/secrets |
| Restore duration | **~6 seconds** (12,509 rows, 55 MB) |
| Atomic? | **Yes** — one `BEGIN…COMMIT`; verified that a failed attempt leaves the target untouched |

**Independent corroboration of the recovery.** The rehearsal restore produced **2 companies, 72
agents, 148 issues, 46 secrets** — exactly the figures obtained by parsing the dump directly. Two
independent methods, same result. The recovered org data is sound.

---

## WHY THE STOCK RESTORE PATH DOES NOT WORK HERE

**Verified by rehearsal, not assumed.** This host has **no `psql`/`pg_dump`/`pg_restore` binary
anywhere**, and Paperclip 2026.722.0 ships **no restore CLI** (only `db:backup`). Paperclip's library
restore fails twice:

1. `psql error: spawn psql ENOENT`
2. `ERROR: syntax error at or near "1" [statement: COPY "drizzle"."__drizzle_migrations" ... FROM stdin;]`
   — **postgres.js cannot execute an inline `COPY … FROM stdin` payload**, and the dump has **35 such blocks.**

**Fix:** `/opt/data/scripts/paperclip_restore_copyaware.mjs` feeds each COPY block through
postgres.js's streaming `.writable()` COPY API (payload never re-encoded). **Rehearsed successfully
end-to-end.** Do not attempt the restore from the CLI or library as-is.

---

## THE TWO RISKS THAT ACTUALLY MATTER

### 1. SECRETS KEY MISMATCH — the silent killer
The live `secrets/master.key` and the snapshot's **are different files**
(md5 `2a885778…` vs `3896b441…`). All **46** restored secret rows are `local_encrypted_v1`
ciphertext and decrypt **only with the snapshot key.**

> **Skip the key swap and 44 agents' `hermes_gateway` apiKey `secret_ref` fails to resolve — the
> restored fleet cannot authenticate, and it fails quietly.**

The live instance holds **0** company_secrets, so swapping the key destroys nothing.

### 2. The dump contains PLAINTEXT credentials
`agents.adapter_config` stores at least one adapter **apiKey in the clear** alongside the secret_refs,
plus encrypted material and business/clinical content (NUR- issue titles, hiring and research
directives, 149 document bodies). Treat the 2.3 MB `.gz` (~40 MB raw) as **confidential — do not copy
it off-host, into chat, or into logs.** After restore that content is readable through the board UI by
anyone with instance access.

---

## PROCEDURE (condensed — full detail in the delegation transcript)

1. **Do NOT stop the control plane first.** The embedded PostgreSQL (`:54329`) is a **child of the
   `paperclipai` node process** (`npm exec → sh → node → postgres`). Stopping it kills PG and the
   restore has nothing to connect to. Restore while it runs; restart at step 8.
2. **Preflight** — `python3 /opt/data/scripts/paperclip_server_manager.py status` (expect
   `healthy=true db_healthy=true`).
3. **Dry-run** the driver against the snapshot (parses 1,405 statements / 35 COPY blocks / 12,509 rows,
   sends no SQL).
4. **Capture rollback** — `paperclipai db:backup` of the current empty DB (~36.7 KB).
5. **Preserve the live secrets key** (`master.key.live-<ts>`, `chmod 600`).
6. **Run the restore** — one connection, ~6 s, DROPs + re-creates all 157 tables.
   **Run at :20 past the hour** (automatic backups fire at HH:10) and **not while agents are mid-run.**
7. **Swap the secrets key** — copy the snapshot's `master.key` in, `chmod 600`.
8. **Verify** — `paperclip_db_verify.mjs`: expect 157 tables, 182/182 migrations, companies
   `999ff375` (Nuratech.ai, NUR, counter 147) + `425ddbd7` (NURA Imaging SaaS Division), **agents 72,
   issues 148**, secrets 46.
9. **Restart** the control plane so it drops stale connections and re-reads the new key. The manager's
   `stop()` only acts on a pidfile that can be stale — **pin the real group leader first** (anchor the
   `pgrep` pattern with `^` so it cannot match your own shell).
10. **Fix config drift** — `mcp.env` points at company `58ddc931…`, which **exists in neither DB**
    (confirmed: it 404s and appears in no local backup). Repoint to `999ff375…` and **mint a fresh
    API key** — `board_api_keys` is empty in the dump, so the old `pcp_board_bc61…` token will not
    authenticate.

---

## ROLLBACK — both moves rehearsed

1. **Database.** Run the same driver against the step-4 backup. **Verified in a throwaway cluster on
   `:54398`:** `RESTORE-OK statements=1405 copy_blocks=5 copy_rows=186`, and the result was exactly
   the live state (157 tables, 182/182 migrations, 0 companies/agents/issues, user `local-board`,
   environment `99489c73…`, 1 instance_setting, 1 user_role = instance_admin, 0 secrets).
2. **Secrets key.** Copy `master.key.live-<ts>` back and restart so the old key is re-read.

**If a restore dies mid-run, do nothing** — the transaction rolls back and the live DB is untouched.
No partial-state cleanup needed.

**Nuclear option** (only if the PG data directory itself is damaged): stop → move the datadir aside →
`paperclipai onboard --yes` to recreate a clean, fully-migrated cluster → then restore the step-4 backup.

---

## TWO WARNINGS

- **DO NOT use the physical datadir route.** The snapshot tree contains **`db_corrupted_20260731`** —
  evidence that cluster was damaged on 2026-07-31 (which is why dumps exist at all) — and its
  `postmaster.opts` references a now-deleted npm prefix. **The SQL dump from `data/backups` is the
  sanctioned artifact**; a datadir swap would import a previously-corrupted cluster.
- **Extension/superuser dependencies.** The dump does `CREATE EXTENSION IF NOT EXISTS fuzzystrmatch /
  pg_trgm` (both present in this embedded build — confirmed in rehearsal) and
  `SET LOCAL session_replication_role = replica`, which **requires superuser.** On a locked-down role
  or a Postgres without contrib the restore aborts there — and, being atomic, **rolls back cleanly.**

---

## POST-RESTORE CONFIG DRIFT (things that become stale)

| Item | Before | After |
|---|---|---|
| Environment id | `99489c73-bf04-4751-9afb-1733080a5487` | `c58ebac0-fe20-4b0c-a11d-3d0338d97864` |
| `mcp.env` company | `58ddc931…` (404s — in neither DB) | `999ff375…` |
| API key | empty | must be re-minted |

Anything hard-coding the current environment id becomes stale. Restart is about **cache/in-memory
state, not schema** — prepared statements survive because the schema is structurally identical.

---

## BOTTOM LINE

Restoring is a **6-second, atomic, rehearsed operation with a verified rollback.** The org is not
lost. But restoring buys back a **five-week-old copy of a system that stalled** — 145 of 148 issues
blocked and one agent holding 91% of the board. The data is now on the Notion board where it can be
worked; **the restore is a contingency, not a plan.**
