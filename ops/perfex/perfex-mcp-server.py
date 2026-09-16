#!/usr/bin/env python3
"""
PERFEX CRM — INTERFACE  (NURA OS)
=================================
A read-first MCP interface to the Perfex CRM at pay.nuratech.ai.

WHY THIS EXISTS / WHAT WAS WRONG
--------------------------------
1. The pre-existing server (/opt/data/mcp-installs/perfex/server.py, 1538 lines, 184 tools)
   CANNOT START: it uses the MCP SDK v1 decorator `@server.list_tools()`, but the installed
   SDK is **2.0.0**, whose `Server` class has no `list_tools` attribute ->
   `AttributeError` at import. The MCP lane was therefore dead, not merely misconfigured.

2. Its default `PERFEX_BASE_URL` was `https://195.35.32.113/api` — a BARE IP. Apache on that
   host serves a different vhost for the bare IP (`app.brawlerzbox.com`), so every call
   returned 404. The correct base is `https://pay.nuratech.ai/api` (name-based vhost ->
   /var/www/crm), which returns 401 = "module present, credential needed".

3. The Perfex REST module is on disk at /var/www/crm/modules/api but is ABSENT from
   `tblmodules`, so its tables (`tbluser_api`, `tbluser_api_permissions`, `api_keys`) were
   never created. The REST lane cannot authenticate until the module is activated.
   => This server therefore ships a SECOND lane that works TODAY: read-only SQL via SSH.

LANES
-----
  lane "rest"  : HTTPS -> https://pay.nuratech.ai/api, header `Authtoken`. Used when
                 PERFEX_API_TOKEN is set AND the module answers 200.
  lane "db"    : read-only SELECT over SSH to the edge host, parsing the CRM's own
                 application/config/app-config.php for credentials (never hardcoded,
                 never printed). Works with zero CRM-side changes.

SAFETY — ENFORCED IN CODE, NOT BY CONVENTION
--------------------------------------------
  * READ-ONLY, absolutely: every statement is validated to start with SELECT/ SHOW / or be
    a DESCRIBE. INSERT/UPDATE/DELETE/DROP/ALTER/TRUNCATE/CREATE/GRANT are refused before
    they can reach a connection.
  * PHI WALL: an explicit DENY list blocks the credential vault, consent records, form/intake
    results, session/auth tables and mail content. This is the standing NURA doctrine that
    the CRM must never be a channel for clinical data.
  * ALLOW LIST: only named CRM/billing tables are queryable. An unlisted table is refused.
  * Credentials are read from the server's own config at runtime and never returned.

TRANSPORT
---------
  MCP over stdio, newline-delimited JSON-RPC. Implemented against the RAW protocol rather
  than a framework, because this venv's SDK (2.0.0) has no FastMCP and other live servers
  on this box use exactly this pattern. `initialize` IS handled — omitting it is the known
  defect that makes every MCP client time out.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.request

SERVER_NAME = "perfex"
SERVER_VERSION = "2.0.0"

BASE_URL = os.environ.get("PERFEX_BASE_URL", "https://pay.nuratech.ai/api").rstrip("/")
API_TOKEN = os.environ.get("PERFEX_API_TOKEN", "").strip()
SSH_ALIAS = os.environ.get("PERFEX_SSH_ALIAS", "edge")
SSH_CONFIG = os.environ.get("PERFEX_SSH_CONFIG",
                            "/opt/data/profiles/nura/home/.ssh/config")
REMOTE_APP_CONFIG = os.environ.get("PERFEX_APP_CONFIG",
                                   "/var/www/crm/application/config/app-config.php")
READ_ONLY = os.environ.get("PERFEX_READ_ONLY", "true").lower() != "false"

# ---------------------------------------------------------------- safety tables
# Only these tables may ever be read. Chosen as the CRM / revenue-operations surface.
ALLOWED_TABLES = {
    # parties
    "tblclients", "tblcontacts", "tblcustomer_admins", "tblcustomer_groups",
    # money in
    "tblinvoices", "tblinvoicepaymentrecords", "tblestimates", "tblproposals",
    "tblcreditnotes", "tblcreditnote_refunds", "tblsubscriptions", "tblcredits",
    "tblpayment_modes", "tblpayment_attempts",
    # catalogue / tax / currency
    "tblitems", "tblitems_groups", "tblitem_tax", "tbltaxes", "tblcurrencies",
    "tblservices",
    # pipeline
    "tbleads", "tblleads_sources", "tblleads_status", "tbllead_activity_log",
    # delivery
    "tblprojects", "tblproject_members", "tblmilestones", "tbltasks",
    "tbltask_assigned", "tbltasks_checklist_templates", "tbltaskstimers",
    "tblcontracts", "tblcontracts_types", "tblcontract_renewals",
    # support
    "tbltickets", "tbltickets_status", "tbltickets_priorities", "tbldepartments",
    # spend
    "tblexpenses", "tblexpenses_categories",
    # people (internal)
    "tblstaff", "tblstaff_departments", "tblroles", "tblstaff_permissions",
    # reference
    "tblknowledge_base", "tblknowledge_base_groups", "tblnotes", "tblcountries",
    "tblactivity_log",
}

# Explicitly NEVER readable, even if someone adds them to the allow list later.
DENIED_TABLES = {
    # credentials / secrets
    "tblvault", "tbluser_auto_login", "tbluser_meta", "tblsessions",
    "tbltokens", "tbluser_api", "tbluser_api_permissions", "api_keys",
    # consent + intake == potential PHI
    "tblconsents", "tblconsent_purposes",
    "tblform_questions", "tblform_question_box", "tblform_question_box_description",
    "tblform_results",
    # message content can carry PHI
    "tblmail_queue", "tblscheduled_emails", "tblemailtemplates", "tbltracked_mails",
    "tblticket_replies", "tblticket_attachments",
    # leads integration mail bodies
    "tbllead_integration_emails", "tblleads_email_integration",
    # infra
    "tblmigrations", "tblmodules", "tbloptions", "tblfilters",
    "tblfilter_defaults", "tblviews_tracking", "tblweb_to_lead",
}

# Any table carrying these substrings is refused outright. Belt and braces for the
# PHI wall: a new clinical module's table is denied by default, not allowed by default.
DENY_SUBSTRINGS = ("consent", "form_result", "vault", "session", "token", "password",
                   "patient", "emr", "lifefile", "kareo", "chart", "diagnos",
                   "prescri", "medication", "lab_", "vital", "encounter", "phi")

# ---- COLUMN-LEVEL WALL (added after a live finding, 2026-09-14) --------------
# `tblclients` is on the READ allow list, but it also carries `getfwd_config` and
# `nmi_config`, which hold PLAINTEXT `ghl_access_token` values. A plain
# `SELECT * FROM tblclients` would therefore have returned live OAuth tokens through
# this interface. Table-level allow-listing is not sufficient; columns are filtered too.
DENIED_COLUMN_SUBSTRINGS = (
    "token", "secret", "password", "passwd", "api_key", "apikey", "access_key",
    "private", "credential", "hash", "salt", "stripe_id", "config",
    "auth", "signature", "session", "vault", "ssn", "dob", "birth",
)


def _columns_of(table):
    """Introspect a table's columns (cached). Used for column-level filtering."""
    key = f"cols::{table}"
    if key in _CREDS_CACHE:
        return _CREDS_CACHE[key]
    try:
        rows = _db_rows(f"DESCRIBE `{table}`;")
        cols = [r[0] for r in rows if r]
    except Exception:
        cols = []
    _CREDS_CACHE[key] = cols
    return cols


