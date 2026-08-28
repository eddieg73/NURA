# CTO Session Ledger — 2026-08-28

Date: 2026-08-28 · Owner: Eddie (founder) · Operator: Hermes (CTO)
Mirrored to Notion master board: `NURA-Work-Update — the Master Board 🏥` (08-28 ledger).

## Decision
Make the model lane **free-first / sovereign** — stop depending on paid third-party inference that either needs credits or is retired. Stand up our own local inference and repin the fallback chain so Hermes survives any provider outage.

## What was done (verified)
1. **Sovereign model lane on the dock** — own Ollama `/opt/data/ollama-home/bin/ollama` (v0.33.1) on port **:11435**, model store `/opt/data/ollama-home/models`. Pulled `qwen2.5:3b` (1.8G) and **verified a real generation (~10s CPU)**.
2. **Provider + fallback** — registered Hermes provider `local_ollama` = `http://127.0.0.1:11435/v1` (no key). Fallback chain FREE-FIRST: `local_ollama/qwen2.5:3b` → `ollama(Lab)/qwen2.5:3b` → `ollama/deepseek-r1:8b`. Primary = `deepseek/deepseek-chat`.
3. **Paid lanes diagnosed dead** (live probe): nvidia `404` (empty key), openrouter `402` (insufficient credits), gemini `404` (model retired), anthropic credit-gated. This is the root cause of "backups don't work / need credits."
4. **Lab (srv1030183 / 72.60.163.140) root-caused** as **hypervisor-starved**: load ~78 on 8 vCPU, **91–92% steal** — not a credit problem. `systemctl restart ollama` un-zombied it; documented as unreliable under load → inference goes on the dock, Lab used for its model store only.
5. **Telegram gateway FIXED** — `.env` bot token was revoked/invalid (`getMe` → 401). Replaced with the valid `@Nuratechbot` token, restarted gateway via s6 (disabled the obsolete `gateway-default` duplicate). **Verified live:** `[Telegram] Connected to Telegram (polling mode)`, `60 commands registered`, `✓ telegram connected`.
6. **Surface (whitney, Windows)** confirmed on the tailnet (`100.77.239.3`, ping OK) but all ports firewalled — agent peer link prepared (`hermes peer add`), needs Surface-side firewall rule + `platforms.api_server.extra.host 0.0.0.0` to complete. (Open item.)

## Open items / next
- Complete the Surface Hermes agent peer link (firewall rule + api_server bind on the Surface).
- Decide whether to keep `deepseek` paid as primary or promote the dock `qwen2.5:3b` (faster, free) — currently primary is deepseek because it's the largest live model.

## Evidence
- Dock generation: `RESPONSE: A common preventable cause of death in the US is cardiovascular disease.` (~10s)
- Deepseek getMe/lane: 200 live · nvidia/openrouter/gemini: 404/402/404 dead
- Telegram: `[Telegram] Connected to Telegram (polling mode)` / `✓ telegram connected`
