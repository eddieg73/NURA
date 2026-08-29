# CLAUDE CODE PYTHON REWRITES — DEEP REVIEW PASS (2026-08-06, the founder's directive)

**The deeper audit, executed: the fork-by-fork clone + the security-scan + the architecture-diff. The earlier pass (the research + the sandbox-extract + the 6-flag-doc) = the foundation; THIS = the code-level verification.**

## THE FORKS EXAMINED (cloned to /opt/data/review-lab/)
| Fork | Files | Structure | Scan |
|---|---|---|---|
| GPT-AGI/Clawd-Code ★522 | 165 .py | the full reconstruction: tool-system · command-system · context-system · permissions · the legacy-REPL · the tool-parity-tests | CLEAN (no shell=True/eval/base64/pipe-bash/hardcoded-secrets!) |
| mzpatrick0529-mzyh/claw-code ★123 | 67 .py | the leaner rewrite: src/prefetch · src/tools · projectOnboardingState · src/state/ | CLEAN (same scan!) |

## THE FINDINGS (the scientist's notes)
1. **The thin-core thesis CONFIRMED**: the 512K-line TS original (~1,900 files!) reconstructs into 165/67 Python files — the real agent-core is THIN; the bulk of the original was the product-surface (the platforms/adapters/UI!). The Hermes-architecture (the narrow-waist + the fat-edge!) = the SAME philosophy, natively.
2. **The security-scans**: no obvious injection/backdoor patterns in the cloned snapshots (the grep-limit: the top-level patterns — the deeper per-file audit = the next pass if needed!)
3. **The legal posture UNCHANGED**: the source-derived forks = the derivative-of-the-leak (the license-claims don't cure the provenance!) — the REVIEW-ONLY doctrine holds.
4. **The NURA-application**: the patterns (the tool-parity · the permissions-systems · the context-systems!) = the study-material for our OWN core (never the code!)

## THE MCP ADMINISTRATOR (the same directive's tool — built in parallel)
- /opt/data/scripts/mcp-admin.py (inventory | health | spinup | teardown!)
- The skill: mcp-administrator (the lifecycle-doctrine + the governance!)
- The GitHub-verified solutions: mcp-router ★2,117 (the unified-manager-app!) + mcpm.sh ★986 (the CLI-registry!) — cloned for the patterns; the NURA-admin = the native-lightweight (the hermes-CLI-backed!)
