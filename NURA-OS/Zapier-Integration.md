# ⚡ Zapier Integration — NURA OS

> **Status:** Active | **Created:** 2026-08-01 | **Owner:** Hermes Agent

## Architecture

```
Zapier (Trigger)
  │
  ├─→ Path A: n8n Webhook (immediate)
  │     └─ https://n8n.nuratech.ai/webhook/{webhookId}
  │        └─ n8n Workflow: "ZAPIER — Hermes Bridge (CI/CD, Webhook, API)"
  │           ├─ Parse Zapier Payload
  │           ├─ Route by Event Type
  │           └─ Respond to Zapier
  │
  └─→ Path B: Hermes Webhook (gateway-dependent)
        └─ http://localhost:8644/webhooks/zapier-bridge
           └─ Hermes Agent processes request
              ├─ Skills loaded: n8n-workflow-authoring, communication, daily-briefing
              └─ HMAC-SHA256 validated
```

## Endpoints

### Path A — n8n Webhook (Production)

| Field | Value |
|-------|-------|
| Workflow ID | `nZ2RfhfnBmVxybDC` |
| Name | ZAPIER — Hermes Bridge (CI/CD, Webhook, API) |
| Status | Active |
| Webhook URL | **Get from n8n UI:** https://n8n.nuratech.ai/workflow/nZ2RfhfnBmVxybDC → Webhook node → Production URL |
| Method | POST |
| Content-Type | application/json |

**Sample Zapier Webhook POST:**
```json
{
  "action": "new_lead",
  "source": "zapier",
  "event": "crm_webhook",
  "payload": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Custom Headers (optional):**
- `X-Zapier-Source`: source system identifier
- `X-Zapier-Event`: event type for routing

**Response:**
```json
{
  "status": "received",
  "event_type": "crm_webhook",
  "routing_key": "zapier:crm_webhook",
  "timestamp": "2026-08-01T01:35:00.000Z",
  "bridge": "n8n-zapier-bridge-v1"
}
```

### Path B — Hermes Webhook (Gateway)

| Field | Value |
|-------|-------|
| Platform | `webhook` (enabled in config) |
| Port | 8644 (gateway) |
| URL | `http://localhost:8644/webhooks/zapier-bridge` |
| Secret | `JZU6KVAvO_brMs0-A8Yz3XU05UCYlBiDPrRUhITdSlY` |
| HMAC | SHA256 |
| Status | **Gateway not running — requires `hermes gateway run`** |

### CI/CD Webhook

| Field | Value |
|-------|-------|
| URL | `http://localhost:8644/webhooks/ci-pipeline` |
| Secret | `NPnS07hElCsCxel_uzCXD9UDoF5TmaSQqVcMTxwSZzg` |
| Skills | github-pr-workflow, github-code-review, requesting-code-review |
| Status | **Gateway not running** |

## Zapier Zap Configuration

### Zap 1: CRM → Hermes
1. **Trigger:** New CRM event (Typeform, GHL, etc.)
2. **Action:** Webhook POST to n8n
3. **URL:** `https://n8n.nuratech.ai/webhook/{webhookId}`
4. **Method:** POST
5. **Headers:** `X-Zapier-Source: crm`, `X-Zapier-Event: new_lead`

### Zap 2: CI/CD → Hermes
1. **Trigger:** GitHub/GitLab event
2. **Action:** Webhook POST
3. **URL:** n8n webhook or Hermes webhook
4. **Payload:** `{source, repository, branch, commit, action}`

### Zap 3: Notifications → Hermes
1. **Trigger:** Any Zapier trigger
2. **Action:** Webhook POST to n8n
3. **Hermes delivers to user via Telegram**

## API Server (Hermes)

| Field | Value |
|-------|-------|
| Host | `127.0.0.1` |
| Port | `8642` |
| Auth | Cookie-based (requires login) |
| Status | **Running** |

**Note:** The API server requires authentication. For unauthenticated webhook access, use the webhook platform (port 8644 via gateway) or n8n webhooks.

## Gateway Activation

To enable direct Hermes webhooks (Path B):
```bash
hermes gateway run
```
This opens port 8644 and activates all webhook subscriptions. **Requires explicit authorization per execution boundaries.**

## Related

- [[NURA-OS/Integration-Status]] — Live integration health
- [[NURA-OS/System-Architecture]] — Full platform architecture
- [[NURA-OS/Webhook-Subscriptions]] — All registered webhooks
- [[SOPs/Zapier-Zap-Templates]] — Reusable Zap templates