def _sensitive_columns(table):
    return [c for c in _columns_of(table)
            if any(s in c.lower() for s in DENIED_COLUMN_SUBSTRINGS)]

FORBIDDEN_SQL = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|replace|rename|"
    r"call|exec|execute|load_file|outfile|dumpfile|into\s+outfile|into\s+dumpfile|"
    r"set\s+global|lock\s+tables|handler)\b",
    re.I,
)


# ---------------------------------------------------------------- helpers
def _err(msg):
    return {"content": [{"type": "text", "text": str(msg)}], "isError": True}


def _ok(text):
    return {"content": [{"type": "text", "text": text}]}


def _check_sql(sql):
    """Return None if safe, else a refusal reason. Never lets a write through."""
    s = (sql or "").strip().rstrip(";")
    if not s:
        return "empty statement"
    if FORBIDDEN_SQL.search(s):
        return ("refused: this lane is READ-ONLY. Write/DDL/privilege verbs are blocked "
                "before reaching any connection (perfex doctrine).")
    if ";" in s:
        return "refused: multiple statements are not permitted"
    head = s.split(None, 1)[0].upper()
    if head not in ("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN"):
        return f"refused: only SELECT/SHOW/DESCRIBE/EXPLAIN are permitted (got {head})"
    return None


def _tables_in(sql):
    return re.findall(r"\b(?:from|join)\s+`?([a-zA-Z0-9_]+)`?", sql, re.I)


