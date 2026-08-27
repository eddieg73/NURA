# NURA Perfex CRM Modules (white-label CRM integration set)

Version-controlled set of the Perfex CRM modules NURATECH runs for the Medisun/clinical business (first-client). The main CRM is `pay.nuratech.ai` (\`/var/www/crm\`), the module swarm is mirrored from the module-rich \`/var/www/erp\` + brawlerz/medisun installs (byte-identical copies -> versions synced).

## The modules (right-click the white-label practice-operating CRM)
| Module | Purpose | Source install |
|---|---|---|
| **api** | Perfex REST module (Themesic) — enables MCP/API writes | erp |
| **emr** | Medical EMR module | erp |
| **kareo** | Kareo EHR integration | erp |
| **lifefile** | Patient records / LifeFile | erp |
| **appointly** | Appointments | erp |
| **epipay** | Payment processing | erp |
| **fixed_equipment** | Fixed/medical equipment tracking | erp |
| **warehouse** | Inventory / warehouse | erp |
| **quickbooks** | QuickBooks accounting integration | erp |
| **services_module** | Medical services catalog | erp |
| **sales_agent** | CRM sales agent | erp |
| **perfex_board** | Kanban/board | erp |
| **prchat** | CRM chat | erp |
| **webhooks** | Webhooks | erp |
| **erp_webhook** | ERP webhook bridge | erp |
| **ma** | Marketing automation | erp |
| **ghl_sync** | GoHighLevel sync | brawlerz |
| **einvoice** | e-Invoicing | brawlerz |
| exports / sync / openai / surveys / ideal / the_pdf_maker / launchpadai_payment / menu_setup / theme_style | base/common | crm |

## Install locations
- Main CRM: `/var/www/crm/modules/` (pay.nuratech.ai) — 21+ modules.
- Source installs (same files): `/var/www/erp`, `/var/www/app.brawlerzbox.com`, `/var/www/erp.medisunmedical.com`.
- REST module artifact (installable zip): `/var/www/erp/modules/api.zip`.

## Status
- Modules installed on the main CRM filesystem (copied + chowned, crm modules backed up before).
- **Enable** each via Perfex Admin -> Modules -> activate (runs install.php/creates tables).
- **API token** via Perfex Admin -> API -> API Management (unblocks the Perfex MCP writes).
