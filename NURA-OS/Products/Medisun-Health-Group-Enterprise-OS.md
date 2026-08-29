# Medisun Health Group — Enterprise Operating Architecture (schema · scaffolding · logic)

**Owner:** Medisun Health Group (MSO) · **Built:** 2026-08-27 · **Systems:** Perfex CRM (back-office/ops) · OpenEMR (EMR) · eMedical (practice manager) · QuickBooks MCP (accounting, planned) · GHL (optional patient capture) · Backblaze B2 (durable store)
**Class:** Enterprise operating spec · Source of truth (vault). Mirror: Notion.

---

## 1. The multi-entity model (this is the spine)
**Medisun Health Group** = the **MSO / managed-care organization** — owns shared services, contracts, the ops.
It operates **individual clinics, each a SEPARATE legal entity with its own Tax ID (TIN) + Medicare (NPI) number:**
| Entity | Location | TIN | NPI | Type |
|---|---|---|---|---|
| **Medisun Health Group** | — | — | — | MSO / parent |
| Clinic 1 | **Little Haiti** | TIN_1 | NPI_1 | core clinic |
| Clinic 2 | **North Miami** | TIN_2 | NPI_2 | core clinic |
| Clinic 3 | **Lauderhill** | TIN_3 | NPI_3 | core clinic |
| Clinic 4 | **Pinecrest** | (affiliate) | (affiliate) | affiliate provider (agreement) |
| Med Dir office | **Tampa** | (adds patients) | — | Medical Director practice |
| Expansion | **Clearwater** | (new) | (new) | expansion office |

**Isolation rule:** every Perfex record (customer, item, invoice, expense, task, asset) is **scoped to an Entity/Clinic** — so ledgers, PM, inventory, and finance are per-legal-entity (per TIN/NPI). Never cross-entity.

## 2. Perfex module map (the scaffolding)
| Domain | Perfex representation | Key fields |
|---|---|---|
| **Inventory** | `Items` (category) + custom `clinic` | SKU, Name, Qty, Reorder point, Supplier, Unit cost, Clinic |
| **Vehicles / Fleet** | `Items` (type=Vehicle) or Fleet project | Make/Model/Year, VIN, Plate, Assigned clinic, Odometer, Status |
| **Logistics** | `Projects`/`Tasks` (routing) | Route, Driver, Vehicle, Shipment, Leg time, Status, Clinic |
| **PM — Vehicles** | recurring `Tasks` on the vehicle | Interval (miles/days), Next due, Checklist, Done-by, Cost |
| **PM — Med Equipment** | recurring `Tasks` on the equipment asset | Interval, Next calibration/due, Checklist, Tech, Cost |
| **Med Equipment tracking** | `Items`/custom Equipment | Asset ID, Type, Serial, Clinic, Status, PM interval, Next due |
| **Finance / Payments** | `Invoices`, `Estimates`, `Payments`, `Subscriptions` | Clinic-scoped, per-entity |
| **Accounting** | `Expenses` + **sync out** to QuickBooks + eMedical | GL map, per-entity, sync status |
| **CRM / Patient capture** | `Customers` (non-clinical) grouped by location | Name, phone, email, DOB, Location |