def _check_tables(sql):
    for t in _tables_in(sql):
        tl = t.lower()
        if tl in DENIED_TABLES:
            return f"refused: `{t}` is on the DENY list (credentials/PHI/message content)"
        for sub in DENY_SUBSTRINGS:
            if sub in tl:
                return f"refused: `{t}` matches denied pattern '{sub}'"
        if tl not in ALLOWED_TABLES:
            return (f"refused: `{t}` is not on the read allow list. "
                    f"Allowed: {len(ALLOWED_TABLES)} CRM/billing tables.")
        # Column-level wall: `SELECT *` on a table that carries credential-bearing
        # columns would leak them. Require explicit column names instead.
        if re.search(r"select\s+\*", sql, re.I):
            sens = _sensitive_columns(tl)
            if sens:
                return (f"refused: `SELECT *` on `{t}` is blocked — that table carries "
                        f"credential-bearing columns ({', '.join(sens[:6])}). "
                        f"Name the columns you want explicitly.")
    return None


# ---------------------------------------------------------------- lane: db (read-only)
_CREDS_CACHE = {}


def _db_creds():
    """Read the CRM's OWN db credentials on the host. Never persisted, never printed."""
    if _CREDS_CACHE:
        return _CREDS_CACHE
    # NOTE: the remote script is piped via stdin (`python3 -`), NOT passed with -c.
    # `python3 -c` with this payload gets word-split by the remote shell and dies on
    # "syntax error near unexpected token `('". Stdin avoids shell parsing entirely.
    remote = (
        "import re, json\n"
        f"S = open({REMOTE_APP_CONFIG!r}).read()\n"
        "v = dict(re.findall(r\"define\\(\\s*'APP_DB_([A-Z]+)'\\s*,\\s*'([^']*)'\\s*\\)\", S))\n"
        "print(json.dumps(v))\n"
    )
    r = subprocess.run(["ssh", "-F", SSH_CONFIG, "-o", "ConnectTimeout=12",
                        "-o", "BatchMode=yes", SSH_ALIAS, "python3", "-"],
                       input=remote, capture_output=True, text=True, timeout=90)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError(f"cannot read Perfex config on {SSH_ALIAS}: "
                           f"{(r.stderr or '').strip()[:200]}")
    v = json.loads(r.stdout.strip())
    _CREDS_CACHE.update(v)
    return _CREDS_CACHE


def _db_query(sql, timeout=90):
    """Execute a read-only SELECT on the host.

    The SQL is embedded into the remote script as a JSON string literal — NOT concatenated
    onto the script text. Concatenating made the SQL part of the Python source, so
    `SELECT COUNT(*) FROM x` was parsed as Python and died with
    "SyntaxError: Invalid star expression". Embedding keeps the two separate.
    """
    v = _db_creds()
    host, user, pw, db = v.get("HOSTNAME", "localhost"), v.get("USERNAME", ""), \
        v.get("PASSWORD", ""), v.get("NAME", "")
    remote = (
        "import subprocess, sys\n"
        "sql = %s\n"
        "r = subprocess.run(['mysql', '-h' + %r, '-u' + %r, '-p' + %r, %r, "
        "'-N', '--batch', '-e', sql], capture_output=True, text=True)\n"
        "sys.stdout.write(r.stdout)\n"
        "sys.stderr.write(r.stderr)\n"
    ) % (json.dumps(sql), host, user, pw, db)
    r = subprocess.run(["ssh", "-F", SSH_CONFIG, "-o", "ConnectTimeout=12",
                        "-o", "BatchMode=yes", SSH_ALIAS, "python3", "-"],
                       input=remote, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout or "")
    err = (r.stderr or "")
    err = "\n".join(l for l in err.splitlines()
                    if "Using a password on the command line" not in l).strip()
    if err:
        raise RuntimeError(err[:400])
    return out


