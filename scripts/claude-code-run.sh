#!/usr/bin/env bash
# Claude Code multi-provider launcher (verified 2026-08-02)
# Usage: claude-code-run.sh <deepseek|gemini|claude|openrouter> [claude args...]
set -euo pipefail
ENV=/opt/data/profiles/nura/.env
CC=/opt/data/profiles/nura/node-packages/node_modules/@anthropic-ai/claude-code/cli-wrapper.cjs

get() { grep "^$1=" "$ENV" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'"; }

PROV="${1:?provider required: deepseek|gemini|claude|openrouter}"
shift

case "$PROV" in
  deepseek)
    # VERIFIED: api.deepseek.com/anthropic returns real completions (deepseek-v4-flash)
    export ANTHROPIC_BASE_URL="https://api.deepseek.com/anthropic"
    export ANTHROPIC_AUTH_TOKEN="$(get DEEPSEEK_API_KEY)"
    export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-deepseek-chat}"
    ;;
  gemini)
    # Gemini via OpenRouter Anthropic-compat (google/* models) — reliable lane
    export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
    export ANTHROPIC_AUTH_TOKEN="$(get OPENROUTER_API_KEY)"
    export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-google/gemini-2.5-flash}"
    ;;
  openrouter)
    export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
    export ANTHROPIC_AUTH_TOKEN="$(get OPENROUTER_API_KEY)"
    export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-anthropic/claude-sonnet-4.6}"
    ;;
  claude)
    # Native Anthropic — requires ANTHROPIC_API_KEY drop in .env
    if ! get ANTHROPIC_API_KEY >/dev/null 2>&1 || [ -z "$(get ANTHROPIC_API_KEY)" ]; then
      echo "ANTHROPIC_API_KEY missing — drop it in .env (0600)"; exit 1
    fi
    export ANTHROPIC_BASE_URL="https://api.anthropic.com"
    export ANTHROPIC_API_KEY="$(get ANTHROPIC_API_KEY)"
    export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-claude-sonnet-4-6}"
    ;;
  *) echo "provider must be deepseek|gemini|claude|openrouter"; exit 1 ;;
esac

exec node "$CC" "$@"
