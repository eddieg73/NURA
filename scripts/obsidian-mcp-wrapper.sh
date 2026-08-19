#!/bin/bash
# Obsidian MCP wrapper — the vault path + the sealed creds (0600!)
export VAULT_PATH="/opt/data/Obsidian Vault"
ENV_FILE="/opt/data/profiles/nura/.env"
[ -f "$ENV_FILE" ] && while IFS='=' read -r k v; do
  case "$k" in
    OBSIDIAN_*) export "$k=${v//\"/}" ;;
  esac
done < <(grep -E '^OBSIDIAN_' "$ENV_FILE" || true)
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
cd "/opt/data/profiles/nura/home/vault-real" && exec npx -y obsidian-mcp . 2>/dev/null
