# NURA CREDENTIAL REGISTRY (2026-08-09 — the CTO-consolidation!)

## The canonical state: 135 sealed vars — the dedup + the status!

## The DUPLICATES (the consolidation-targets!)
| Canonical | Aliases (the merged!) | Status |
|---|---|---|
| KIMI_API_KEY | MOONSHOT_API_KEY (same-key!) | ⚠️ INVALID (both rejected!) |
| LANGGRAPH_API_KEY | LANGRAPH_API_KEY · LANGSMITH_API_KEY | ⚠️ the sk-lf-key (the observability-lane; the endpoint-untested!) |
| NOTION_MCP_TOKEN | NOTION_API_KEY · NOTION_API_TOKEN | ✅ LIVE (the ntn-token — the workspace-visible!) |
| OPENROUTER_API_KEY | OPENROUTER_OR_KEY | ✅ LIVE (the models-catalog ✓!) |
| HF_TOKEN | HF_TOKEN_2 | ✅ LIVE (the whoami ✓!) |
| GHL (9 vars!) | GHL_API_KEY ×3 · GHL_API_TOKEN ×3 · GHL_MCP_API_KEY ×3 | ⚠️ the scopes-limited (the 401s!) |

## The STATUS-LEDGER (the live vs the dead!)
- ✅ LIVE (verified 08-15 probes): HF_TOKEN (whoami 200) · KIMI (moonshot models 200 — the invalid-issue FIXED!) · NVIDIA (models 200) · DEEPSEEK (models 200) · LANGGRAPH (smith 200 — untested→LIVE) · OPENROUTER ×2 · EXA · FIRECRAWL · NOTION_MCP_TOKEN · TWILIO ×4 · META_DATASET_QUALITY · MIRTH ×3 · HOSTINGER · RUNPOD
- ⚠️ PENDING/INVALID: ELEVENLABS (BOTH stored values rejected — 400 invalid_api_key; the a1727f drop = same bad value; founder must generate a NEW key in the console: sk_ format) · **VAPI (08-15 drop: 401 Invalid Key — possible private/public key mixup; founder re-check the VAPI dashboard)** · HONCHO (tenant cold-storage — resume from their console) · 9ROUTER (endpoint unresolved — api.9router.ai no DNS; key format 12-char untested) · CLAUDE-API (api.claude.ai unresolved from this box) · E2B (endpoint 404-validated; key untested) · GHL (scopes) · ANTHROPIC · GOOGLE_API_KEY (session-token) · OPENEVIDENCE · TAVUS (missing) · GROK (missing)
- ✅ VERIFIED 08-15: GEMINI (REAL key sealed + probed — gemini-flash-latest "OK" via founder's curl + vision lane gemini-3-flash-preview ✓; project 781459835625) · N8N_API_KEY (53 workflows inventoried) · GITHUB_FINEGRAIN_TOKEN (sealed — probe pending) · HERMES_WEBUI (admin creds sealed)
- ❓ UNKNOWN: OLLAMA_API_KEY (58-char sealed — ollama.com/api/keys untested) · NOTION_MCP_PASSWORD (Fnjkerqf — purpose unlabeled)
- 📌 NOTES: GHL ticket 5999916 = 2 sub-account transfer (open with GHL) · E2B drop was labeled "Alibaba" (e2b_ prefix = E2B sandboxes — stored as E2B_API_KEY) · caveman repo (JuliusBrussee/caveman) pending skill-eval

## The SOP (the key-drop flow — from now on!)
1. SEAL: the .env-append + the 0600 ✓
2. PROBE: the live-API-test (the endpoint + the auth!) → the status!
3. REGISTER: this registry-doc → the status-column!
4. WIRE: the MCP/CLI-lane if the service has one!
5. DOC: the lane + the access-in-the-vault!
6. THE FAILURE: the invalid-key → the founder's-re-drop-flagged (the status-⚠️, never-silent!)

## The maintenance
- The weekly-re-audit: the registry-vs-the-.env (the duplicates + the statuses!)
- The monthly-cleanup: the dead-keys-purged (with the founder's-ok!)
