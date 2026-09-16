# NURA Estate Audit — Skills · Artifacts · Plugins · Monitoring Coverage

**Date:** 2026-09-13
**Founder directive:** *"Review all skills, artifacts, plugins and make sure all is working, develop
skills needed to monitor and prevent systems from going down."*
**Commits:** `9e9546d` (audit + watchdogs), `1b623fe` (watchdog-patterns skill)

---

## 1. Skills — 885 SKILL.md files

| Check | Result |
|---|---|
| Missing frontmatter | **0** |
| Missing description | **0** |
| Tiny / stub files | **0** |
| Descriptions > 160 chars | 76 (bloat, not breakage) |
| Empty directories | 6 |
| Duplicate names | 85 |

**Verdict: structurally healthy.** No broken skill.

**The 85 "duplicates" are NOT a defect.** All but one are byte-identical copies across two separate
profile trees — `/opt/data/profiles/nura/skills/` (this profile) and `/opt/data/skills/` (the
**default profile's**, owned by a different session and deliberately NOT touched). One genuine
divergence exists: `comfyui` (24,117 vs 24,075 bytes). Left alone rather than "reconciled" — it is
another profile's data.

**Verified with a real YAML parser, not regex.** An initial regex-based validator reported
`a2a-bind-fail-prevention` with a 1-character description; the frontmatter is actually **valid YAML**
— a `>` block scalar resolving to a proper 280-char description. **The validator was wrong, not the
skill.** Worth recording: a naive frontmatter check produces false defects.

---

## 2. Artifacts — 1,300 scripts scanned

**1 syntax error found and FIXED.**

`NURA/scripts/paperclip-product-companies.py` — a description string group opened with `(` was closed
with `},` instead of `),`. Note the fix required care: correcting one instance merely moved the
`SyntaxError` further down, so **all** instances were fixed and the file verified to compile with
structure preserved (2 title keys, 2 assignee keys intact). A one-line fix would have looked
successful while remaining broken.

---

## 3. Plugins — 75 MCP servers

75 declared · 61 enabled · **0 malformed**. 1 plugin directory entry. No defects.

---

## 4. Coverage — and the false all-clear I had to correct

**My first coverage check reported `UNMONITORED SYSTEMS: 0`.** That was wrong, and the reason is
reusable: it keyword-matched each system against a blob of every job's name **+ full prompt**. At 97
jobs that matches nearly anything — *"marine forecast"* was credited with monitoring disk/space, and
*"self-improvement, evolution review, marine forecast"* with monitoring external endpoints.

**A substring match against prose is not evidence of coverage.**

Corrected rule: **a system is monitored only if a job NAMES it in the job name or monitor/script
path.** Re-run under that rule, the count went **0 → 7**.

A sibling trap in the same check: it reported `monitor-gated: 0` minutes after I created a
monitor-gated job — because the real field is **`monitor_script`**, not `monitor`. **Check field names
before trusting a zero.**

### The 7 genuinely unwatched systems — now covered

`gateway process` · `qdrant` · `redis` · `cron roster` · `Notion` · `n8n` · `external endpoints`

Built **`estate-watchdog.py`** (+ `estate-monitor.py` shim), cron **`estate watchdog` `2f30c0ee660a`**,
every 6h at :30, monitor-gated.

---

## 5. The failure mode nothing was catching

**A cron that silently stops firing is invisible: it produces no output, so it looks exactly like a
job with nothing to report.** The alarm and the all-clear are the same signal.

Section C of the watchdog checks **schedule adherence** — that the smoke detector is still *wired in*,
not merely that it is not beeping. Two distinct failures, both flagged:

- **OVERDUE** — did not run within its window (window computed from the cron expression).
- **ON TIME BUT ERRORING** — `last_status == error`. A job can fire perfectly and fail every time.

### Finding: `emos gap audit` — a system down for weeks, hidden by disabling the alarm

Daily job, **DISABLED**, last ran 2026-09-06. Its output artifacts tell the story:

```
login=False multiple-login-alert=False logout=failed scanned=0
patients=0 missing-labs=0 missing-imaging=0 missing-consults=0 soap-gaps=0
note: login blocked: login exception: TimeoutError
```

It produced a **437-byte file every night for weeks** — byte-identical in size — scanning **zero
patients**, because it could not log into eMedical. It was then **disabled rather than fixed**.
**Disabling a noisy job converts a visible failure into a silent one.** Still open; needs the eMedical
login investigated.

### Finding: `evolution review` — root cause confirmed, already remediated

Failed 2026-09-01 with:

```
TimeoutError: Timed out waiting for the TERMINAL_CWD read lock after 660s — another cron job
(a workdir writer, or long-running readers) has held it for longer than the cron inactivity limit.
```

**Root cause proven by collision analysis.** Only 4 jobs declare a workdir — all of them
`/opt/data/Obsidian Vault`:

| workdir holder | expr | runs at 08:00? |
|---|---|---|
| `obsidian-morning` | `0 8 * * *` | **YES** |
| `obsidian-nightly` | `0 22 * * *` | no |
| `obsidian-weekly` | `0 18 * * 5` | no |
| `obsidian-health-check` | `0 21 * * 0` | no |

`evolution review` ran `0 8 1 * *` — **08:00 on the 1st** — the same minute `obsidian-morning` holds
the vault lock. It fired once, died, and looked quiet for 30 days. **The current schedule is
`45 9 1 * *` (09:45), which avoids all four vault windows — so the collision is already fixed.**

**Important consequence:** a *monthly* job that errored on 09-01 keeps `last_status=error` until
2026-10-01 even though the cause is resolved. **An error flag on an infrequent job is a claim about
the LAST RUN, not the current configuration.** The watchdog prints the error date for exactly this
reason — a stale monthly error and a live daily error must stay distinguishable, or the report trains
its reader to ignore it.

### The pattern worth stating plainly

**Both of these were already written down in `watchdog-patterns` as known failure modes** — including
"`evolution review`, failed 09-01, undetected 9 days". **Writing a failure in a document did not put a
watcher on it.** That is the same dead end as a skill prescribing "P2 watch" with no watcher behind
it. Hence the standing rule now in the skill:

> **If a document says "watch" or "monitor", name the job — or the advice is noise.**

---

## 6. False alarms removed from the watchdog (both my own instrument bugs)

| False alarm | Why it was wrong | Fix |
|---|---|---|
| `docker: 0 containers` | This host has the docker CLI but **no daemon**; fleet containers live on clinic/lab/edge | Check `docker info` first; report **n/a** when absent |
| `lane state watchdog: NEVER RUN` | Flagged a cron created **4 minutes earlier** | `jobs.json` has `created_at` — grant one full expected window of grace |

**A watchdog that cries wolf on an expected condition gets muted**, and the mute is exactly how the
next real outage hides. Expected-down entries must be excluded by construction.

---

## 7. Final verified state

```
A. LOCAL SERVICES
   [OK  ] gateway process       pid=1515118 alive=True api=404
   [OK  ] qdrant :6333          ok
   [OK  ] redis :6379           ok
   [OK  ] docker containers     n/a — no local daemon (fleet on clinic/lab/edge)

B. EXTERNAL ENDPOINTS
   [OK  ] nuratech.ai           HTTP 200
   [OK  ] pay.nuratech.ai       HTTP 307
   [FAIL] carepilot.nuratech.ai HTTP 000   <- known open (AWS ALB dark, origin healthy)
   [FAIL] api.nuratech.ai       HTTP 000   <- known open (skill api-gateway-public-fix)

C. CRON SCHEDULE ADHERENCE
   [FAIL] evolution review      ON TIME BUT ERRORING (last 2026-09-01) <- cause already fixed, stale flag
```

Deterministic `--state` across runs · heartbeat fresh · exit codes correct.

---

## 8. Monitoring now in place

| Watchdog | Covers | Schedule | Cron |
|---|---|---|---|
| `lane-state-watchdog.py` | gateway platform lanes (the 6-day A2A class) | `0 */6 * * *` | `a67d954e02c5` |
| `estate-watchdog.py` | the 7 unwatched systems + cron adherence | `30 */6 * * *` | `2f30c0ee660a` |

Both are **monitor-gated** (silent unless the state string changes) and both carry a **heartbeat with
a run counter** so a dead watchdog cannot masquerade as a healthy system.

## 9. Skills written / updated

- **`silent-lane-degradation-prevention`** (new) — the self-reported-status-with-no-consumer class.
- **`watchdog-patterns`** (updated) — coverage-by-probe (not prose) · schedule adherence · false-alarm
  discipline · self-liveness · determinism-as-contract.
- **`a2a-bind-fail-prevention`** (updated) — recorded the "P2 watch with no watcher" dead end and added
  a verify-by-socket step, because the flag was still `true` after the lane was provably healthy.

## 10. Open items for the founder

1. **`emos gap audit` disabled with a real failure behind it** — eMedical login `TimeoutError`,
   scanning 0 patients. Fix the login or record the disable as deliberate with a date.
2. **`carepilot.nuratech.ai` = 000** — AWS ALB, both IPs dark; origin `srv1682494` healthy. Gated as
   R-CAREPILOT-1.
3. **`api.nuratech.ai` = 000** — public door.
4. **4 lanes still degraded in `gateway_state.json`** (email, signal, bluebubbles, msgraph_webhook) —
   the lane watchdog is clocking them and will surface them past threshold.
