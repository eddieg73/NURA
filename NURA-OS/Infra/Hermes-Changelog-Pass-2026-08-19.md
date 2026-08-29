# The Hermes changelog pass (2026-08-19) — the 2,746 commits distilled

The running install: v0.20.0 (2026.8.3). The latest release: v0.20.2 (2026.8.16). The span: v2026.7.30 → HEAD = 2,746 commits.

## What matters for the NURA stack

### The features worth taking
1. **hermes peer** — bot-to-bot DMs across machines and gateways. The Paperclip's agents on the Lab could DM the Hermes directly. The future multi-node fabric.
2. **MCP: the 2026-07-28 stateless protocol** — the newer MCP spec. Our MCP lanes (the GitHub, the B2, the Kaggle) will migrate with the upgrade automatically.
3. **Project-skill quarantine + per-repo trust gate** — the security for the community skills we installed (the 686-skill arsenal).
4. **NVIDIA SkillEvaluator Tier 1 scan on skill installs** — the license + security scan per install.
5. **Cron: misfire catch-up + configurable media-send timeout** — the directly relevant to the 8PM eMedical audit and the briefing crons.
6. **Per-plugin durable data directory** — the plugin state survives updates.

### The fixes worth taking
1. fix(gateway): never construct SessionDB on the event-loop thread — stability.
2. fix(cron): manual runs no longer silently drop media attachments — our crons attach media.
3. fix(state): v25 prompt dedupe degrades gracefully on a contended DB.
4. fix(api-server): stop persisting the virtual model alias as a session's model.
5. fix(gateway): grace window keeps first-call goal persistence on healthy DBs.

## The apply decision
- The delta v0.20.0 → v0.20.2 is PATCH-level (13 days), not a breaking jump.
- The backup is armed; the rollback path is known (re-pull the v0.20.0 tag).
- The gate: the founder's chosen window (the root-level rebuild or the docker recreate; the gateway blinks).

## The no-action items (the desktop/OS-specific)
The Electron desktop fixes, the Windows process-scan bounds, the macOS specifics — the not applicable to this headless VPS.
