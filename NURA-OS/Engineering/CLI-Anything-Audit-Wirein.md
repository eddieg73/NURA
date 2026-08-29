# CLI-Anything — audit + wire-in (2026-08-28)

Date: 2026-08-28 · Operator: Hermes (CTO)
Source: HKUDS/CLI-Anything (Apache-2.0, active, 4.5k forks, 2.4k tests)
Skill: `gui-to-cli-harness` (the methodology) · Venv: `/opt/data/cli-anything-venv`

## The audit (evidence-first) — passed with one guard
- **Installer security: PASS.** All 79 registry CLIs use the `pip` install strategy (argv-array,
  no `shell=True`, no `curl|bash`). The risky `command`/shell path is ZERO in the current registry.
- **Supply-chain: bounded.** installs come from the repo's own `git+https://...` (Apache-2.0,
  active 08-21). Standard third-party trust; pin the package version for reproducibility.
- **Telemetry: ON by default → MUST disable.** `analytics.py` phones to PostHog + Umami
  (hardcoded endpoints) and fingerprints the env (detects which agent tool is calling).
  **Disable with `CLI_HUB_NO_ANALYTICS=1`** (docs confirm: 1/true/yes = off). Verification:
  `_is_enabled()` returns false when env is set.

## What it is (the truthful frame)
79 agent-native CLIs + a 7-phase methodology (`HARNESS.md`) + a pip package `cli-hub`.
NOT clinical (no OpenEMR/Mirth harness — our device-connectivity doctrine owns that).
It's a GENERAL capability multiplier for agent-ifying GUI/desktop tools.

## Wire-in (verified live)
- `cli-anything-ollama` → drives the sovereign dock Ollama (`--host http://127.0.0.1:11435`).
  Verified: `server status` = running; `generate text -m qwen2.5:3b -p "Reply exactly: OK"` → **OK**.
- `cli-anything-exa` → EXA_API_KEY valid; live search returned real CMS CY2026 risk-adjustment
  implementation memo (relevant to MA/RAF work).

## How to use
```bash
export CLI_HUB_NO_ANALYTICS=1
V=/opt/data/cli-anything-venv
# ollama (sovereign dock)
$V/bin/cli-anything-ollama --host http://127.0.0.1:11435 generate text -m qwen2.5:3b -p "..."
# exa
export EXA_API_KEY=$(grep '^EXA_API_KEY=' /opt/data/profiles/nura/.env | cut -d= -f2)
$V/bin/cli-anything-exa search --type fast -n 5 "..."
```

## Open / next
- `obsidian` harness needs the Obsidian app + Local REST API plugin RUNNING (it's a local REST
  wrapper, not just the vault). Stand up the plugin before installing that one.
- `n8n` harness (55+ cmds over the n8n REST API) — install + wire to our n8n instance next.
- Port the *methodology* to any NURA GUI tool we want agent-native (see `gui-to-cli-harness`).
