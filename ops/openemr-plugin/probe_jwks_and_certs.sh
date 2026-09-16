#!/usr/bin/env bash
# Two decisive questions before any deployment:
#  A. Does OpenEMR issue JWT access tokens verifiable via JWKS? The plugin's jwt mode REQUIRES
#     jose.jwtVerify against a JWKS. If OpenEMR issues OPAQUE tokens (introspection-only), the
#     plugin's AUTH_MODE=jwt cannot validate them and there is no introspection verifier shipped.
#  B. What TLS certs does radris-stack-nginx-1 (the real :443 owner) hold, and can it take a new vhost?
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 150 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "=== A1. OpenEMR JWKS (are there signing keys?) ==="
  curl -s -m 12 http://127.0.0.1:32777/oauth2/default/jwk 2>/dev/null | head -c 700
  echo ""
  echo ""
  echo "=== A2. OAuth discovery doc on the OpenEMR side ==="
  for p in /oauth2/default/.well-known/openid-configuration /apis/default/fhir/.well-known/smart-configuration; do
    echo -n "  $p -> "
    curl -s -o /tmp/d -m 10 -w "HTTP %{http_code}\n" "http://127.0.0.1:32777$p"
  done

  echo ""
  echo "=== A3. Any OAUTH CLIENT already registered in OpenEMR? ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mysql -uroot -p\$MYSQL_ROOT_PASSWORD openemr -e \"
      SHOW TABLES LIKE \\\"%oauth%\\\";\" 2>/dev/null" 2>/dev/null | head -12
  echo "  -- clients --"
  docker exec openemr-zklo-mariadb-1 sh -c "
    mysql -uroot -p\$MYSQL_ROOT_PASSWORD openemr -e \"
      SELECT client_id, client_name, is_confidential, scope FROM oauth_clients;\" 2>/dev/null" 2>/dev/null | head -15

  echo ""
  echo "=== B1. radris-stack-nginx-1 certs + mounts ==="
  docker inspect radris-stack-nginx-1 --format "{{range .Mounts}}{{.Source}} -> {{.Destination}}
{{end}}" 2>/dev/null | head -12
  echo "  -- certs visible inside the container --"
  docker exec radris-stack-nginx-1 sh -c "ls -la /etc/nginx/certs/ 2>/dev/null; ls /etc/letsencrypt/live/ 2>/dev/null" 2>/dev/null | head -15
  echo "  -- default.conf (the catch-all that currently swallows mcp.*) --"
  docker exec radris-stack-nginx-1 sh -c "cat /etc/nginx/conf.d/default.conf" 2>/dev/null | head -30
' 2>&1 | head -90