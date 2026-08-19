#!/bin/bash
# Backend log after URL fix + reachability probe from the backend
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.61.71.211 'echo "=== log ==="; docker logs docsgpt-oss-backend-1 2>&1 | grep -iE "error|exception|refused|resolve|connect" | tail -5; echo "=== backend reachability (python) ==="; docker exec docsgpt-oss-backend-1 python -c "import urllib.request; print(urllib.request.urlopen(\"http://127.0.0.1:11434/\", timeout=5).status)" 2>&1 | tail -1; echo "=== host tunnel ==="; ss -tlnp 2>/dev/null | grep 11434 | head -1'