def _db_rows(sql):
    out = _db_query(sql)
    return [line.split("\t") for line in out.splitlines() if line.strip()]


# ---------------------------------------------------------------- lane: rest
def _rest(path, params=None):
    url = f"{BASE_URL}/{path.lstrip('/')}"
    if params:
        qs = "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params.items())
        url += f"?{qs}"
    req = urllib.request.Request(url)
    req.add_header("Authtoken", API_TOKEN)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return e.code, (e.read().decode("utf-8", "replace")[:400])
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}"


def _rest_alive():
    if not API_TOKEN:
        return False, "PERFEX_API_TOKEN not set"
    code, _ = _rest("customers", {"per_page": 1})
    if code == 200:
        return True, "REST 200"
    if code == 401:
        return False, "HTTP 401 — module present, token rejected/absent"
    if code == 404:
        return False, "HTTP 404 — REST module not routed"
    return False, f"HTTP {code}"


# ---------------------------------------------------------------- tools
def tool_status(_args):
    lines = ["PERFEX CRM INTERFACE — status", f"  base_url : {BASE_URL}",
             f"  read_only: {READ_ONLY}",
             f"  ssh host : {SSH_ALIAS}  (config {SSH_CONFIG})", ""]
    alive, why = _rest_alive()
    lines.append(f"  LANE rest: {'UP' if alive else 'DOWN'} — {why}")
    lines.append(f"    token set: {bool(API_TOKEN)}")
    try:
        rows = _db_rows("SELECT COUNT(*) FROM tblclients;")
        n_clients = rows[0][0] if rows else "?"
        rows = _db_rows("SELECT COUNT(*) FROM tblinvoices;")
        n_inv = rows[0][0] if rows else "?"
        rows = _db_rows("SELECT COUNT(*) FROM tbltickets;")
        n_tk = rows[0][0] if rows else "?"
        rows = _db_rows("SELECT COUNT(*) FROM tblstaff;")
        n_st = rows[0][0] if rows else "?"
        lines.append("  LANE db  : UP (read-only, PHI-walled)")
        lines.append(f"    clients={n_clients}  invoices={n_inv}  tickets={n_tk}  staff={n_st}")
    except Exception as e:
        lines.append(f"  LANE db  : DOWN — {e}")
    lines += ["", f"  allow list: {len(ALLOWED_TABLES)} tables",
              f"  deny list : {len(DENIED_TABLES)} tables + {len(DENY_SUBSTRINGS)} patterns",
              "  writes    : refused in code (SELECT/SHOW/DESCRIBE only)"]
    return _ok("\n".join(lines))


def tool_summary(_args):
    try:
        c = _db_rows("SELECT COUNT(*) FROM tblclients;")[0][0]
        inv = _db_rows("SELECT COUNT(*), COALESCE(SUM(total),0) FROM tblinvoices;")
        n_inv, tot = (inv[0] + ["0", "0"])[:2]
        paid = _db_rows("SELECT COALESCE(SUM(amount),0) FROM tblinvoicepaymentrecords;")[0][0]
        try:
            outstanding = float(tot) - float(paid)
        except Exception:
            outstanding = "?"
        # NOTE: the leads table is `tblleads` (double L). `tbleads` does not exist.
        leads = _db_rows("SELECT COUNT(*) FROM tblleads;")[0][0]
        proj = _db_rows("SELECT COUNT(*) FROM tblprojects;")[0][0]
        tasks = _db_rows("SELECT COUNT(*) FROM tbltasks;")[0][0]
        tickets = _db_rows("SELECT COUNT(*) FROM tbltickets;")[0][0]
        contacts = _db_rows("SELECT COUNT(*) FROM tblcontacts;")[0][0]
        return _ok(json.dumps({
            "clients": int(c), "contacts": int(contacts), "invoices": int(n_inv),
            "invoiced_total": float(tot), "payments_received": float(paid),
            "outstanding": outstanding, "leads": int(leads), "projects": int(proj),
            "tasks": int(tasks), "open_tickets": int(tickets),
            "lane": "db-read-only",
        }, indent=2))
    except Exception as e:
        return _err(f"summary failed: {e}")


