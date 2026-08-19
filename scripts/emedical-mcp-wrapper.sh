#!/bin/bash
# eMedical FHIR MCP wrapper — the sealed EMED creds + the eMedical FHIR base (never in config!)
ENV_FILE="/opt/data/profiles/nura/.env"
[ -f "$ENV_FILE" ] && while IFS='=' read -r k v; do
  case "$k" in
    EMED_*|FHIR_*) export "$k=${v//\"/}" ;;
  esac
done < <(grep -E '^(EMED_|FHIR_)' "$ENV_FILE" || true)
export FHIR_BASE_URL="${FHIR_BASE_URL:-https://fhirbackup.emedpractice.com:8443/r4/}"
export FHIR_AUTH="${FHIR_AUTH:-none}"
export FHIR_ACTIVE_KEY="${FHIR_ACTIVE_KEY:-emedical-nura-key}"
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
exec npx -y fhirhydrant 2>/dev/null
