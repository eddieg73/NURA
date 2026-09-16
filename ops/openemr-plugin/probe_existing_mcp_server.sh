#!/usr/bin/env bash
# What IS the existing nuratech-mcp-server on :8088, and how close is it to the plugin we reviewed?
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 150 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "=== container detail ==="
  docker inspect nuratech-mcp-server --format "image={{.Config.Image}}
created={{.Created}}
started={{.State.StartedAt}}
restarts={{.RestartCount}}
env={{range .Config.Env}}{{.}} {{end}}" 2>/dev/null | sed "s/ /\n  /g" | head -40

  echo ""
  echo "=== compose project / labels ==="
  docker inspect nuratech-mcp-server --format "{{json .Config.Labels}}" 2>/dev/null | tr "," "\n" | head -20

  echo ""
  echo "=== what does it answer? ==="
  for p in / /healthz /mcp /health /.well-known/oauth-protected-resource; do
    echo -n "  GET  http://127.0.0.1:8088$p -> "
    curl -s -o /tmp/x -m 8 -w "HTTP %{http_code} (%{size_download}B)\n" "http://127.0.0.1:8088$p" 2>/dev/null
    head -c 220 /tmp/x 2>/dev/null | tr "\n" " " | sed "s/^/       body: /"
    echo ""
  done
  echo -n "  POST http://127.0.0.1:8088/mcp -> "
  curl -s -o /tmp/y -m 10 -w "HTTP %{http_code}\n" -X POST http://127.0.0.1:8088/mcp \
    -H "content-type: application/json" -H "accept: application/json, text/event-stream" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}" 2>/dev/null
  head -c 400 /tmp/y 2>/dev/null | tr "\n" " " | sed "s/^/       body: /"
  echo ""
' 2>&1 | head -70