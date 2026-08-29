# Daily Self-Reflection — 2026-08-28

Cron run (silent, autonomous). Summary: **2 same-pass fixes applied (moltbook + emos/playwright root-caused); 1 real infra incident persists (LAB overload); local swap filled to 100%; 1 new recurring API-key noise signal.**

## Pass 1: Config Files
- `config.yaml` (active profile): sealed, 969 lines, `mcp_servers` present, model aliases/providers coherent. No drift.
- `.env`: **600** perms, all keys set, no empty/placeholder values (grep empty-check returned nothing). Clean.
- Compose: many deploy-target compose files exist under repos; **no local dockerd** (confirmed `docker info` → cannot connect; no dockerd/containerd proc). Compose is fleet-deploy-only; runtime orphans not assessable locally (consistent with doctrine). Static review only.

## Pass 2: Databases + Memory
- **Qdrant** (`:6333`, green): `garrido-kb` 925 pts, `nura-docs` 543 pts, `nura-os` 216 pts (grew 215→216). Healthy.
- **mem0** (OSS, qdrant back-end `/opt/data/profiles/nura/home/.hermes/mem0_qdrant`): `meta.json` collection `mem0` present, `collection/mem0` dir present, single stale `.lock.stale.bak` (cleanup artifact, not live). Healthy.
- **Redis** (`:6379`): PONG, dbsize=7, used_mem ~948K. Keys present. Healthy.
- **Postgres (paperclip one-instance)**: exactly ONE embedded proc (`paperclip-runtime/instances/default/db` @ **54329**). Doctrine satisfied.
- **Disk**: / 251G used / 387G = 65%; mem 22Gi avail / 31Gi. Fine.
- **SWAP (local)**: **4.0Gi/4.0Gi = 100% used** (43Mi free) — was 1.5Mi on 08-27. Local swap fully exhausted. 22Gi RAM avail ⇒ not thrashing, but monitor (likely a large build/agent run). Not critical; no action yet.

## Pass 3: Skills
- `skill-link-scan` → **747 indexed, 0 broken related_skills refs, 0 pruned markers.** Clean. No broken references found.

## Pass 4: Crons
- 87 jobs, all enabled.
- **Still-failing classes (recurring — same as 08-27, unfixed):**
  1. **"llama3.1:8b does not support thinking"** (~10 weekly): medical blog, self-improvement, space audit, clinical literature, marine forecast, drift audit, weekly snapshot, self-model review, competitive watch, obsidian-weekly. Jobs route to `deepseek-v4-flash-vision-exp` but a thinking flag reaches local `llama3.1:8b`. **Weekly — RE-FIRES TODAY (Fri). Needs intended-model decision (config mismatch). NOT auto-patched (consequential routing change).**
  2. **LAB overload** (infra) — see incident.
- **FIXED same-pass:**
  - **moltbook morning/midday/evening** — was "Script not found: ...moltbook-human-checkin.py --part morning". Root cause: args inlined in `script` field (runner resolves bare filename only; no `command`/`Args` field used anywhere). Fixed → repointed to bare `moltbook-human-checkin.py` (script auto-infers part by time-of-day: <11 morning, <15 midday, else evening). Verified dry-run EXIT 0 (`[DRY RUN morning] ...`), jobs.json valid (87), backup `jobs.json.bak-reflect-1787905048`.
  - **emos gap audit** — was "playwright not importable". **ROOT-CAUSED:** greenlet shipped only `_greenlet.cpython-311*.so` but runtime is **Python 3.13.5** → ABI mismatch → `greenlet._greenlet` invisible → playwright.async_api import fails. FIXED: installed `greenlet==3.5.5` (cp313) into `/opt/data/profiles/nura/python-packages`. Verified: `from playwright.async_api import async_playwright` imports OK; `--selftest` passes.

## Pass 5: Critical Scripts (compile + smoke)
- All `*.py` compile clean (py_compile sweep, no FAIL).
- `legal-inbox-ingest.py`: COMPILE OK (email lane is a KNOWN silent drop — creds unset; returns 0). Expected.
- `swap-watchdog.py`: smoke → **Fleet ALERT: CLINIC SWAP CRITICAL 99%, LAB SWAP CRITICAL 94%.**
- `fleet-scan.py` / `swap-watchdog.py` (live SSH probe): see incident.
- `moltbook-human-checkin.py`: dry-run OK.
- `emed-gap-audit.py`: `--selftest` OK (SOAP/labs/Xray/CT/consult all matched; MRI open).

## INCIDENT (escalate — persists from 08-27)
**LAB node (72.60.163.140 / 1030183) — resource exhaustion.**
- Load avg **79.97 / 80.38 / 84.71** (8 cores, ~10x overloaded), swap **3856/4095 = 94%** (CRITICAL), mem 20823/32094 avail (~65%).
- Top consumer: `colibri qwen36` 14.2% mem (local LLM serve); + next-server, clickhouse, node worker.
- Read-only diagnosis; **NO remediation executed** (production node / approval-tier). Recommend: throttling/restart of the colibri qwen process; confirm load target.
- **CLINIC (72.61.71.211): swap 4037/4095 = 99%** (CRITICAL) but load 1.1 (normal), mem ~74% avail. Not thrashing; monitor / see what filled swap (elasticsearch/hermes/sidekiq).

## Pass 6: FIXED same-pass (evidence-first)
1. **moltbook x3 cron** → bare `moltbook-human-checkin.py` (removes unsupported inline args). Verified.
2. **emed gap audit** → `greenlet` cp313 installed (playwright lane unblocked). Verified.

## Pass 7: Log
This reflection appended. Delivered to cron destination.

## NEXT
- Escalate LAB overload: trim/restart `colibri qwen36` (top mem, extreme load); confirm load target.
- **Founder decision:** intended model for the ~10 weekly jobs hitting the llama3.1:8b thinking-routing mismatch (re-fires today) — disable llama3.1:8b in `moa.presets.default.reference_models` (config.yaml ~289-293) or correct reasoning pass-through.
- Investigate recurring `API server rejected invalid API key` on `/v1/models` (127.0.0.1, every ~10 min) — likely a health-check/monitor probe using a stale key.
- Monitor local swap (100%) + CLINIC swap (99%) — confirm no process growth.
