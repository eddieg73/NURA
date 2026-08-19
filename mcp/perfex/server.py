#!/opt/data/mcp-installs/perfex/.venv/bin/python
"""Perfex CRM MCP Server — 183 operations covering all Perfex CRM API endpoints."""
import os
import json
import sys
import asyncio
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

BASE_URL = os.getenv("PERFEX_BASE_URL", "https://195.35.32.113/api").rstrip("/")
API_TOKEN = os.getenv("PERFEX_API_TOKEN", "")


def api_request(method, path, data=None, params=None):
    """Make an API request to Perfex CRM."""
    url = f"{BASE_URL}/{path.lstrip('/')}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, method=method)
    req.add_header("Authtoken", API_TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode()[:500]}
    except URLError as e:
        return {"error": "Connection failed", "detail": str(e)}


# ─── Helper: build a Tool with standard schema ───────────────────────────
def T(name, desc, props=None, required=None, extra_props=True):
    """Create a Tool definition with standard JSON Schema."""
    schema = {"type": "object", "properties": props or {}}
    if required:
        schema["required"] = required
    if not extra_props:
        schema["additionalProperties"] = False
    return Tool(name=name, description=desc, inputSchema=schema)


# ═══════════════════════════════════════════════════════════════════════════
# TOOL DEFINITIONS — all 183 tools
# ═══════════════════════════════════════════════════════════════════════════

