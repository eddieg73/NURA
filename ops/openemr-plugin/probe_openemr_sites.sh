#!/usr/bin/env bash
# The globals say rest_api=0 but /apis/default/fhir/metadata returns 200 and /apis/default/api/patient
# returns a normal OAuth 401. Resolve the contradiction: multi-site OpenEMR has PER-SITE globals, so
# the row I read may not be the site actually serving the port.
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 150 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "=== OpenEMR sites on disk ==="
  docker exec openemr-zklo-openemr-1 sh -c "ls -la /var/www/localhost/htdocs/openemr/sites/ 2>/dev/null" | head -15

  echo ""
  echo "=== which site does the vhost serve? (container openemr config) ==="
  docker exec openemr-zklo-openemr-1 sh -c "grep -rhoE \"\\\$site_id *= *.[a-z]+.\" /var/www/localhost/htdocs/openemr/sites/*.php /etc/apache2/conf.d/* 2>/dev/null | head -5"
  docker exec openemr-zklo-openemr-1 sh -c "cat /var/www/localhost/htdocs/openemr/sites/default/sqlconf.php 2>/dev/null | grep -vE \"pass|user\" | head -12"

  echo ""
  echo "=== globals PER SITE (multi-site means one row set per site) ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mariadb -uroot -p\$MYSQL_ROOT_PASSWORD openemr -N -e \"
      SELECT DISTINCT gl_name, gl_value FROM globals
      WHERE gl_name IN (\\\"rest_api\\\",\\\"rest_fhir_api\\\",\\\"rest_portal_api\\\",\\\"rest_system_scopes_api\\\");\"" 2>/dev/null
  echo "  -- how many rows for rest_api (would indicate per-site duplicates) --"
  docker exec openemr-zklo-mariadb-1 sh -c "
    mariadb -uroot -p\$MYSQL_ROOT_PASSWORD openemr -N -e \"
      SELECT COUNT(*) FROM globals WHERE gl_name=\\\"rest_api\\\";\"" 2>/dev/null

  echo ""
  echo "=== is there a FHIR-specific toggle or a separate fhir config? ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mariadb -uroot -p\$MYSQL_ROOT_PASSWORD openemr -N -e \"
      SELECT gl_name, gl_value FROM globals WHERE gl_name LIKE \\\"%fhir%\\\" OR gl_name LIKE \\\"%smart%\\\";\"" 2>/dev/null | head -10

  echo ""
  echo "=== does the FHIR API actually WORK end-to-end (metadata said 200)? re-probe both paths ==="
  for p in /apis/default/fhir/metadata /apis/default/fhir/Patient /apis/default/api/patient /oauth2/default/token; do
    echo -n "  $p -> HTTP "
    curl -s -o /dev/null -m 10 -w "%{http_code}\n" "http://127.0.0.1:32777$p" 2>/dev/null
  done
' 2>&1 | head -70