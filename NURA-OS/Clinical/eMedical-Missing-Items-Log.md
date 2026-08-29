# eMedical Missing-Items Log — the updatable record

> DOCTRINE: read-only audit · single-session only (explicit logout every run) ·
> browser = fallback lane until the FHIR client registration clears.

- Last run: `2026-08-29T20:01:05+00:00` · mode `live` ·
  login `False` · logout `failed` ·
  scanned `0`
- Counts: patients `0` · missing labs
  `0` · missing imaging
  `0` · missing consults
  `0` · SOAP gaps `0`

## Per-patient board

| Patient | Last SOAP #1 | Last SOAP #2 | Missing labs / SOAP | Missing imaging (X-ray/CT/MRI) | Missing consults | Status | Last checked |
|---|---|---|---|---|---|---|---|
| *(no patients scanned yet)* | — | — | — | — | — | — | — |

## Legend

- **Status** — `open` = identified missing, nothing done · `ordered` = the
  item has been ordered/requested · `received` = the result/note arrived ·
  `ok` = no gaps found.
- **Missing imaging** lists only the modalities with no evidence (X-ray / CT / MRI).

## How this log updates

1. Live audit (single session): `python3 emed-gap-audit.py --limit 25`
2. The script merges into the JSON (the machine lane) and regenerates this
   table — statuses you set to `ordered`/`received` in the JSON are preserved.
3. Rebuild the table without a browser: `python3 emed-gap-audit.py --render-only`

## Run history

| Ran at | Mode | Scanned | Open | Ordered | Received |
|---|---|---|---|---|---|
| 2026-08-29T20:01:05+00:00 | live | 0 | 0 | 0 | 0 |
