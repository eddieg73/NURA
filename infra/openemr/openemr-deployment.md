# OpenEMR deployment — NURA monorepo copy

Our OpenEMR Docker deployment (the openemr-zklo stack on the Clinic node). Maintained against the upstream `openemr/openemr` repo.

## Deployment: `/docker/openemr-zklo/docker-compose.yml` (Clinic `72.61.71.211`)
```yaml
services:
  openemr:
    image: openemr/openemr:latest
    restart: unless-stopped
    ports: ["80"]
    labels:
      - traefik.enable=true
      - traefik.http.routers.${COMPOSE_PROJECT_NAME}.rule=Host(`${COMPOSE_PROJECT_NAME}.${TRAEFIK_HOST}`)
      - traefik.http.routers.${COMPOSE_PROJECT_NAME}.entrypoints=websecure
      - traefik.http.routers.${COMPOSE_PROJECT_NAME}.tls.certresolver=letsencrypt
      - traefik.http.services.${COMPOSE_PROJECT_NAME}.loadbalancer.server.port=80
    entrypoint: /bin/sh
    command: ["-c", "/var/www/localhost/htdocs/openemr/openemr.sh & OE_PID=$!; until curl --silent --insecure --fail https://localhost/meta/health/readyz 2>/dev/null; do sleep 15; done; if [ ! -f /var/www/localhost/htdocs/openemr/sites/.password_initialized ]; then /root/unlock_admin.sh \"${ADMIN_PASSWORD}\"; touch /var/www/localhost/htdocs/openemr/sites/.password_initialized; fi; wait $OE_PID"]
    environment: [MYSQL_HOST=mariadb, MYSQL_ROOT_PASS=${MYSQL_ROOT_PASS}, MYSQL_USER=openemr, MYSQL_PASS=${MYSQL_PASS}, OE_USER=admin]
    volumes: [openemr_sites:/var/www/localhost/htdocs/openemr/sites, openemr_logs:/var/log]
    depends_on: { mariadb: { condition: service_healthy } }
    healthcheck:
      test: ["CMD","curl","--fail","--insecure","--location","--show-error","--silent","https://localhost/meta/health/readyz"]
      start_period: 3m  start_interval: 10s  interval: 1m  timeout: 5s  retries: 3
  mariadb:
    image: mariadb:latest
    restart: unless-stopped
    environment: [MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASS}]
    volumes: [openemr_db:/var/lib/mysql]
volumes: { openemr_sites: {}, openemr_logs: {}, openemr_db: {} }
```

## How we maintain OUR copy (sync with upstream)
- **Upstream repo:** `https://github.com/openemr/openemr` (the OpenEMR source; our container `openemr/openemr:latest` builds from it).
- **Our copy:** this deployment (compose + our config/env). We track upstream so we can pull OpenEMR updates + keep our customizations.
- **Sync model:** vendor the upstream OpenEMR as a git-remote (or a `vendor/openemr` submodule) → `git fetch upstream` → rebase our custom config onto the updated OpenEMR → re-deploy. Custom parts = our compose changes (unlock_admin, traefik labels, env), which we apply on top, never overwrite upstream.

## Notes
- OpenEMR is **GPL** — call its API/use its image freely; don't vendor its source into a non-GPL context (keep our custom compose/config, treat OpenEMR source as an upstream dependency).
- Secrets (admin/mysql passwords) come from `.env` at deploy time — never in the repo.
- (Clearwater Aesthetics — a Perfex module `clearwateraesthetics` lives in the erp install; an OpenEMR instance for it may be a separate deploy to locate.)
