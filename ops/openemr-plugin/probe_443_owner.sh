#!/usr/bin/env bash
# Who REALLY owns :443 on clinic, and does it serve mcp.nuratech.ai?
# Host nginx has an mcp.nuratech.ai vhost, but :443 is bound by docker-proxy -> a container.
# That means the host vhost may be shadowed entirely (the TLS-ownership-drift class).
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 120 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "  === container publishing :443 ==="
  docker ps --format "{{.Names}}|{{.Ports}}" 2>/dev/null | grep -E "443" | head -10

  echo ""
  echo "  === which container is radris-nginx? ==="
  docker ps --format "{{.Names}}|{{.Image}}|{{.Ports}}" 2>/dev/null | grep -iE "radris|nginx|proxy" | head -10

  echo ""
  echo "  === host nginx vs container: is host nginx even running? ==="
  systemctl is-active nginx 2>/dev/null || echo "  (no systemd nginx unit)"
  pgrep -a nginx 2>/dev/null | head -3 | cut -c1-140

  echo ""
  echo "  === ALL nginx-type configs inside the :443 container ==="
  C=$(docker ps --format "{{.Names}}|{{.Ports}}" | grep -E "0.0.0.0:443" | head -1 | cut -d"|" -f1)
  echo "  target container: ${C:-none}"
  if [ -n "$C" ]; then
    echo "  -- conf.d / sites --"
    docker exec "$C" sh -c "ls /etc/nginx/conf.d/ 2>/dev/null; ls /etc/nginx/sites-enabled/ 2>/dev/null" 2>/dev/null | head -20
    echo "  -- grep for mcp / pacs / openemr server_names --"
    docker exec "$C" sh -c "grep -rhnE \"server_name\" /etc/nginx/ 2>/dev/null | head -30" 2>/dev/null
  fi

  echo ""
  echo "  === proxy targets referenced by the live config ==="
  if [ -n "$C" ]; then
    docker exec "$C" sh -c "grep -rhoE \"proxy_pass [^;]+\" /etc/nginx/ 2>/dev/null | sort -u | head -20" 2>/dev/null
  fi
' 2>&1 | head -80