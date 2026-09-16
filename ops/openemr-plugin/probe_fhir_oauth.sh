#!/usr/bin/env bash
# How close is the ChatGPT path actually? Check OpenEMR FHIR + whether ANY OAuth AS exists.
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 150 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "=== 1. WHAT IS ON :8088 (the dead vhost s target)? ==="
  (ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep -E ":8088" | head -3
  curl -s -o /dev/null -m 5 -w "    http://127.0.0.1:8088/ -> HTTP %{http_code}\n" http://127.0.0.1:8088/ 2>&1

  echo ""
  echo "=== 2. OpenEMR FHIR ENABLED? (container on host port 32777) ==="
  for path in /apis/default/fhir/metadata /apis/default/fhir/.well-known/smart-configuration /interface/login/login.php; do
    echo -n "    $path -> "
    curl -s -o /tmp/f -m 12 -w "HTTP %{http_code} (%{size_download}B, %{content_type})\n" "http://127.0.0.1:32777$path" 2>&1
  done
  echo "    metadata head:"
  curl -s -m 12 "http://127.0.0.1:32777/apis/default/fhir/metadata" 2>/dev/null | head -c 400 | sed "s/^/      /"
  echo ""

  echo ""
  echo "=== 3. DOES ANY OAUTH / AUTHORIZATION SERVER EXIST ON THE FLEET? ==="
  echo "    -- containers matching auth/oauth/keycloak/authentik/zitadel --"
  docker ps --format "{{.Names}}" 2>/dev/null | grep -iE "auth|oauth|keycloak|authentik|zitadel|hydra|ory|casdoor" | head -10
  echo "    (empty = none on clinic)"
' 2>&1 | head -60
echo ""
echo "=== 4. LAB + EDGE: any auth server? ==="
for h in lab edge; do
  echo -n "  $h: "
  timeout 60 ssh -F "$CFG" -o ConnectTimeout=12 "$h" \
    'docker ps --format "{{.Names}}" 2>/dev/null | grep -iE "auth|oauth|keycloak|authentik|zitadel|hydra|casdoor" | tr "\n" " "; echo' 2>&1 | head -3
done
echo "  (blank = none found)"