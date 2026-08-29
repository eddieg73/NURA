# n8n Artifacts (founder drops 2026-08-15)

## 1. Automated SEO Content Creation (workflow)
Pipeline: Google Sheets (Campaigns!A1:D100) → Generate Search Query (Code) → SerpAPI keywords → Group Keywords (Code) → GPT-4o article → Write to Google Sheet (GeneratedContent!A1).
- Live instance: Edge n8n — workflow "Automated SEO Content Creation" (11 nodes, currently off).
- Notes: dropped JSON = template with placeholder sheet/serpapi keys; the instance copy may already carry real config (verify via API).

## 2. N8N Chat Widget for GHL Sub-Account (Level Up Aesthetics / "Chat with Veronica")
- Vanilla-JS chat widget: floating button + window, posts {message, sessionId, contactId, locationId, timestamp, userAgent, url, referrer} to `https://<N8N>/webhook/chat`, expects `{message: "..."}` back.
- localStorage session persistence, XSS-safe escaping, GHL contact/location data attributes (`data-contact-id`, `data-location-id`).
- Embed: paste the <script> into the GHL sub-account (custom code/footer).
- Companion workflow: Webhook (POST /chat) → OpenAI (Veronica persona) → Respond to Webhook {message} — CREATED in n8n by Hermes 2026-08-15.
