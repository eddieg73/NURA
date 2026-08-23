# OpenEMR HL7 Forwarding — Mirth Integration (captured 2026-07-31)
Assignees: Amrit (Server Admin) & Osama (Clinical Config)

## Part 1 — ORM (Radiology Orders) Forwarding
- OpenEMR Admin → **Procedures → Providers** → Add New:
  - Name: `Mirth_Radiology_Routing`
  - Method/Transport: `Local Directory` (File)
  - Path: `/opt/openemr/hl7_out/`
- Clinical workflow: ED provider orders a CT and selects `Mirth_Radiology_Routing` as
  performing provider → OpenEMR drops `ORM^O01` HL7 file into `/opt/openemr/hl7_out/`
  → `hl7_dir_pusher` daemon forwards to Mirth :6002 (MLLP).

## Part 2 — ADT (Demographics) Polling
- OpenEMR does not natively push ADT over TCP on registration → Mirth polls OpenEMR
  DB directly with a dedicated **read-only** integration user.

### Provision the read-only Mirth user (run on the live OpenEMR MySQL/MariaDB server)
> NOTE: replace `CHANGE_ME` with a generated password held in your secret store —
> never a hardcoded literal. File perms 0600.

```sql
# Log into MySQL as root
mysql -u root -p

# Create a read-only user for Mirth Connect
CREATE USER 'mirth_reader'@'%' IDENTIFIED BY 'CHANGE_ME';

# Grant read access ONLY to the patient demographics table
GRANT SELECT ON openemr.patient_data TO 'mirth_reader'@'%';

# Apply permissions and exit
FLUSH PRIVILEGES;
EXIT;
```

### ADT channel architecture note (captured 2026-07-31)
- The deployed `OpenEMR_to_ThaiRIS_ADT` channel is a TCP listener (:6001) — it
  receives MLLP, it does not poll.
- ADT-by-polling requires a **second Mirth channel**: DB Reader (SELECT on
  `openemr.patient_data` with a timestamp watermark) → transformer mapping rows to
  `ADT^A04` → TCP sender → `thairis:6001`.
- The read-only grant above supports exactly that DB Reader; no write grants are
  needed or permitted.

## Artifacts
- `scripts/hl7_dir_pusher.sh` — directory watcher → MLLP forward (uses
  `hermes-hl7-simulator/scripts/send_mllp.py` framing).
- Verification: `hermes-hl7-simulator` against :6001/:6002 after channel deploy.
