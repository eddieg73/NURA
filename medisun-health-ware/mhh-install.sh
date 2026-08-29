#!/usr/bin/env bash
cd /opt/data/medisun-health-ware
uv venv .venv --quiet 2>&1 | tail -1
uv pip install --python .venv/bin/python fastapi uvicorn 2>&1 | tail -4
