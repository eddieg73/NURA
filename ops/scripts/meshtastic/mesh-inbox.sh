#!/bin/bash
# Mesh inbox watchdog: prints NEW routed mesh events (silent when none).
# Delivered verbatim by the Hermes cron (no_agent) as 📡 MESH updates.
python3 /opt/data/scripts/meshtastic/mesh-router.py 2>/dev/null