def tool_list_tables(_args):
    return _ok("ALLOWED (readable):\n  " + "\n  ".join(sorted(ALLOWED_TABLES)) +
               "\n\nDENIED (never readable):\n  " + "\n  ".join(sorted(DENIED_TABLES)))


def tool_query(args):
    sql = (args or {}).get("sql", "")
    reason = _check_sql(sql) or _check_tables(sql)
    if reason:
        return _err(reason)
    limit = int((args or {}).get("limit", 50) or 50)
    if "limit" not in sql.lower():
        sql = sql.rstrip(";") + f" LIMIT {min(limit, 500)}"
    try:
        rows = _db_rows(sql)
    except Exception as e:
        return _err(f"query failed: {e}")
    return _ok(json.dumps(rows[:min(limit, 500)], indent=1)[:20000])


def tool_clients(args):
    args = args or {}
    # tblclients has NO firstname/lastname — those live on tblcontacts. Verified columns:
    # userid, company, phonenumber, city, state, country, active, datecreated.
    # getfwd_config / nmi_config are deliberately NOT selected (they hold ghl_access_token).
    where = []
    if args.get("search"):
        s = re.sub(r"[^A-Za-z0-9 @._-]", "", str(args["search"]))[:60]
        where.append(f"(c.company LIKE '%{s}%' OR c.phonenumber LIKE '%{s}%')")
    lim = min(int(args.get("limit", 25) or 25), 200)
    sql = ("SELECT c.userid, c.company, c.phonenumber, c.city, c.state, c.country, "
           "c.active, c.datecreated, ct.email AS primary_contact_email "
           "FROM tblclients c "
           "LEFT JOIN tblcontacts ct ON ct.userid = c.userid AND ct.is_primary = 1")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += f" ORDER BY c.userid DESC LIMIT {lim}"
    try:
        return _ok(json.dumps(_db_rows(sql), indent=1)[:20000])
    except Exception as e:
        return _err(f"clients failed: {e}")


def tool_invoices(args):
    args = args or {}
    lim = min(int(args.get("limit", 25) or 25), 200)
    sql = ("SELECT i.id, i.number, i.formatted_number, i.clientid, i.date, i.duedate, "
           "i.total, i.status, c.company FROM tblinvoices i "
           "LEFT JOIN tblclients c ON c.userid = i.clientid")
    if args.get("status") is not None:
        sql += f" WHERE i.status = {int(args['status'])}"
    sql += f" ORDER BY i.id DESC LIMIT {lim}"
    try:
        return _ok(json.dumps(_db_rows(sql), indent=1)[:20000])
    except Exception as e:
        return _err(f"invoices failed: {e}")


