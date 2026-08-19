#!/bin/bash
cd /opt/data/hermes-ecosystem/hermes-agent-self-evolution
.venv/bin/python -c "import dspy, openai; print('deps OK')"
.venv/bin/python -m evolution.skills.evolve_skill --help 2>&1 | head -12
