#!/usr/bin/env bash
set -euo pipefail

HOME=/opt/data/home
export HOME

status_file=/opt/data/cron/output/skill-availability-watchdog.txt
mkdir -p /opt/data/cron/output

missing=()
for s in segment-anything-model nutrition-analyzer communication productivity godmode research sleep-analyzer smart-home hermes-internals planning weightloss-analyzer yuanbao; do
  if ! find /opt/data/skills -maxdepth 3 -type d -name "$s" | grep -q .; then
    missing+=("$s")
  fi
done

if [ ! -f "$HOME/.hermes/google_token.json" ] || [ ! -f "$HOME/.hermes/google_client_secret.json" ]; then
  gws="google-workspace: missing OAuth files"
else
  gws="google-workspace: ready"
fi

if [ ${#missing[@]} -eq 0 ] && [ "$gws" = "google-workspace: ready" ]; then
  : > "$status_file"
  exit 0
fi

{
  printf 'Status:\n'
  printf -- '- %s\n' "$gws"
  printf -- '- missing_skills: %s\n' "${missing[*]}"
  printf -- '- note: manual installation/source required for missing skills\n'
} | tee "$status_file"