# Connections — 2026-08-28 19:39:18Z

Source: `data/connections.json` (no secrets).

```json
{
 "ts": "2026-08-28T19:39:18Z",
 "lanes": {
  "openfda": {
   "kind": "service/lane",
   "creds": false,
   "status": "no_creds"
  },
  "pubmed": {
   "kind": "eutils (external)",
   "creds": true,
   "status": "ok"
  },
  "bioportal": {
   "kind": "service/lane",
   "creds": false,
   "status": "no_creds"
  },
  "redis": {
   "kind": "service",
   "creds": true,
   "status": "ok"
  },
  "qdrant": {
   "kind": "service",
   "creds": true,
   "status": "ok"
  },
  "paperclip": {
   "kind": "service",
   "creds": true,
   "status": "down"
  },
  "moltbook": {
   "kind": "lane",
   "creds": true,
   "status": "ok"
  },
  "mirth": {
   "kind": "lane",
   "creds": true,
   "status": "ok"
  },
  "openemr": {
   "kind": "lane",
   "creds": false,
   "status": "no_creds"
  },
  "perfex": {
   "kind": "lane",
   "creds": false,
   "status": "no_creds"
  },
  "chatwoot": {
   "kind": "lane",
   "creds": false,
   "status": "no_creds"
  },
  "documo": {
   "kind": "lane",
   "creds": false,
   "status": "no_creds"
  },
  "granola": {
   "kind": "lane",
   "creds": false,
   "status": "no_creds"
  },
  "firebase": {
   "kind": "lane",
   "creds": false,
   "status": "no_creds"
  },
  "openevidence": {
   "kind": "lane",
   "creds": true,
   "status": "ok"
  },
  "ghl": {
   "kind": "lane",
   "creds": true,
   "status": "ok"
  },
  "twilio": {
   "kind": "channel",
   "creds": true,
   "status": "ok"
  }
 }
}
```

**Read:** 8/17 lanes ok (ghl, mirth, moltbook, openevidence, pubmed, qdrant, redis, twilio). Down: paperclip. No-creds: bioportal, chatwoot, documo, firebase, granola, openemr, openfda, perfex. `paperclip` down (API key empty — expected; DB lane serves reads).
