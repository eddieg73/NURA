# OIE + Radris-Stack Deploy — 2026-08-15 (verified live)

## Open Integration Engine (Mirth fork) — Clinic VPS
- Project `mirth-oie` @ `/docker/mirth-connect/` (compose: `docker-compose.oie.yml`, env: `.env.oie` 0600)
- Image: `openintegrationengine/engine:latest` (1:1 Mirth 4.5.2 fork) · Postgres 15 backend `enginedb` (14 tables built ✓)
- Ports: 8085→8080 (HTTP), 6661 (MLLP), 8444→8443 (admin; host 8443 held by NPM)
- DB internal-only (no host port) ✓ · appdata named volume ✓
- Creds: admin password rotated off default (sealed in profile .env `MIRTH_PASS`; API verified 4.5.2 with new creds)
- Old commercial `nextgenhealthcare/connect` container STOPPED (rollback: `docker start mirth-connect-mirth-connect-1`)
- Channels: 0 on old instance (nothing to migrate) → DICOM channel = next task on OIE
- Mirth MCP lane: `MIRTH_BASE_URL` added to sealed .env → picks up at next session restart

## Radris Stack — Clinic VPS (founder spec, validated)
- Project @ `/docker/radris-stack/` — db + orthanc + radris + nginx on one internal network
- nginx = ONLY service exposing host ports (80/443) ✓; db/orthanc/radris internal ✓
- Orthanc: `orthancteam/orthanc:latest`, Postgres plugin enabled, AET RADRIS_PACS, user `orthanc` (sealed pw) — VERIFIED: /system returns ApiVersion 30 through nginx
- Radris: image `radris/radris-app:latest` BUILT FROM SOURCE on Clinic (ghcr image is private; hub `radris/radris-app` does not exist) — RADIS 0.7.0 (openradx), Django on Postgres, migrations + superuser nura_admin done ✓, LLM lane wired to OpenRouter (deepseek-chat-v3.1)
- Verified: pacs.nuratech.ai → Orthanc JSON 200 · ris.nuratech.ai → HTTP 200 (self-signed certs, SAN both hosts)
- PENDING founder: DNS A records (Hostinger API 4009) → LE certs auto-swap after

## Viewer
- OHIF wired 16:25: `viewer.nuratech.ai` vhost in radris-stack nginx → ohif-viewer (32791)
- app-config.js: TWO sources — `pacs` (new stack via /dicom-web-pacs/) + `legacy` (orthanc-pacs via /dicom-web-legacy/); auth injected by nginx (browser never sees creds)
- FIX: Orthanc 26.x `latest`/`latest-full` images dropped libOrthancDicomWeb.so → hybrid plugin dir mounted (dicom-web .so from legacy image layer + postgres .so from latest-full). Verified: dicom-web 1.23 registered, QIDO 200 on both sources.
- VERIFIED: viewer 200 · QIDO-new 200 · QIDO-legacy 200 · pacs-anon 401 · ris 200
- PENDING founder: A viewer.nuratech.ai → 72.61.71.211 (with pacs + ris batch)

## ThaiRIS
- REMOVED per founder order (`docker compose -p thairis down`); MySQL volume retained for rollback
