#!/bin/bash
export PATH="/opt/data/profiles/nura/bin:/opt/data/profiles/nura/.local/bin:/opt/hermes/bin:/opt/hermes/.venv/bin:$PATH"
cd /opt/data/hermes-ecosystem/google-flow-browser-mcp && exec node src/index.js