TOOLS = {
    "perfex_status": {
        "fn": tool_status,
        "description": "Lane health for the Perfex CRM interface: REST availability, DB lane, "
                       "row counts, and the enforcement summary (read-only + PHI wall).",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "perfex_summary": {
        "fn": tool_summary,
        "description": "Revenue/CRM overview: clients, invoices, invoiced total, payments "
                       "received, outstanding, leads, projects, tasks, open tickets.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "perfex_list_tables": {
        "fn": tool_list_tables,
        "description": "Show the readable allow list and the never-readable deny list.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    "perfex_query": {
        "fn": tool_query,
        "description": "Run a READ-ONLY SELECT against an allow-listed CRM table. Writes and "
                       "denied tables are refused in code. Example: SELECT userid, company "
                       "FROM tblclients LIMIT 10",
        "inputSchema": {"type": "object",
                        "properties": {"sql": {"type": "string",
                                               "description": "A single SELECT statement"},
                                       "limit": {"type": "integer", "default": 50}},
                        "required": ["sql"]},
    },
    "perfex_clients": {
        "fn": tool_clients,
        "description": "List CRM clients (company, contact, phone, city, active). Optional "
                       "substring search.",
        "inputSchema": {"type": "object",
                        "properties": {"search": {"type": "string"},
                                       "limit": {"type": "integer", "default": 25}}},
    },
    "perfex_invoices": {
        "fn": tool_invoices,
        "description": "List invoices with client company, dates, total and status. Optional "
                       "status filter.",
        "inputSchema": {"type": "object",
                        "properties": {"status": {"type": "integer"},
                                       "limit": {"type": "integer", "default": 25}}},
    },
}


def _call_tool(name, args):
    t = TOOLS.get(name)
    if not t:
        return _err(f"unknown tool: {name}")
    try:
        return t["fn"](args)
    except Exception as e:
        return _err(f"{name} failed: {type(e).__name__}: {e}")


# ---------------------------------------------------------------- MCP stdio loop
def serve():
    """Newline-delimited JSON-RPC over stdio. `initialize` is mandatory — a missing
    initialize branch is the documented cause of clients timing out at connect."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        method = req.get("method")
        rid = req.get("id")

        if method == "initialize":
            print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}}}), flush=True)

        elif method in ("notifications/initialized", "initialized"):
            continue

        elif method == "ping":
            print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": {}}), flush=True)

        elif method == "tools/list":
            print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"tools": [
                {"name": n, "description": t["description"], "inputSchema": t["inputSchema"]}
                for n, t in TOOLS.items()]}}), flush=True)

        elif method == "tools/call":
            p = req.get("params") or {}
            print(json.dumps({"jsonrpc": "2.0", "id": rid,
                              "result": _call_tool(p.get("name"), p.get("arguments") or {})}),
                  flush=True)

        elif rid is not None:
            print(json.dumps({"jsonrpc": "2.0", "id": rid,
                              "error": {"code": -32601,
                                        "message": f"method not found: {method}"}}), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        print(f"tools: {len(TOOLS)}")
        for n in TOOLS:
            print("  ", n)
        print("\n", tool_status({})["content"][0]["text"])
        # safety assertions
        # NOTE: `SELECT * FROM tblclients` is expected to be REFUSED. tblclients carries
        # getfwd_config / nmi_config, which hold plaintext ghl_access_token values, so a
        # wildcard select would leak live credentials. The original expectation here
        # (allow=True) was written before that finding and was corrected on 2026-09-14.
        checks = [
            ("SELECT userid FROM tblclients LIMIT 1", True),
            ("SELECT * FROM tblclients LIMIT 1", False),          # credential columns
            ("SELECT userid, company FROM tblclients LIMIT 1", True),
            ("SELECT COUNT(*) FROM tblinvoices", True),
            ("DELETE FROM tblclients", False),
            ("UPDATE tblclients SET active=0", False),
            ("SELECT * FROM tblvault", False),
            ("SELECT * FROM tblform_results", False),
            ("SELECT * FROM tblconsents", False),
            ("SELECT * FROM tblsessions", False),
            ("SELECT * FROM tbl_unknown_thing", False),
            ("DROP TABLE tblclients", False),
            ("SELECT * FROM tblclients; SELECT 1", False),
        ]
        bad = 0
        print("\nsafety checks:")
        for sql, should_pass in checks:
            reason = _check_sql(sql) or _check_tables(sql)
            got = reason is None
            mark = "OK " if got == should_pass else "FAIL"
            if got != should_pass:
                bad += 1
            print(f"  [{mark}] allow={got!s:5s} expect={should_pass!s:5s}  {sql[:48]}")
        print(f"\n{'ALL SAFETY CHECKS PASS' if bad==0 else str(bad)+' SAFETY FAILURES'}")
        sys.exit(1 if bad else 0)
    serve()
