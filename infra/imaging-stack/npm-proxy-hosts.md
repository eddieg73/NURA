# NURA Imaging Stack — Nginx Proxy Manager Configuration
Target: /opt/thairis (VPS) · NPM domain routing · applies to all subdomains below

## SSL Standard (all hosts)
- SSL: ON (Let's Encrypt, Force SSL: ON, HTTP/2: ON)
- Request new certificate on first save
- HSTS: enabled after cert issuance (optional hardening)
- Block common exploits: ON (NPM advanced tab)
- Websocket support: ON (required for OHIF Viewer)

## Proxy Host Table

| Domain | Forward Host | Forward Port | SSL | Force SSL | HTTP/2 |
|---|---|---|---|---|---|
| ris.nuratech.ai        | thairis          | **80** (confirmed) | Let's Encrypt | ON | ON |
| pacs.nuratech.ai       | orthanc          | 8042 (Orthanc REST) | Let's Encrypt | ON | ON |
| viewer.nuratech.ai    | ohif-viewer      | 3000              | Let's Encrypt | ON | ON |
| mirth.nuratech.ai     | mirth-connect    | 8080 (HTTP admin)  | Let's Encrypt | ON | ON |
| openemr.nuratech.ai   | openemr          | 80                | Let's Encrypt | ON | ON |
| hermes.nuratech.ai    | hermes-gateway   | 8642              | Let's Encrypt | ON | ON |

## Notes
- pacs.nuratech.ai should expose ONLY the Orthanc REST API + DICOMweb endpoints
  (8042); the DICOM C-STORE port (4242) stays on the private network — never public.
- viewer.nuratech.ai talks to Orthanc DICOMweb through the private docker network;
  the browser never contacts PACS directly (short-lived launch tokens only).
- hermes.nuratech.ai → Hermes gateway (127.0.0.1:8642 upstream equivalent in NPM
  network) for the API + MCP surface.
- ThaiRIS web port depends on deployment mode (vendor package); confirm on install
  and update the table.

## Payments (NUR-14)
- pay.nuratech.ai → Perfex payment module / NMI hosted-checkout entry (upstream: perfex:80 payment routes; SSL via Let's Encrypt, Force SSL + HTTP/2 per doctrine). Callback/webhook: pay.nuratech.ai/payment/nmi-callback (signature-verified, idempotent by NMI transaction id).
- NMI hosted checkout itself stays on NMI servers (redirect target) — pay.nuratech.ai is the entry/origin, never the card-data handler.
