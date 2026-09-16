#!/usr/bin/env bash
# Read OpenEMR's actual API/OAuth globals with the correct client.
CFG=/opt/data/profiles/nura/home/.ssh/config
timeout 150 ssh -F "$CFG" -o ConnectTimeout=12 clinic '
  echo "=== which db client exists? ==="
  docker exec openemr-zklo-mariadb-1 sh -c "command -v mariadb mysql 2>/dev/null" 2>&1 | head -3

  echo ""
  echo "=== credentials visible to the container ==="
  docker exec openemr-zklo-mariadb-1 sh -c "env | grep -iE \"MYSQL|MARIADB\" | sed \"s/PASSWORD=.*/PASSWORD=<redacted>/I\"" 2>&1 | head -10

  echo ""
  echo "=== API / OAuth globals ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mariadb -uroot -p\$MARIADB_ROOT_PASSWORD openemr -N -e \"
      SELECT gl_name, gl_value FROM globals
      WHERE gl_name LIKE \\\"%api%\\\" OR gl_name LIKE \\\"%oauth%\\\" OR gl_name=\\\"rest_api\\\";\"" 2>&1 | head -25

  echo ""
  echo "=== oauth tables + clients ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mariadb -uroot -p\$MARIADB_ROOT_PASSWORD openemr -N -e \"SHOW TABLES LIKE \\\"oauth%\\\";\"" 2>&1 | head -10
  docker exec openemr-zklo-mariadb-1 sh -c "
    mariadb -uroot -p\$MARIADB_ROOT_PASSWORD openemr -e \"
      SELECT client_id, client_name, is_confidential FROM oauth_clients;\"" 2>&1 | head -12

  echo ""
  echo "=== OpenEMR version ==="
  docker exec openemr-zklo-mariadb-1 sh -c "
    mariadb -uroot -p\$MARIADB_ROOT_PASSWORD openemr -N -e \"
      SELECT gl_value FROM globals WHERE gl_name=\\\"version\\\";\"" 2>&1 | head -3
' 2>&1 | head -70