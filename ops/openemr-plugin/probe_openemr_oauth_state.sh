#!/usr/bin/env bash
# Is OpenEMR's REST/OAuth2 API actually enabled? The FHIR API answers 200 but /oauth2/* says
# "API is disabled" -- these are separate toggles in OpenEMR globals. This decides whether the
# plugin's AUTH_MODE=jwt can ever validate a token, and whether OAuth client registration is possible.
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 150 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "=== OpenEMR version + api toggles ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mysql -uroot -p\$MYSQL_ROOT_PASSWORD openemr -N -e \"
      SELECT gl_name, gl_value FROM globals
      WHERE gl_name IN (\\\"rest_api\\\",\\\"rest_fhir_api\\\",\\\"rest_portal_api\\\",
                        \\\"oauth2_enabled\\\",\\\"oauth_ehr_launch\\\",\\\"rest_system_scopes_api\\\",
                        \\\"api_log_option\\\",\\\"rest_api\\\",\\\"version\\\");\"" 2>&1 | head -20

  echo ""
  echo "=== oauth tables present? ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mysql -uroot -p\$MYSQL_ROOT_PASSWORD openemr -N -e \"SHOW TABLES LIKE \\\"oauth%\\\";\"" 2>&1 | head -10

  echo ""
  echo "=== registered oauth clients ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mysql -uroot -p\$MYSQL_ROOT_PASSWORD openemr -e \"
      SELECT client_id, client_name, is_confidential, LEFT(scope,90) AS scope FROM oauth_clients;\"" 2>&1 | head -20

  echo ""
  echo "=== live probe of the oauth endpoints (are they registered as routes at all?) ==="
  for p in /oauth2/default/token /oauth2/default/authorize /oauth2/default/jwk /apis/default/api/patient; do
    echo -n "  $p -> "
    curl -s -o /tmp/z -m 10 -w "HTTP %{http_code} " "http://127.0.0.1:32777$p" 2>/dev/null
    echo "| $(head -c 130 /tmp/z | tr -d "\n")"
  done
' 2>&1 | head -70