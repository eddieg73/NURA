#!/bin/bash
# DOCSGPT COMPLETION: ingest the medical corpus -> the agent's sources
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@72.60.163.140 'ls /opt/nura-corpora/textbooks/chunk/ | head -3; du -sh /opt/nura-corpora/textbooks/chunk/ 2>/dev/null | head -1' 2>&1 | head -4