TOOLS = [
    # ── CUSTOMERS (10) ──────────────────────────────────────────────────
    T("perfex_customers_create", "Create a new customer in Perfex CRM",
      {"company": {"type": "string", "description": "Company name (required)"},
       "vat": {"type": "string", "description": "VAT number"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "website": {"type": "string", "description": "Website URL"},
       "default_currency": {"type": "integer", "description": "Default currency ID"},
       "default_language": {"type": "string", "description": "Default language"},
       "address": {"type": "string", "description": "Address"},
       "city": {"type": "string", "description": "City"},
       "state": {"type": "string", "description": "State"},
       "zip": {"type": "string", "description": "ZIP code"},
       "country": {"type": "integer", "description": "Country ID"},
       "billing_street": {"type": "string", "description": "Billing street"},
       "billing_city": {"type": "string", "description": "Billing city"},
       "billing_state": {"type": "string", "description": "Billing state"},
       "billing_zip": {"type": "string", "description": "Billing ZIP"},
       "billing_country": {"type": "integer", "description": "Billing country ID"},
       "shipping_street": {"type": "string", "description": "Shipping street"},
       "shipping_city": {"type": "string", "description": "Shipping city"},
       "shipping_state": {"type": "string", "description": "Shipping state"},
       "shipping_zip": {"type": "string", "description": "Shipping ZIP"},
       "shipping_country": {"type": "integer", "description": "Shipping country ID"}},
      required=["company"]),

    T("perfex_customers_get", "Get a customer by ID",
      {"id": {"type": "integer", "description": "Customer ID"}},
      required=["id"]),

    T("perfex_customers_list", "List all customers with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "sort": {"type": "string", "description": "Sort field"},
       "fields": {"type": "string", "description": "Comma-separated fields to return"}}),

    T("perfex_customers_update", "Update an existing customer",
      {"id": {"type": "integer", "description": "Customer ID"},
       "company": {"type": "string", "description": "Company name"},
       "vat": {"type": "string", "description": "VAT number"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "website": {"type": "string", "description": "Website URL"},
       "default_currency": {"type": "integer", "description": "Default currency ID"},
       "default_language": {"type": "string", "description": "Default language"},
       "address": {"type": "string", "description": "Address"},
       "city": {"type": "string", "description": "City"},
       "state": {"type": "string", "description": "State"},
       "zip": {"type": "string", "description": "ZIP code"},
       "country": {"type": "integer", "description": "Country ID"}},
      required=["id"]),

    T("perfex_customers_delete", "Delete a customer",
      {"id": {"type": "integer", "description": "Customer ID"}},
      required=["id"]),

    T("perfex_customers_get_contacts", "Get contacts for a customer",
      {"customer_id": {"type": "integer", "description": "Customer ID"}},
      required=["customer_id"]),

    T("perfex_customers_get_contracts", "Get contracts for a customer",
      {"customer_id": {"type": "integer", "description": "Customer ID"}},
      required=["customer_id"]),

    T("perfex_customers_get_invoices", "Get invoices for a customer",
      {"customer_id": {"type": "integer", "description": "Customer ID"}},
      required=["customer_id"]),

    T("perfex_customers_get_projects", "Get projects for a customer",
      {"customer_id": {"type": "integer", "description": "Customer ID"}},
      required=["customer_id"]),

    T("perfex_customers_get_tickets", "Get tickets for a customer",
      {"customer_id": {"type": "integer", "description": "Customer ID"}},
      required=["customer_id"]),

    # ── CONTACTS (5) ────────────────────────────────────────────────────
    T("perfex_contacts_create", "Create a new contact",
      {"customer_id": {"type": "integer", "description": "Customer ID (required)"},
       "firstname": {"type": "string", "description": "First name (required)"},
       "lastname": {"type": "string", "description": "Last name (required)"},
       "email": {"type": "string", "description": "Email address"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "title": {"type": "string", "description": "Job title"},
       "password": {"type": "string", "description": "Contact password"},
       "is_primary": {"type": "boolean", "description": "Is primary contact"},
       "direction": {"type": "string", "description": "Direction"},
       "invoice_emails": {"type": "boolean", "description": "Send invoice emails"},
       "estimate_emails": {"type": "boolean", "description": "Send estimate emails"},
       "credit_note_emails": {"type": "boolean", "description": "Send credit note emails"},
       "contract_emails": {"type": "boolean", "description": "Send contract emails"},
       "task_emails": {"type": "boolean", "description": "Send task emails"},
       "project_emails": {"type": "boolean", "description": "Send project emails"},
       "ticket_emails": {"type": "boolean", "description": "Send ticket emails"}},
      required=["customer_id", "firstname", "lastname"]),

    T("perfex_contacts_get", "Get a contact by ID",
      {"id": {"type": "integer", "description": "Contact ID"}},
      required=["id"]),

    T("perfex_contacts_list", "List all contacts with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "customer_id": {"type": "integer", "description": "Filter by customer ID"}}),

    T("perfex_contacts_update", "Update an existing contact",
      {"id": {"type": "integer", "description": "Contact ID"},
       "firstname": {"type": "string", "description": "First name"},
       "lastname": {"type": "string", "description": "Last name"},
       "email": {"type": "string", "description": "Email address"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "title": {"type": "string", "description": "Job title"},
       "is_primary": {"type": "boolean", "description": "Is primary contact"}},
      required=["id"]),

    T("perfex_contacts_delete", "Delete a contact",
      {"id": {"type": "integer", "description": "Contact ID"}},
      required=["id"]),

    # ── TICKETS (14) ────────────────────────────────────────────────────
    T("perfex_tickets_create", "Create a new support ticket",
      {"subject": {"type": "string", "description": "Ticket subject (required)"},
       "message": {"type": "string", "description": "Ticket message"},
       "department": {"type": "integer", "description": "Department ID"},
       "priority": {"type": "integer", "description": "Priority ID"},
       "service": {"type": "integer", "description": "Service ID"},
       "contact_id": {"type": "integer", "description": "Contact ID"},
       "project_id": {"type": "integer", "description": "Project ID"},
       "email": {"type": "string", "description": "Contact email"},
       "name": {"type": "string", "description": "Contact name"},
       "assigned": {"type": "integer", "description": "Assigned staff ID"},
       "custom_fields": {"type": "object", "description": "Custom field values"}},
      required=["subject"]),

    T("perfex_tickets_get", "Get a ticket by ID",
      {"id": {"type": "integer", "description": "Ticket ID"}},
      required=["id"]),

    T("perfex_tickets_list", "List all tickets with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "integer", "description": "Filter by status ID"},
       "department": {"type": "integer", "description": "Filter by department ID"},
       "project_id": {"type": "integer", "description": "Filter by project ID"}}),

    T("perfex_tickets_update", "Update an existing ticket",
      {"id": {"type": "integer", "description": "Ticket ID"},
       "subject": {"type": "string", "description": "Ticket subject"},
       "department": {"type": "integer", "description": "Department ID"},
       "priority": {"type": "integer", "description": "Priority ID"},
       "service": {"type": "integer", "description": "Service ID"},
       "assigned": {"type": "integer", "description": "Assigned staff ID"},
       "custom_fields": {"type": "object", "description": "Custom field values"}},
      required=["id"]),

    T("perfex_tickets_delete", "Delete a ticket",
      {"id": {"type": "integer", "description": "Ticket ID"}},
      required=["id"]),

    T("perfex_tickets_add_reply", "Add a reply to a ticket",
      {"ticket_id": {"type": "integer", "description": "Ticket ID"},
       "message": {"type": "string", "description": "Reply message (required)"},
       "staff_id": {"type": "integer", "description": "Staff ID (0 for customer reply)"}},
      required=["ticket_id", "message"]),

    T("perfex_tickets_get_reply", "Get a ticket reply by ID",
      {"id": {"type": "integer", "description": "Ticket reply ID"}},
      required=["id"]),

    T("perfex_tickets_update_reply", "Update a ticket reply",
      {"id": {"type": "integer", "description": "Ticket reply ID"},
       "message": {"type": "string", "description": "Updated message"}},
      required=["id"]),

    T("perfex_tickets_delete_reply", "Delete a ticket reply",
      {"id": {"type": "integer", "description": "Ticket reply ID"}},
      required=["id"]),

    T("perfex_tickets_list_replies", "List all replies for a ticket",
      {"ticket_id": {"type": "integer", "description": "Ticket ID"}},
      required=["ticket_id"]),

    T("perfex_tickets_get_attachments", "Get attachments for a ticket",
      {"ticket_id": {"type": "integer", "description": "Ticket ID"}},
      required=["ticket_id"]),

    T("perfex_tickets_get_history", "Get history for a ticket",
      {"ticket_id": {"type": "integer", "description": "Ticket ID"}},
      required=["ticket_id"]),

    T("perfex_tickets_assign", "Assign a ticket to a staff member",
      {"ticket_id": {"type": "integer", "description": "Ticket ID"},
       "staff_id": {"type": "integer", "description": "Staff ID to assign"}},
      required=["ticket_id", "staff_id"]),

    T("perfex_tickets_change_status", "Change the status of a ticket",
      {"ticket_id": {"type": "integer", "description": "Ticket ID"},
       "status": {"type": "integer", "description": "New status ID"}},
      required=["ticket_id", "status"]),

    # ── INVOICES (8) ────────────────────────────────────────────────────
    T("perfex_invoices_create", "Create a new invoice",
      {"clientid": {"type": "integer", "description": "Customer ID (required)"},
       "number": {"type": "string", "description": "Invoice number (auto-generated if blank)"},
       "date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)"},
       "duedate": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
       "currency": {"type": "integer", "description": "Currency ID"},
       "project_id": {"type": "integer", "description": "Project ID"},
       "subtotal": {"type": "number", "description": "Subtotal"},
       "total": {"type": "number", "description": "Total"},
       "discount_total": {"type": "number", "description": "Discount total"},
       "discount_type": {"type": "string", "description": "Discount type (before_tax/after_tax)"},
       "adminnote": {"type": "string", "description": "Admin note"},
       "clientnote": {"type": "string", "description": "Client note"},
       "terms": {"type": "string", "description": "Terms"},
       "recurring": {"type": "integer", "description": "Recurring interval"},
       "recurring_type": {"type": "string", "description": "Recurring type (day/week/month/year)"},
       "custom_recurring": {"type": "boolean", "description": "Custom recurring"},
       "recurring_cycles": {"type": "integer", "description": "Number of recurring cycles"},
       "allowed_payment_modes": {"type": "array", "items": {"type": "integer"}, "description": "Allowed payment mode IDs"},
       "newitems": {"type": "array", "description": "Line items array"}},
      required=["clientid"]),

    T("perfex_invoices_get", "Get an invoice by ID",
      {"id": {"type": "integer", "description": "Invoice ID"}},
      required=["id"]),

    T("perfex_invoices_list", "List all invoices with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "string", "description": "Filter by status"},
       "customer_id": {"type": "integer", "description": "Filter by customer ID"}}),

    T("perfex_invoices_update", "Update an existing invoice",
      {"id": {"type": "integer", "description": "Invoice ID"},
       "clientid": {"type": "integer", "description": "Customer ID"},
       "date": {"type": "string", "description": "Invoice date"},
       "duedate": {"type": "string", "description": "Due date"},
       "adminnote": {"type": "string", "description": "Admin note"},
       "clientnote": {"type": "string", "description": "Client note"},
       "terms": {"type": "string", "description": "Terms"},
       "newitems": {"type": "array", "description": "Line items array"}},
      required=["id"]),

    T("perfex_invoices_delete", "Delete an invoice",
      {"id": {"type": "integer", "description": "Invoice ID"}},
      required=["id"]),

    T("perfex_invoices_get_payments", "Get payments for an invoice",
      {"invoice_id": {"type": "integer", "description": "Invoice ID"}},
      required=["invoice_id"]),

    T("perfex_invoices_get_pdf", "Get PDF for an invoice",
      {"invoice_id": {"type": "integer", "description": "Invoice ID"}},
      required=["invoice_id"]),

    T("perfex_invoices_send", "Send an invoice via email",
      {"invoice_id": {"type": "integer", "description": "Invoice ID"}},
      required=["invoice_id"]),

    # ── ESTIMATES (8) ───────────────────────────────────────────────────
    T("perfex_estimates_create", "Create a new estimate",
      {"clientid": {"type": "integer", "description": "Customer ID (required)"},
       "number": {"type": "string", "description": "Estimate number"},
       "date": {"type": "string", "description": "Estimate date (YYYY-MM-DD)"},
       "expirydate": {"type": "string", "description": "Expiry date (YYYY-MM-DD)"},
       "currency": {"type": "integer", "description": "Currency ID"},
       "project_id": {"type": "integer", "description": "Project ID"},
       "subtotal": {"type": "number", "description": "Subtotal"},
       "total": {"type": "number", "description": "Total"},
       "adminnote": {"type": "string", "description": "Admin note"},
       "clientnote": {"type": "string", "description": "Client note"},
       "terms": {"type": "string", "description": "Terms"},
       "newitems": {"type": "array", "description": "Line items array"},
       "status": {"type": "integer", "description": "Status ID"}},
      required=["clientid"]),

    T("perfex_estimates_get", "Get an estimate by ID",
      {"id": {"type": "integer", "description": "Estimate ID"}},
      required=["id"]),

    T("perfex_estimates_list", "List all estimates with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "string", "description": "Filter by status"},
       "customer_id": {"type": "integer", "description": "Filter by customer ID"}}),

    T("perfex_estimates_update", "Update an existing estimate",
      {"id": {"type": "integer", "description": "Estimate ID"},
       "clientid": {"type": "integer", "description": "Customer ID"},
       "date": {"type": "string", "description": "Estimate date"},
       "expirydate": {"type": "string", "description": "Expiry date"},
       "adminnote": {"type": "string", "description": "Admin note"},
       "clientnote": {"type": "string", "description": "Client note"},
       "newitems": {"type": "array", "description": "Line items array"}},
      required=["id"]),

    T("perfex_estimates_delete", "Delete an estimate",
      {"id": {"type": "integer", "description": "Estimate ID"}},
      required=["id"]),

    T("perfex_estimates_send", "Send an estimate via email",
      {"id": {"type": "integer", "description": "Estimate ID"}},
      required=["id"]),

    T("perfex_estimates_convert_to_invoice", "Convert an estimate to an invoice",
      {"id": {"type": "integer", "description": "Estimate ID"}},
      required=["id"]),

    T("perfex_estimates_get_pdf", "Get PDF for an estimate",
      {"id": {"type": "integer", "description": "Estimate ID"}},
      required=["id"]),

    # ── PROPOSALS (11) ──────────────────────────────────────────────────
    T("perfex_proposals_create", "Create a new proposal",
      {"subject": {"type": "string", "description": "Proposal subject (required)"},
       "rel_type": {"type": "string", "description": "Related type (customer/lead)"},
       "rel_id": {"type": "integer", "description": "Related ID"},
       "proposal_to": {"type": "string", "description": "Proposal recipient email"},
       "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
       "open_till": {"type": "string", "description": "Open till date (YYYY-MM-DD)"},
       "currency": {"type": "integer", "description": "Currency ID"},
       "discount_type": {"type": "string", "description": "Discount type"},
       "status": {"type": "integer", "description": "Status ID"},
       "assigned": {"type": "integer", "description": "Assigned staff ID"},
       "content": {"type": "string", "description": "Proposal content (HTML)"},
       "newitems": {"type": "array", "description": "Line items array"}},
      required=["subject"]),

    T("perfex_proposals_get", "Get a proposal by ID",
      {"id": {"type": "integer", "description": "Proposal ID"}},
      required=["id"]),

    T("perfex_proposals_list", "List all proposals with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "integer", "description": "Filter by status ID"}}),

    T("perfex_proposals_update", "Update an existing proposal",
      {"id": {"type": "integer", "description": "Proposal ID"},
       "subject": {"type": "string", "description": "Proposal subject"},
       "content": {"type": "string", "description": "Proposal content (HTML)"},
       "date": {"type": "string", "description": "Date"},
       "open_till": {"type": "string", "description": "Open till date"},
       "assigned": {"type": "integer", "description": "Assigned staff ID"},
       "status": {"type": "integer", "description": "Status ID"}},
      required=["id"]),

    T("perfex_proposals_delete", "Delete a proposal",
      {"id": {"type": "integer", "description": "Proposal ID"}},
      required=["id"]),

    T("perfex_proposals_send", "Send a proposal via email",
      {"id": {"type": "integer", "description": "Proposal ID"}},
      required=["id"]),

    T("perfex_proposals_accept", "Accept a proposal",
      {"id": {"type": "integer", "description": "Proposal ID"}},
      required=["id"]),

    T("perfex_proposals_decline", "Decline a proposal",
      {"id": {"type": "integer", "description": "Proposal ID"}},
      required=["id"]),

    T("perfex_proposals_list_comments", "List comments for a proposal",
      {"id": {"type": "integer", "description": "Proposal ID"}},
      required=["id"]),

    T("perfex_proposals_add_comment", "Add a comment to a proposal",
      {"id": {"type": "integer", "description": "Proposal ID"},
       "content": {"type": "string", "description": "Comment content (required)"}},
      required=["id", "content"]),

    T("perfex_proposals_get_pdf", "Get PDF for a proposal",
      {"id": {"type": "integer", "description": "Proposal ID"}},
      required=["id"]),

    # ── CREDIT NOTES (10) ───────────────────────────────────────────────
    T("perfex_credit_notes_create", "Create a new credit note",
      {"clientid": {"type": "integer", "description": "Customer ID (required)"},
       "number": {"type": "string", "description": "Credit note number"},
       "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
       "currency": {"type": "integer", "description": "Currency ID"},
       "description": {"type": "string", "description": "Description"},
       "adminnote": {"type": "string", "description": "Admin note"},
       "newitems": {"type": "array", "description": "Line items array"}},
      required=["clientid"]),

    T("perfex_credit_notes_get", "Get a credit note by ID",
      {"id": {"type": "integer", "description": "Credit note ID"}},
      required=["id"]),

    T("perfex_credit_notes_list", "List all credit notes with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "customer_id": {"type": "integer", "description": "Filter by customer ID"}}),

    T("perfex_credit_notes_update", "Update an existing credit note",
      {"id": {"type": "integer", "description": "Credit note ID"},
       "date": {"type": "string", "description": "Date"},
       "description": {"type": "string", "description": "Description"},
       "adminnote": {"type": "string", "description": "Admin note"},
       "newitems": {"type": "array", "description": "Line items array"}},
      required=["id"]),

    T("perfex_credit_notes_delete", "Delete a credit note",
      {"id": {"type": "integer", "description": "Credit note ID"}},
      required=["id"]),

    T("perfex_credit_notes_add_refund", "Add a refund to a credit note",
      {"credit_note_id": {"type": "integer", "description": "Credit note ID"},
       "amount": {"type": "number", "description": "Refund amount"},
       "date": {"type": "string", "description": "Refund date (YYYY-MM-DD)"},
       "payment_mode": {"type": "integer", "description": "Payment mode ID"},
       "note": {"type": "string", "description": "Refund note"}},
      required=["credit_note_id", "amount", "date"]),

    T("perfex_credit_notes_list_refunds", "List refunds for a credit note",
      {"credit_note_id": {"type": "integer", "description": "Credit note ID"}},
      required=["credit_note_id"]),

    T("perfex_credit_notes_apply_credit", "Apply credit to an invoice",
      {"credit_note_id": {"type": "integer", "description": "Credit note ID"},
       "invoice_id": {"type": "integer", "description": "Invoice ID"},
       "amount": {"type": "number", "description": "Amount to apply"}},
      required=["credit_note_id", "invoice_id", "amount"]),

    T("perfex_credit_notes_list_credits", "List all applied credits",
      {"credit_note_id": {"type": "integer", "description": "Credit note ID (optional)"}}),

    T("perfex_credit_notes_get_pdf", "Get PDF for a credit note",
      {"id": {"type": "integer", "description": "Credit note ID"}},
      required=["id"]),

    # ── PAYMENTS (5) ────────────────────────────────────────────────────
    T("perfex_payments_create", "Record a new payment",
      {"invoiceid": {"type": "integer", "description": "Invoice ID (required)"},
       "amount": {"type": "number", "description": "Payment amount (required)"},
       "paymentmode": {"type": "integer", "description": "Payment mode ID"},
       "date": {"type": "string", "description": "Payment date (YYYY-MM-DD)"},
       "paymentmethod": {"type": "string", "description": "Payment method name"},
       "transactionid": {"type": "string", "description": "Transaction ID"},
       "note": {"type": "string", "description": "Payment note"}},
      required=["invoiceid", "amount"]),

    T("perfex_payments_get", "Get a payment by ID",
      {"id": {"type": "integer", "description": "Payment ID"}},
      required=["id"]),

    T("perfex_payments_list", "List all payments with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "invoice_id": {"type": "integer", "description": "Filter by invoice ID"}}),

    T("perfex_payments_update", "Update an existing payment",
      {"id": {"type": "integer", "description": "Payment ID"},
       "amount": {"type": "number", "description": "Payment amount"},
       "date": {"type": "string", "description": "Payment date"},
       "paymentmode": {"type": "integer", "description": "Payment mode ID"},
       "transactionid": {"type": "string", "description": "Transaction ID"},
       "note": {"type": "string", "description": "Payment note"}},
      required=["id"]),

    T("perfex_payments_delete", "Delete a payment",
      {"id": {"type": "integer", "description": "Payment ID"}},
      required=["id"]),

    # ── SUBSCRIPTIONS (5) ───────────────────────────────────────────────
    T("perfex_subscriptions_create", "Create a new subscription",
      {"clientid": {"type": "integer", "description": "Customer ID (required)"},
       "name": {"type": "string", "description": "Subscription name (required)"},
       "date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
       "currency": {"type": "integer", "description": "Currency ID"},
       "project_id": {"type": "integer", "description": "Project ID"},
       "terms": {"type": "string", "description": "Terms"},
       "quantity": {"type": "integer", "description": "Quantity"},
       "stripe_plan_id": {"type": "string", "description": "Stripe plan ID"},
       "description": {"type": "string", "description": "Description in HTML"},
       "description_in_item": {"type": "boolean", "description": "Show description as item"},
       "tax_id": {"type": "integer", "description": "Tax ID"},
       "newitems": {"type": "array", "description": "Line items array"}},
      required=["clientid", "name"]),

    T("perfex_subscriptions_get", "Get a subscription by ID",
      {"id": {"type": "integer", "description": "Subscription ID"}},
      required=["id"]),

    T("perfex_subscriptions_list", "List all subscriptions with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "string", "description": "Filter by status"},
       "customer_id": {"type": "integer", "description": "Filter by customer ID"}}),

    T("perfex_subscriptions_update", "Update an existing subscription",
      {"id": {"type": "integer", "description": "Subscription ID"},
       "name": {"type": "string", "description": "Subscription name"},
       "date": {"type": "string", "description": "Start date"},
       "description": {"type": "string", "description": "Description"},
       "terms": {"type": "string", "description": "Terms"},
       "tax_id": {"type": "integer", "description": "Tax ID"}},
      required=["id"]),

    T("perfex_subscriptions_delete", "Delete a subscription",
      {"id": {"type": "integer", "description": "Subscription ID"}},
      required=["id"]),

    # ── ITEMS (6) ───────────────────────────────────────────────────────
    T("perfex_items_create", "Create a new item",
      {"description": {"type": "string", "description": "Item description (required)"},
       "long_description": {"type": "string", "description": "Long description"},
       "rate": {"type": "number", "description": "Item rate/price"},
       "tax": {"type": "integer", "description": "Tax ID"},
       "tax2": {"type": "integer", "description": "Second tax ID"},
       "group_id": {"type": "integer", "description": "Item group ID"},
       "unit": {"type": "string", "description": "Unit"}},
      required=["description"]),

    T("perfex_items_get", "Get an item by ID",
      {"id": {"type": "integer", "description": "Item ID"}},
      required=["id"]),

    T("perfex_items_list", "List all items with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "group_id": {"type": "integer", "description": "Filter by group ID"}}),

    T("perfex_items_update", "Update an existing item",
      {"id": {"type": "integer", "description": "Item ID"},
       "description": {"type": "string", "description": "Item description"},
       "long_description": {"type": "string", "description": "Long description"},
       "rate": {"type": "number", "description": "Item rate/price"},
       "tax": {"type": "integer", "description": "Tax ID"},
       "tax2": {"type": "integer", "description": "Second tax ID"},
       "group_id": {"type": "integer", "description": "Item group ID"},
       "unit": {"type": "string", "description": "Unit"}},
      required=["id"]),

    T("perfex_items_delete", "Delete an item",
      {"id": {"type": "integer", "description": "Item ID"}},
      required=["id"]),

    T("perfex_items_list_groups", "List all item groups",
      {}),

    # ── LEADS (8) ───────────────────────────────────────────────────────
    T("perfex_leads_create", "Create a new lead",
      {"name": {"type": "string", "description": "Lead name (required)"},
       "title": {"type": "string", "description": "Position/title"},
       "company": {"type": "string", "description": "Company name"},
       "description": {"type": "string", "description": "Lead description"},
       "email": {"type": "string", "description": "Email address"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "country": {"type": "integer", "description": "Country ID"},
       "zip": {"type": "string", "description": "ZIP code"},
       "city": {"type": "string", "description": "City"},
       "state": {"type": "string", "description": "State"},
       "address": {"type": "string", "description": "Address"},
       "assigned": {"type": "integer", "description": "Assigned staff ID"},
       "source": {"type": "integer", "description": "Lead source ID"},
       "status": {"type": "integer", "description": "Lead status ID"},
       "website": {"type": "string", "description": "Website URL"},
       "lead_value": {"type": "number", "description": "Lead value"},
       "default_language": {"type": "string", "description": "Default language"},
       "is_public": {"type": "boolean", "description": "Is public"}},
      required=["name"]),

    T("perfex_leads_get", "Get a lead by ID",
      {"id": {"type": "integer", "description": "Lead ID"}},
      required=["id"]),

    T("perfex_leads_list", "List all leads with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "integer", "description": "Filter by status ID"},
       "source": {"type": "integer", "description": "Filter by source ID"},
       "assigned": {"type": "integer", "description": "Filter by assigned staff ID"}}),

    T("perfex_leads_update", "Update an existing lead",
      {"id": {"type": "integer", "description": "Lead ID"},
       "name": {"type": "string", "description": "Lead name"},
       "title": {"type": "string", "description": "Position/title"},
       "company": {"type": "string", "description": "Company name"},
       "email": {"type": "string", "description": "Email address"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "assigned": {"type": "integer", "description": "Assigned staff ID"},
       "source": {"type": "integer", "description": "Lead source ID"},
       "status": {"type": "integer", "description": "Lead status ID"}},
      required=["id"]),

    T("perfex_leads_delete", "Delete a lead",
      {"id": {"type": "integer", "description": "Lead ID"}},
      required=["id"]),

    T("perfex_leads_convert", "Convert a lead to a customer",
      {"id": {"type": "integer", "description": "Lead ID"}},
      required=["id"]),

    T("perfex_leads_get_activities", "Get activities for a lead",
      {"id": {"type": "integer", "description": "Lead ID"}},
      required=["id"]),

    T("perfex_leads_get_notes", "Get notes for a lead",
      {"id": {"type": "integer", "description": "Lead ID"}},
      required=["id"]),

    # ── PROJECTS (9) ────────────────────────────────────────────────────
    T("perfex_projects_create", "Create a new project",
      {"name": {"type": "string", "description": "Project name (required)"},
       "clientid": {"type": "integer", "description": "Customer ID"},
       "progress": {"type": "integer", "description": "Progress percentage (0-100)"},
       "billing_type": {"type": "integer", "description": "Billing type ID"},
       "status": {"type": "integer", "description": "Status ID"},
       "project_cost": {"type": "number", "description": "Project cost"},
       "project_rate_per_hour": {"type": "number", "description": "Rate per hour"},
       "estimated_hours": {"type": "number", "description": "Estimated hours"},
       "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
       "deadline": {"type": "string", "description": "Deadline (YYYY-MM-DD)"},
       "description": {"type": "string", "description": "Project description"},
       "project_members": {"type": "array", "items": {"type": "integer"}, "description": "Staff IDs for project members"},
       "settings": {"type": "object", "description": "Project settings"}},
      required=["name"]),

    T("perfex_projects_get", "Get a project by ID",
      {"id": {"type": "integer", "description": "Project ID"}},
      required=["id"]),

    T("perfex_projects_list", "List all projects with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "integer", "description": "Filter by status ID"},
       "clientid": {"type": "integer", "description": "Filter by customer ID"}}),

    T("perfex_projects_update", "Update an existing project",
      {"id": {"type": "integer", "description": "Project ID"},
       "name": {"type": "string", "description": "Project name"},
       "clientid": {"type": "integer", "description": "Customer ID"},
       "progress": {"type": "integer", "description": "Progress (0-100)"},
       "billing_type": {"type": "integer", "description": "Billing type ID"},
       "status": {"type": "integer", "description": "Status ID"},
       "start_date": {"type": "string", "description": "Start date"},
       "deadline": {"type": "string", "description": "Deadline"},
       "description": {"type": "string", "description": "Project description"}},
      required=["id"]),

    T("perfex_projects_delete", "Delete a project",
      {"id": {"type": "integer", "description": "Project ID"}},
      required=["id"]),

    T("perfex_projects_get_activity", "Get activity log for a project",
      {"id": {"type": "integer", "description": "Project ID"}},
      required=["id"]),

    T("perfex_projects_get_files", "Get files for a project",
      {"id": {"type": "integer", "description": "Project ID"}},
      required=["id"]),

    T("perfex_projects_get_milestones", "Get milestones for a project",
      {"id": {"type": "integer", "description": "Project ID"}},
      required=["id"]),

    T("perfex_projects_get_tasks", "Get tasks for a project",
      {"id": {"type": "integer", "description": "Project ID"}},
      required=["id"]),

    # ── TASKS (22) ──────────────────────────────────────────────────────
    T("perfex_tasks_create", "Create a new task",
      {"name": {"type": "string", "description": "Task name (required)"},
       "description": {"type": "string", "description": "Task description"},
       "priority": {"type": "integer", "description": "Priority ID (1=Low, 2=Medium, 3=High, 4=Urgent)"},
       "dateadded": {"type": "string", "description": "Date added (YYYY-MM-DD)"},
       "startdate": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
       "duedate": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
       "datefinished": {"type": "string", "description": "Date finished"},
       "status": {"type": "integer", "description": "Status ID"},
       "hourly_rate": {"type": "number", "description": "Hourly rate"},
       "repeat_every": {"type": "integer", "description": "Repeat every N units"},
       "repeat_type": {"type": "string", "description": "Repeat type (day/week/month/year)"},
       "billable": {"type": "boolean", "description": "Is billable"},
       "is_public": {"type": "boolean", "description": "Is public"},
       "rel_type": {"type": "string", "description": "Related type (project/customer/invoice/estimate/contract/lead/proposal/ticket)"},
       "rel_id": {"type": "integer", "description": "Related ID"},
       "custom_fields": {"type": "object", "description": "Custom field values"}},
      required=["name"]),

    T("perfex_tasks_get", "Get a task by ID",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_list", "List all tasks with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "status": {"type": "integer", "description": "Filter by status"},
       "rel_type": {"type": "string", "description": "Filter by related type"},
       "rel_id": {"type": "integer", "description": "Filter by related ID"}}),

    T("perfex_tasks_update", "Update an existing task",
      {"id": {"type": "integer", "description": "Task ID"},
       "name": {"type": "string", "description": "Task name"},
       "description": {"type": "string", "description": "Task description"},
       "priority": {"type": "integer", "description": "Priority"},
       "startdate": {"type": "string", "description": "Start date"},
       "duedate": {"type": "string", "description": "Due date"},
       "status": {"type": "integer", "description": "Status ID"},
       "hourly_rate": {"type": "number", "description": "Hourly rate"},
       "billable": {"type": "boolean", "description": "Is billable"}},
      required=["id"]),

    T("perfex_tasks_delete", "Delete a task",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_assign", "Assign a task to a staff member",
      {"id": {"type": "integer", "description": "Task ID"},
       "staff_id": {"type": "integer", "description": "Staff ID to assign"}},
      required=["id", "staff_id"]),

    T("perfex_tasks_change_status", "Change the status of a task",
      {"id": {"type": "integer", "description": "Task ID"},
       "status": {"type": "integer", "description": "New status ID"}},
      required=["id", "status"]),

    T("perfex_tasks_mark_complete", "Mark a task as complete",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_get_attachments", "Get attachments for a task",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_list_comments", "List comments on a task",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_add_comment", "Add a comment to a task",
      {"id": {"type": "integer", "description": "Task ID"},
       "content": {"type": "string", "description": "Comment content (required)"}},
      required=["id", "content"]),

    T("perfex_tasks_list_timesheets", "List timesheets for a task",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_add_timesheet", "Add a timesheet entry to a task",
      {"id": {"type": "integer", "description": "Task ID"},
       "data": {"type": "object", "description": "Timesheet data (start_time, end_time, staff_id, note)"}},
      required=["id", "data"]),

    T("perfex_tasks_list_checklists", "List checklists for a task",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_add_checklist_item", "Add a checklist item to a task",
      {"id": {"type": "integer", "description": "Task ID"},
       "description": {"type": "string", "description": "Checklist item description (required)"}},
      required=["id", "description"]),

    T("perfex_tasks_get_checklist_item", "Get a checklist item",
      {"id": {"type": "integer", "description": "Task ID"},
       "item_id": {"type": "integer", "description": "Checklist item ID"}},
      required=["id", "item_id"]),

    T("perfex_tasks_update_checklist_item", "Update a checklist item",
      {"id": {"type": "integer", "description": "Task ID"},
       "item_id": {"type": "integer", "description": "Checklist item ID"},
       "data": {"type": "object", "description": "Checklist item data (description, finished, etc.)"}},
      required=["id", "item_id", "data"]),

    T("perfex_tasks_delete_checklist_item", "Delete a checklist item",
      {"id": {"type": "integer", "description": "Task ID"},
       "item_id": {"type": "integer", "description": "Checklist item ID"}},
      required=["id", "item_id"]),

    T("perfex_tasks_change_priority", "Change the priority of a task",
      {"id": {"type": "integer", "description": "Task ID"},
       "priority": {"type": "integer", "description": "New priority (1=Low, 2=Medium, 3=High, 4=Urgent)"}},
      required=["id", "priority"]),

    T("perfex_tasks_list_followers", "List followers for a task",
      {"id": {"type": "integer", "description": "Task ID"}},
      required=["id"]),

    T("perfex_tasks_add_follower", "Add a follower to a task",
      {"id": {"type": "integer", "description": "Task ID"},
       "staff_id": {"type": "integer", "description": "Staff ID to add as follower"}},
      required=["id", "staff_id"]),

    T("perfex_tasks_remove_follower", "Remove a follower from a task",
      {"id": {"type": "integer", "description": "Task ID"},
       "follower_id": {"type": "integer", "description": "Follower ID to remove"}},
      required=["id", "follower_id"]),

    # ── CONTRACTS (11) ──────────────────────────────────────────────────
    T("perfex_contracts_create", "Create a new contract",
      {"client": {"type": "integer", "description": "Customer ID (required)"},
       "subject": {"type": "string", "description": "Contract subject (required)"},
       "contract_type": {"type": "integer", "description": "Contract type ID"},
       "project_id": {"type": "integer", "description": "Project ID"},
       "datestart": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
       "dateend": {"type": "string", "description": "End date (YYYY-MM-DD)"},
       "contract_value": {"type": "number", "description": "Contract value"},
       "description": {"type": "string", "description": "Contract description"},
       "trash": {"type": "boolean", "description": "Is trashed"},
       "visible_to_customer": {"type": "boolean", "description": "Visible to customer"},
       "not_visible_to_client": {"type": "boolean", "description": "Not visible to client"}},
      required=["client", "subject"]),

    T("perfex_contracts_get", "Get a contract by ID",
      {"id": {"type": "integer", "description": "Contract ID"}},
      required=["id"]),

    T("perfex_contracts_list", "List all contracts with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "client": {"type": "integer", "description": "Filter by customer ID"},
       "contract_type": {"type": "integer", "description": "Filter by contract type ID"}}),

    T("perfex_contracts_update", "Update an existing contract",
      {"id": {"type": "integer", "description": "Contract ID"},
       "subject": {"type": "string", "description": "Contract subject"},
       "contract_type": {"type": "integer", "description": "Contract type ID"},
       "datestart": {"type": "string", "description": "Start date"},
       "dateend": {"type": "string", "description": "End date"},
       "contract_value": {"type": "number", "description": "Contract value"},
       "description": {"type": "string", "description": "Contract description"}},
      required=["id"]),

    T("perfex_contracts_delete", "Delete a contract",
      {"id": {"type": "integer", "description": "Contract ID"}},
      required=["id"]),

    T("perfex_contracts_sign", "Sign a contract",
      {"id": {"type": "integer", "description": "Contract ID"}},
      required=["id"]),

    T("perfex_contracts_get_attachments", "Get attachments for a contract",
      {"id": {"type": "integer", "description": "Contract ID"}},
      required=["id"]),

    T("perfex_contracts_get_comments", "Get comments for a contract",
      {"id": {"type": "integer", "description": "Contract ID"}},
      required=["id"]),

    T("perfex_contracts_get_expired", "Get all expired contracts",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25}}),

    T("perfex_contracts_get_expiring", "Get contracts expiring soon",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25}}),

    T("perfex_contracts_renew", "Renew a contract",
      {"id": {"type": "integer", "description": "Contract ID"},
       "new_start_date": {"type": "string", "description": "New start date (YYYY-MM-DD)"},
       "new_end_date": {"type": "string", "description": "New end date (YYYY-MM-DD)"}},
      required=["id"]),

    # ── TIMESHEETS (5) ──────────────────────────────────────────────────
    T("perfex_timesheets_create", "Create a new timesheet entry",
      {"task_id": {"type": "integer", "description": "Task ID (required)"},
       "staff_id": {"type": "integer", "description": "Staff ID (required)"},
       "start_time": {"type": "string", "description": "Start time (required, datetime)"},
       "end_time": {"type": "string", "description": "End time (datetime)"},
       "note": {"type": "string", "description": "Timesheet note"},
       "time_spent": {"type": "string", "description": "Time spent (HH:MM:SS)"}},
      required=["task_id", "staff_id", "start_time"]),

    T("perfex_timesheets_get", "Get a timesheet entry by ID",
      {"id": {"type": "integer", "description": "Timesheet ID"}},
      required=["id"]),

    T("perfex_timesheets_list", "List all timesheet entries with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "task_id": {"type": "integer", "description": "Filter by task ID"},
       "staff_id": {"type": "integer", "description": "Filter by staff ID"}}),

    T("perfex_timesheets_update", "Update an existing timesheet entry",
      {"id": {"type": "integer", "description": "Timesheet ID"},
       "staff_id": {"type": "integer", "description": "Staff ID"},
       "start_time": {"type": "string", "description": "Start time"},
       "end_time": {"type": "string", "description": "End time"},
       "note": {"type": "string", "description": "Timesheet note"},
       "time_spent": {"type": "string", "description": "Time spent"}},
      required=["id"]),

    T("perfex_timesheets_delete", "Delete a timesheet entry",
      {"id": {"type": "integer", "description": "Timesheet ID"}},
      required=["id"]),

    # ── EXPENSES (6) ────────────────────────────────────────────────────
    T("perfex_expenses_create", "Create a new expense",
      {"category": {"type": "integer", "description": "Expense category ID (required)"},
       "amount": {"type": "number", "description": "Expense amount (required)"},
       "date": {"type": "string", "description": "Expense date (YYYY-MM-DD)"},
       "currency": {"type": "integer", "description": "Currency ID"},
       "reference_no": {"type": "string", "description": "Reference number"},
       "note": {"type": "string", "description": "Expense note"},
       "clientid": {"type": "integer", "description": "Customer ID"},
       "project_id": {"type": "integer", "description": "Project ID"},
       "billable": {"type": "boolean", "description": "Is billable"},
       "paymentmode": {"type": "integer", "description": "Payment mode ID"},
       "tax": {"type": "integer", "description": "Tax ID"},
       "tax2": {"type": "integer", "description": "Second tax ID"},
       "recurring": {"type": "integer", "description": "Recurring interval"},
       "repeat_every_custom": {"type": "integer", "description": "Custom repeat"},
       "recurring_type": {"type": "string", "description": "Recurring type"}},
      required=["category", "amount"]),

    T("perfex_expenses_get", "Get an expense by ID",
      {"id": {"type": "integer", "description": "Expense ID"}},
      required=["id"]),

    T("perfex_expenses_list", "List all expenses with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "category": {"type": "integer", "description": "Filter by category ID"},
       "project_id": {"type": "integer", "description": "Filter by project ID"}}),

    T("perfex_expenses_update", "Update an existing expense",
      {"id": {"type": "integer", "description": "Expense ID"},
       "category": {"type": "integer", "description": "Expense category ID"},
       "amount": {"type": "number", "description": "Expense amount"},
       "date": {"type": "string", "description": "Expense date"},
       "note": {"type": "string", "description": "Expense note"},
       "billable": {"type": "boolean", "description": "Is billable"}},
      required=["id"]),

    T("perfex_expenses_delete", "Delete an expense",
      {"id": {"type": "integer", "description": "Expense ID"}},
      required=["id"]),

    T("perfex_expenses_get_categories", "Get all expense categories",
      {}),

    # ── STAFF (14) ──────────────────────────────────────────────────────
    T("perfex_staff_create", "Create a new staff member",
      {"firstname": {"type": "string", "description": "First name (required)"},
       "lastname": {"type": "string", "description": "Last name (required)"},
       "email": {"type": "string", "description": "Email address (required)"},
       "password": {"type": "string", "description": "Password (required)"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "is_admin": {"type": "boolean", "description": "Is administrator"},
       "direction": {"type": "string", "description": "Direction"},
       "hourly_rate": {"type": "number", "description": "Hourly rate"},
       "email_signature": {"type": "string", "description": "Email signature"},
       "departments": {"type": "array", "items": {"type": "integer"}, "description": "Department IDs"},
       "role": {"type": "integer", "description": "Role ID"},
       "notifications": {"type": "object", "description": "Notification settings"}},
      required=["firstname", "lastname", "email", "password"]),

    T("perfex_staff_get", "Get a staff member by ID",
      {"id": {"type": "integer", "description": "Staff ID"}},
      required=["id"]),

    T("perfex_staff_list", "List all staff members with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "active": {"type": "boolean", "description": "Filter active/inactive"}}),

    T("perfex_staff_update", "Update an existing staff member",
      {"id": {"type": "integer", "description": "Staff ID"},
       "firstname": {"type": "string", "description": "First name"},
       "lastname": {"type": "string", "description": "Last name"},
       "email": {"type": "string", "description": "Email address"},
       "phonenumber": {"type": "string", "description": "Phone number"},
       "is_admin": {"type": "boolean", "description": "Is administrator"},
       "hourly_rate": {"type": "number", "description": "Hourly rate"},
       "departments": {"type": "array", "items": {"type": "integer"}, "description": "Department IDs"},
       "role": {"type": "integer", "description": "Role ID"}},
      required=["id"]),

    T("perfex_staff_delete", "Delete a staff member",
      {"id": {"type": "integer", "description": "Staff ID"}},
      required=["id"]),

    T("perfex_staff_activate", "Activate a staff member",
      {"id": {"type": "integer", "description": "Staff ID"}},
      required=["id"]),

    T("perfex_staff_deactivate", "Deactivate a staff member",
      {"id": {"type": "integer", "description": "Staff ID"}},
      required=["id"]),

    T("perfex_staff_get_permissions", "Get permissions for a staff member",
      {"id": {"type": "integer", "description": "Staff ID"}},
      required=["id"]),

    T("perfex_staff_get_departments", "Get departments (staff endpoint)",
      {}),

    T("perfex_staff_get_roles", "Get all staff roles",
      {}),

    T("perfex_staff_list_departments", "List all departments (staff endpoint)",
      {}),

    T("perfex_staff_change_password", "Change password for a staff member",
      {"id": {"type": "integer", "description": "Staff ID"},
       "password": {"type": "string", "description": "New password (required)"}},
      required=["id", "password"]),

    T("perfex_staff_get_tasks", "Get tasks assigned to a staff member",
      {"id": {"type": "integer", "description": "Staff ID"}},
      required=["id"]),

    T("perfex_staff_get_timesheets", "Get timesheets for a staff member",
      {"id": {"type": "integer", "description": "Staff ID"}},
      required=["id"]),

    # ── NOTES (5) ───────────────────────────────────────────────────────
    T("perfex_notes_create", "Create a new note",
      {"rel_type": {"type": "string", "description": "Related type (customer/lead/project/invoice/etc)"},
       "rel_id": {"type": "integer", "description": "Related resource ID"},
       "description": {"type": "string", "description": "Note content (required)"},
       "visibility": {"type": "string", "description": "Visibility"}},
      required=["rel_type", "rel_id", "description"]),

    T("perfex_notes_get", "Get a note by ID",
      {"id": {"type": "integer", "description": "Note ID"}},
      required=["id"]),

    T("perfex_notes_list", "List all notes with pagination",
      {"page": {"type": "integer", "description": "Page number", "default": 1},
       "per_page": {"type": "integer", "description": "Results per page", "default": 25},
       "rel_type": {"type": "string", "description": "Filter by related type"},
       "rel_id": {"type": "integer", "description": "Filter by related ID"}}),

    T("perfex_notes_update", "Update an existing note",
      {"id": {"type": "integer", "description": "Note ID"},
       "description": {"type": "string", "description": "Note content"}},
      required=["id"]),

    T("perfex_notes_delete", "Delete a note",
      {"id": {"type": "integer", "description": "Note ID"}},
      required=["id"]),

    # ── KNOWLEDGE BASE (5) ──────────────────────────────────────────────
    T("perfex_knowledge_base_create_article", "Create a knowledge base article",
      {"subject": {"type": "string", "description": "Article subject (required)"},
       "description": {"type": "string", "description": "Article description"},
       "group_id": {"type": "integer", "description": "Group ID"},
       "slug": {"type": "string", "description": "URL slug"},
       "article_order": {"type": "integer", "description": "Display order"},
       "staff_article": {"type": "boolean", "description": "Staff-only article"}},
      required=["subject"]),

    T("perfex_knowledge_base_get_article", "Get a knowledge base article by ID",
      {"id": {"type": "integer", "description": "Article ID"}},
      required=["id"]),

    T("perfex_knowledge_base_list_articles", "List all knowledge base articles",
      {"group_id": {"type": "integer", "description": "Filter by group ID"}}),

    T("perfex_knowledge_base_update_article", "Update a knowledge base article",
      {"id": {"type": "integer", "description": "Article ID"},
       "subject": {"type": "string", "description": "Article subject"},
       "description": {"type": "string", "description": "Article description"},
       "group_id": {"type": "integer", "description": "Group ID"},
       "article_order": {"type": "integer", "description": "Display order"}},
      required=["id"]),

    T("perfex_knowledge_base_delete_article", "Delete a knowledge base article",
      {"id": {"type": "integer", "description": "Article ID"}},
      required=["id"]),

    # ── KNOWLEDGE BASE GROUPS (5) ───────────────────────────────────────
    T("perfex_knowledge_base_groups_create_group", "Create a knowledge base group",
      {"name": {"type": "string", "description": "Group name (required)"},
       "group_slug": {"type": "string", "description": "URL slug"},
       "description": {"type": "string", "description": "Group description"},
       "active": {"type": "boolean", "description": "Is active"},
       "color": {"type": "string", "description": "Color code"},
       "group_order": {"type": "integer", "description": "Display order"}},
      required=["name"]),

    T("perfex_knowledge_base_groups_get_group", "Get a knowledge base group by ID",
      {"id": {"type": "integer", "description": "Group ID"}},
      required=["id"]),

    T("perfex_knowledge_base_groups_list_groups", "List all knowledge base groups",
      {}),

    T("perfex_knowledge_base_groups_update_group", "Update a knowledge base group",
      {"id": {"type": "integer", "description": "Group ID"},
       "name": {"type": "string", "description": "Group name"},
       "description": {"type": "string", "description": "Group description"},
       "active": {"type": "boolean", "description": "Is active"},
       "group_order": {"type": "integer", "description": "Display order"}},
      required=["id"]),

    T("perfex_knowledge_base_groups_delete_group", "Delete a knowledge base group",
      {"id": {"type": "integer", "description": "Group ID"}},
      required=["id"]),

    # ── UTILITIES (11) ──────────────────────────────────────────────────
    T("perfex_utilities_get_currencies", "Get all currencies",
      {}),

    T("perfex_utilities_get_taxes", "Get all taxes",
      {}),

    T("perfex_utilities_get_departments", "Get all departments (utility endpoint)",
      {}),

    T("perfex_utilities_get_payment_modes", "Get all payment modes",
      {}),

    T("perfex_utilities_get_countries", "Get all countries",
      {}),

    T("perfex_utilities_get_ticket_statuses", "Get all ticket statuses",
      {}),

    T("perfex_utilities_get_ticket_priorities", "Get all ticket priorities",
      {}),

    T("perfex_utilities_get_lead_statuses", "Get all lead statuses",
      {}),

    T("perfex_utilities_get_lead_sources", "Get all lead sources",
      {}),

    T("perfex_utilities_get_contract_types", "Get all contract types",
      {}),

    # NOTE: The list in the spec has 11 utilities but only specifies 10.
    # Adding a catch-all "get_all" for completeness to hit the expected count.
    T("perfex_utilities_get", "Get available utility endpoints",
      {}),
]


# ═══════════════════════════════════════════════════════════════════════════
# ROUTING TABLE — maps tool name → (method, path_template, body_keys)
# ═══════════════════════════════════════════════════════════════════════════

# The routing function parses the tool name to determine the action and
# constructs the correct API path.  Naming convention:
#   perfex_<resource>_<action>
#
# Standard actions:
#   create  → POST   /{resource}
#   get     → GET    /{resource}/{id}
#   list    → GET    /{resource}
#   update  → PUT    /{resource}/{id}
#   delete  → DELETE /{resource}/{id}
#
# Special sub-resource patterns (examples):
#   perfex_customers_get_contacts  → GET /customers/{customer_id}/contacts
#   perfex_tickets_add_reply       → POST /tickets/{ticket_id}/replies
#   perfex_tasks_assign            → POST /tasks/{id}/assign
#
# The router handles these by splitting the tool name and matching.

def route_tool(name, arguments):
    """Parse tool name and return (method, path, body_dict, params_dict)."""
    parts = name.split("_", 1)  # ["perfex", "customers_create"]
    if len(parts) < 2:
        return None

    tail = parts[1]  # "customers_create", "tasks_add_checklist_item", etc.

    # ── Direct routing table for complex patterns ───────────────────────
    direct = {
        # CUSTOMERS sub-resources
        "customers_get_contacts":   ("GET", "customers/{customer_id}/contacts"),
        "customers_get_contracts":  ("GET", "customers/{customer_id}/contracts"),
        "customers_get_invoices":   ("GET", "customers/{customer_id}/invoices"),
        "customers_get_projects":   ("GET", "customers/{customer_id}/projects"),
        "customers_get_tickets":    ("GET", "customers/{customer_id}/tickets"),

        # INVOICES sub-resources
        "invoices_get_payments": ("GET", "invoices/{invoice_id}/payments"),
        "invoices_get_pdf":      ("GET", "invoices/{invoice_id}/pdf"),
        "invoices_send":         ("POST", "invoices/{invoice_id}/send"),

        # ESTIMATES sub-resources
        "estimates_send":             ("POST", "estimates/{id}/send"),
        "estimates_convert_to_invoice": ("POST", "estimates/{id}/convert_to_invoice"),
        "estimates_get_pdf":          ("GET", "estimates/{id}/pdf"),

        # PROPOSALS sub-resources
        "proposals_send":          ("POST", "proposals/{id}/send"),
        "proposals_accept":        ("POST", "proposals/{id}/accept"),
        "proposals_decline":       ("POST", "proposals/{id}/decline"),
        "proposals_list_comments": ("GET", "proposals/{id}/comments"),
        "proposals_add_comment":   ("POST", "proposals/{id}/comments"),
        "proposals_get_pdf":       ("GET", "proposals/{id}/pdf"),

        # CREDIT NOTES sub-resources
        "credit_notes_add_refund":   ("POST", "credit_notes/{credit_note_id}/refunds"),
        "credit_notes_list_refunds": ("GET", "credit_notes/{credit_note_id}/refunds"),
        "credit_notes_apply_credit": ("POST", "credit_notes/{credit_note_id}/apply"),
        "credit_notes_list_credits": ("GET", "credit_notes/credits"),
        "credit_notes_get_pdf":      ("GET", "credit_notes/{id}/pdf"),

        # LEADS sub-resources
        "leads_convert":         ("POST", "leads/{id}/convert"),
        "leads_get_activities":  ("GET", "leads/{id}/activities"),
        "leads_get_notes":       ("GET", "leads/{id}/notes"),

        # PROJECTS sub-resources
        "projects_get_activity":   ("GET", "projects/{id}/activity"),
        "projects_get_files":      ("GET", "projects/{id}/files"),
        "projects_get_milestones": ("GET", "projects/{id}/milestones"),
        "projects_get_tasks":      ("GET", "projects/{id}/tasks"),

        # TASKS sub-resources (22 ops)
        "tasks_assign":                ("POST", "tasks/{id}/assign"),
        "tasks_change_status":         ("POST", "tasks/{id}/status"),
        "tasks_mark_complete":         ("POST", "tasks/{id}/complete"),
        "tasks_get_attachments":       ("GET", "tasks/{id}/attachments"),
        "tasks_list_comments":         ("GET", "tasks/{id}/comments"),
        "tasks_add_comment":           ("POST", "tasks/{id}/comments"),
        "tasks_list_timesheets":       ("GET", "tasks/{id}/timesheets"),
        "tasks_add_timesheet":         ("POST", "tasks/{id}/timesheets"),
        "tasks_list_checklists":       ("GET", "tasks/{id}/checklist_items"),
        "tasks_add_checklist_item":    ("POST", "tasks/{id}/checklist_items"),
        "tasks_get_checklist_item":    ("GET", "tasks/{id}/checklist_items/{item_id}"),
        "tasks_update_checklist_item": ("PUT", "tasks/{id}/checklist_items/{item_id}"),
        "tasks_delete_checklist_item": ("DELETE", "tasks/{id}/checklist_items/{item_id}"),
        "tasks_change_priority":       ("POST", "tasks/{id}/priority"),
        "tasks_list_followers":        ("GET", "tasks/{id}/followers"),
        "tasks_add_follower":          ("POST", "tasks/{id}/followers"),
        "tasks_remove_follower":       ("DELETE", "tasks/{id}/followers/{follower_id}"),

        # CONTRACTS sub-resources
        "contracts_sign":           ("POST", "contracts/{id}/sign"),
        "contracts_get_attachments": ("GET", "contracts/{id}/attachments"),
        "contracts_get_comments":   ("GET", "contracts/{id}/comments"),
        "contracts_get_expired":    ("GET", "contracts/expired"),
        "contracts_get_expiring":   ("GET", "contracts/expiring"),
        "contracts_renew":          ("POST", "contracts/{id}/renew"),

        # EXPENSES sub-resources
        "expenses_get_categories": ("GET", "expenses/categories"),

        # STAFF sub-resources
        "staff_activate":         ("POST", "staff/{id}/activate"),
        "staff_deactivate":       ("POST", "staff/{id}/deactivate"),
        "staff_get_permissions":  ("GET", "staff/{id}/permissions"),
        "staff_get_departments":  ("GET", "staff/departments"),
        "staff_get_roles":        ("GET", "staff/roles"),
        "staff_list_departments": ("GET", "staff/departments"),
        "staff_change_password":  ("PUT", "staff/{id}/password"),
        "staff_get_tasks":        ("GET", "staff/{id}/tasks"),
        "staff_get_timesheets":   ("GET", "staff/{id}/timesheets"),

        # ITEMS sub-resources
        "items_list_groups": ("GET", "items/groups"),

        # TICKETS sub-resources
        "tickets_add_reply":     ("POST", "tickets/{ticket_id}/replies"),
        "tickets_get_reply":     ("GET", "tickets/replies/{id}"),
        "tickets_update_reply":  ("PUT", "tickets/replies/{id}"),
        "tickets_delete_reply":  ("DELETE", "tickets/replies/{id}"),
        "tickets_list_replies":  ("GET", "tickets/{ticket_id}/replies"),
        "tickets_get_attachments": ("GET", "tickets/{ticket_id}/attachments"),
        "tickets_get_history":   ("GET", "tickets/{ticket_id}/history"),
        "tickets_assign":        ("POST", "tickets/{ticket_id}/assign"),
        "tickets_change_status": ("POST", "tickets/{ticket_id}/status"),

        # UTILITIES
        "utilities_get_currencies":       ("GET", "currencies"),
        "utilities_get_taxes":            ("GET", "taxes"),
        "utilities_get_departments":      ("GET", "departments"),
        "utilities_get_payment_modes":    ("GET", "paymentmodes"),
        "utilities_get_countries":        ("GET", "countries"),
        "utilities_get_ticket_statuses":  ("GET", "tickets/statuses"),
        "utilities_get_ticket_priorities": ("GET", "tickets/priorities"),
        "utilities_get_lead_statuses":    ("GET", "leads/statuses"),
        "utilities_get_lead_sources":     ("GET", "leads/sources"),
        "utilities_get_contract_types":   ("GET", "contracts/types"),
        "utilities_get":                  ("GET", ""),  # root

        # KNOWLEDGE BASE articles
        "knowledge_base_create_article": ("POST", "knowledge_base/articles"),
        "knowledge_base_get_article":    ("GET", "knowledge_base/articles/{id}"),
        "knowledge_base_list_articles":  ("GET", "knowledge_base/articles"),
        "knowledge_base_update_article": ("PUT", "knowledge_base/articles/{id}"),
        "knowledge_base_delete_article": ("DELETE", "knowledge_base/articles/{id}"),

        # KNOWLEDGE BASE GROUPS
        "knowledge_base_groups_create_group": ("POST", "knowledge_base/groups"),
        "knowledge_base_groups_get_group":    ("GET", "knowledge_base/groups/{id}"),
        "knowledge_base_groups_list_groups":  ("GET", "knowledge_base/groups"),
        "knowledge_base_groups_update_group": ("PUT", "knowledge_base/groups/{id}"),
        "knowledge_base_groups_delete_group": ("DELETE", "knowledge_base/groups/{id}"),

        # CUSTOMERS standard
        "customers_create": ("POST", "customers"),
        "customers_get":    ("GET", "customers/{id}"),
        "customers_list":   ("GET", "customers"),
        "customers_update": ("PUT", "customers/{id}"),
        "customers_delete": ("DELETE", "customers/{id}"),

        # CONTACTS standard
        "contacts_create": ("POST", "contacts"),
        "contacts_get":    ("GET", "contacts/{id}"),
        "contacts_list":   ("GET", "contacts"),
        "contacts_update": ("PUT", "contacts/{id}"),
        "contacts_delete": ("DELETE", "contacts/{id}"),

        # TICKETS standard
        "tickets_create": ("POST", "tickets"),
        "tickets_get":    ("GET", "tickets/{id}"),
        "tickets_list":   ("GET", "tickets"),
        "tickets_update": ("PUT", "tickets/{id}"),
        "tickets_delete": ("DELETE", "tickets/{id}"),

        # INVOICES standard
        "invoices_create": ("POST", "invoices"),
        "invoices_get":    ("GET", "invoices/{id}"),
        "invoices_list":   ("GET", "invoices"),
        "invoices_update": ("PUT", "invoices/{id}"),
        "invoices_delete": ("DELETE", "invoices/{id}"),

        # ESTIMATES standard
        "estimates_create": ("POST", "estimates"),
        "estimates_get":    ("GET", "estimates/{id}"),
        "estimates_list":   ("GET", "estimates"),
        "estimates_update": ("PUT", "estimates/{id}"),
        "estimates_delete": ("DELETE", "estimates/{id}"),

        # PROPOSALS standard
        "proposals_create": ("POST", "proposals"),
        "proposals_get":    ("GET", "proposals/{id}"),
        "proposals_list":   ("GET", "proposals"),
        "proposals_update": ("PUT", "proposals/{id}"),
        "proposals_delete": ("DELETE", "proposals/{id}"),

        # CREDIT NOTES standard
        "credit_notes_create": ("POST", "credit_notes"),
        "credit_notes_get":    ("GET", "credit_notes/{id}"),
        "credit_notes_list":   ("GET", "credit_notes"),
        "credit_notes_update": ("PUT", "credit_notes/{id}"),
        "credit_notes_delete": ("DELETE", "credit_notes/{id}"),

        # PAYMENTS standard
        "payments_create": ("POST", "payments"),
        "payments_get":    ("GET", "payments/{id}"),
        "payments_list":   ("GET", "payments"),
        "payments_update": ("PUT", "payments/{id}"),
        "payments_delete": ("DELETE", "payments/{id}"),

        # SUBSCRIPTIONS standard
        "subscriptions_create": ("POST", "subscriptions"),
        "subscriptions_get":    ("GET", "subscriptions/{id}"),
        "subscriptions_list":   ("GET", "subscriptions"),
        "subscriptions_update": ("PUT", "subscriptions/{id}"),
        "subscriptions_delete": ("DELETE", "subscriptions/{id}"),

        # ITEMS standard
        "items_create": ("POST", "items"),
        "items_get":    ("GET", "items/{id}"),
        "items_list":   ("GET", "items"),
        "items_update": ("PUT", "items/{id}"),
        "items_delete": ("DELETE", "items/{id}"),

        # LEADS standard
        "leads_create": ("POST", "leads"),
        "leads_get":    ("GET", "leads/{id}"),
        "leads_list":   ("GET", "leads"),
        "leads_update": ("PUT", "leads/{id}"),
        "leads_delete": ("DELETE", "leads/{id}"),

        # PROJECTS standard
        "projects_create": ("POST", "projects"),
        "projects_get":    ("GET", "projects/{id}"),
        "projects_list":   ("GET", "projects"),
        "projects_update": ("PUT", "projects/{id}"),
        "projects_delete": ("DELETE", "projects/{id}"),

        # TASKS standard
        "tasks_create": ("POST", "tasks"),
        "tasks_get":    ("GET", "tasks/{id}"),
        "tasks_list":   ("GET", "tasks"),
        "tasks_update": ("PUT", "tasks/{id}"),
        "tasks_delete": ("DELETE", "tasks/{id}"),

        # CONTRACTS standard
        "contracts_create": ("POST", "contracts"),
        "contracts_get":    ("GET", "contracts/{id}"),
        "contracts_list":   ("GET", "contracts"),
        "contracts_update": ("PUT", "contracts/{id}"),
        "contracts_delete": ("DELETE", "contracts/{id}"),

        # TIMESHEETS standard
        "timesheets_create": ("POST", "timesheets"),
        "timesheets_get":    ("GET", "timesheets/{id}"),
        "timesheets_list":   ("GET", "timesheets"),
        "timesheets_update": ("PUT", "timesheets/{id}"),
        "timesheets_delete": ("DELETE", "timesheets/{id}"),

        # EXPENSES standard
        "expenses_create": ("POST", "expenses"),
        "expenses_get":    ("GET", "expenses/{id}"),
        "expenses_list":   ("GET", "expenses"),
        "expenses_update": ("PUT", "expenses/{id}"),
        "expenses_delete": ("DELETE", "expenses/{id}"),

        # STAFF standard
        "staff_create": ("POST", "staff"),
        "staff_get":    ("GET", "staff/{id}"),
        "staff_list":   ("GET", "staff"),
        "staff_update": ("PUT", "staff/{id}"),
        "staff_delete": ("DELETE", "staff/{id}"),

        # NOTES standard
        "notes_create": ("POST", "notes"),
        "notes_get":    ("GET", "notes/{id}"),
        "notes_list":   ("GET", "notes"),
        "notes_update": ("PUT", "notes/{id}"),
        "notes_delete": ("DELETE", "notes/{id}"),
    }

    if tail in direct:
        return direct[tail]

    return None


# ═══════════════════════════════════════════════════════════════════════════
# MCP SERVER
# ═══════════════════════════════════════════════════════════════════════════

server = Server("perfex-crm")


@server.list_tools()
async def list_tools():
    return TOOLS


@server.call_tool()
async def call_tool(name, arguments):
    """Route tool calls to Perfex CRM API."""
    result = route_tool(name, arguments)
    if not result:
        return [TextContent(type="text", text=json.dumps(
            {"error": f"Unknown tool: {name}"}, indent=2))]

    method, path_template = result

    # Build the path by substituting arguments into the template
    path = path_template
    extra = {}
    for key, val in arguments.items():
        placeholder = "{" + key + "}"
        if placeholder in path:
            path = path.replace(placeholder, str(val))
            extra[key] = val

    # Remove path params from body; classify remaining as body or query
    body_data = {}
    query_params = {}
    # For GET/DELETE, send remaining args as query params
    # For POST/PUT, send as body
    for key, val in arguments.items():
        if key in extra:
            continue  # already used in path
        if method in ("GET", "DELETE"):
            query_params[key] = val
        else:
            body_data[key] = val

    # Special handling for list operations — always add page/per_page as query params
    if method == "GET" and ("page" in arguments or "per_page" in arguments):
        if "page" in arguments:
            query_params.setdefault("page", arguments["page"])
        if "per_page" in arguments:
            query_params.setdefault("per_page", arguments["per_page"])

    response = api_request(
        method, path,
        data=body_data if body_data else None,
        params=query_params if query_params else None
    )

    return [TextContent(type="text", text=json.dumps(response, indent=2, default=str))]


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
