# Market Data — 2026-08-02 07:15:10Z

Source: `data/market-data.json` (no secrets).

```json
{
 "ts": "2026-08-02T07:15:10.377910+00:00",
 "sources": {
  "yahoo_finance": {
   "status": "ok",
   "note": "{\"chart\":{\"result\":[{\"meta\":{\"currency\":\"USD\",\"symbol\":\"EURUSD=X\",\"exchangeName\"",
   "key_needed": false
  },
  "stooq": {
   "status": "down",
   "note": "HTTP Error 404: Not Found",
   "key_needed": false
  },
  "coingecko": {
   "status": "http200",
   "note": "",
   "key_needed": false
  },
  "gdelt": {
   "status": "down",
   "note": "HTTP Error 429: Too Many Requests",
   "key_needed": false
  },
  "senate_efd": {
   "status": "ok",
   "note": "<!DOCTYPE HTML>     <html lang=\"en\">         <head>             <title>eFD: Home",
   "key_needed": false
  },
  "house_disclosures": {
   "status": "down",
   "note": "HTTP Error 500: Internal Server Error",
   "key_needed": false
  },
  "quiver": {
   "status": "ok",
   "note": "<!DOCTYPE html> <html lang=\"en\">         <head>               <meta charset=\"UTF",
   "key_needed": true
  },
  "alpha_vantage": {
   "status": "ok",
   "note": "{     \"Meta Data\": {         \"1. Information\": \"Intraday (5min) open, high, low,",
   "key_needed": true
  },
  "fred": {
   "status": "down",
   "note": "HTTP Error 400: Bad Request",
   "key_needed": true
  },
  "finnhub": {
   "status": "down",
   "note": "HTTP Error 401: Unauthorized",
   "key_needed": true
  }
 }
}
```

**Read:** Market-data sources: 5 ok (alpha_vantage, coingecko, quiver, senate_efd, yahoo_finance), 5 down (finnhub, fred, gdelt, house_disclosures, stooq). Key-needed count: 4.
