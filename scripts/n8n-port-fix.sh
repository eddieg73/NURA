#!/bin/bash
# n8n port-map add (5678:5678) + recreate + verify
ssh -o BatchMode=yes -o ConnectTimeout=10 -i ~/.ssh/id_nura_clean root@195.35.32.113 'P=/etc/dokploy/compose/n8n-n8n-6tp2rd/code/docker-compose.yml && echo "=== current ports ===" && grep -n -A2 "ports\|5678" $P | head -10 && python3 - <<PYEOF
p = "$P"
s = open(p).read()
if "5678:5678" not in s:
    # find the n8n service block and add ports after its image line
    marker = "image: n8nio/n8n"
    if marker in s:
        s = s.replace(marker, marker + "\n    ports:\n      - \"5678:5678\"", 1)
        open(p, "w").write(s)
        print("ports added")
    else:
        print("MARKER NOT FOUND — image name differs")
        import re
        m = re.search(r"^  [\\w-]+:\n(    image: [^\\n]+)", s, re.M)
        print("first service image:", m.group(1) if m else "none")
else:
    print("ports already present")
PYEOF
grep -n "5678:5678" $P | head -1 && cd /etc/dokploy/compose/n8n-n8n-6tp2rd/code && docker compose up -d --force-recreate n8n 2>&1 | tail -1 || docker compose up -d 2>&1 | tail -1; sleep 12; echo "=== verify ===" && curl -s -m 6 -o /dev/null -w "edge-5678: %{http_code}\n" http://127.0.0.1:5678/healthz 2>/dev/null'
