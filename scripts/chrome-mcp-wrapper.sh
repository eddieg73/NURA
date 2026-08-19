#!/bin/bash
# Chrome MCP wrapper — the headless-chrome + the sealed keys (0600!)
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
export CHROME_PATH="/opt/data/profiles/nura/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
export PLAYWRIGHT_BROWSERS_PATH="/opt/data/profiles/nura/.cache/ms-playwright"
exec npx -y chrome-mcp 2>/dev/null