## 3. The schema (data model — per-entity fields)
- **Entity key:** a `clinic`/`entity` custom field on Customers, Items, Invoices, Expenses, Tasks, Projects — value = one of the 6 entities.
- **Entity metadata:** custom fields `entity_tin`, `entity_npi` (stored on each clinic's customer/entity record — never in clinical data).
- **Asset model** (fleet + med equipment): `asset_id · type · make/model · serial · clinic · status · pm_interval_miles/days · pm_interval_cal · next_pm_due · last_pm_done · tech · cost`.
- **PM schedule:** recurring-to-do with a `next_due` date + a checklist (surgical-equipment / vehicle inspection steps) + `done_by` + `cost`.

## 4. The logic (workflows to encode)
1. **PM engine (cron):** daily → find assets where `next_pm_due <= today` → create a PM `Task` with the checklist → assign to the clinic tech → on completion set `next_pm_due = today + interval`. Escalate if overdue (safety-critical: med equipment not used past due).
2. **Inventory reorder:** when `qty <= reorder_point` → create a reorder task/PO → notify the ops lane.
3. **Fleet/logistics:** a route `Task` ties driver + vehicle + shipment + clinic + time; completed → updates odometer (feeds PM interval).
4. **Finance:** receipt → post payment to the entity's ledger → **push to QuickBooks** (per-entity GL) → **sync with eMedical** (encounter/billing) → reconcile.
5. **Accounting sync:** Perfex Expenses/Invoices → **eMedical practice manager** (patient/encounter billing) → **QuickBooks** (the real ledger). Field-mapped, double-entry, per-entity.
6. **Entity isolation:** every transaction tags the clinic → per-entity P&L + PM + inventory reports.

## 5. Integration topology
- **Perfex** = business/ops CRM (**non-clinical** — customers/items/fleet/PM/inventory/finance).
- **OpenEMR** = the EMR (**clinical truth**) via its FHIR R4 + SMART-on-FHIR API (bonFHIR node).
- **eMedical** = the practice manager (appointments/encounters/billing) — **sync accounting** (Perfex ↔ eMedical).
- **QuickBooks MCP** (planned) = the accounting ledger — Perfex Expenses/Invoices → QBO.
- **GHL** (optional) = patient capture; its existing n8n workflows map to OpenEMR + Perfex.
- **Backblaze B2** = durable object store (exports/backups, ObjectLock, no-delete, encrypted).

## 6. Security & compliance (multi-entity + PHI)
- **Entity isolation:** separate TIN/NPI → separate ledgers/records; a clinic group per entity; no cross-entity contamination.
- **PHI wall:** Perfex = **non-clinical only** (names/contact/asset/ops). Clinical (charts, dx) = OpenEMR/eMedical only. **Never write PHI to Perfex.**
- **Creds:** sealed (`SEAL→PROBE→REGISTER→WIRE→DOC→REPORT`); Perfex token, GHL key, B2 keys in `.env` 0600.
- **Audit:** every automated Perfex change logs a system comment attributing to Hermes Agent (Perfex protocol).
- **HIPAA:** production PHI on a BAA host; Perfex/B2 dev-non-PHI until BAA (B2 BAA first per doctrine). No PHI in Perfex workflows/exports.

## 7. Executive lens (CTO · Security · Marketing · Logistics)
- **CTO/Architect:** one source of truth per domain, entity-scoped, modular; the schema above is the contract; sovereign-LLM/automation where sensible.
- **Security:** multi-entity isolation + PHI wall + sealed creds + append-only audit + B2 ObjectLock.
- **Marketing:** GHL capture → Perfex (non-clinical) → OpenEMR; CRM used for business control (not clinical).
- **Logistics:** fleet + routing + PM (vehicles + med equipment) all driven from the same asset/PM engine; per-clinic.

## 8. Build/activation status
- **Design (this spec):** READY.
- **Scaffold into Perfex:** gated on the **Perfex REST module + API token** (currently 404 / absent; founder acquiring). Once in: create the 6 Entities (customer groups + TIN/NPI custom fields), the asset/IM/PM modules + fields, and the finance/accounting fields. Writes go through the Perfex MCP (183 tools) with audit comments.
- **Integration:** eMedical + QuickBooks MCP + OpenEMR FHIR — wire after Perfex.

## 9. "Use all the existing workflows mapped to OpenEMR + Perfex"
The existing n8n workflows (Medisun Voice AI / Booking / Memory, ElevenLabs→GHL, NMI→GHL, OpenEMR 8-pack) all map into this spine: **GHL/voice = patient capture → Perfex customer (non-clinical, by location) + OpenEMR appointment/encounter (clinical)**. Keep the Oussama boundary (Perfex non-clinical) + the PHI wall.
