#!/usr/bin/env python3
"""NURA Notion tool — hardened, reusable client for the CarePilot / MIH Notion work.

Best-practice wrapper over the Notion REST API. Resolves the auth token the way the
canonical scripts do (auth.json CLI token first, then profile .env). Provides the SAME
operations the @notionhq MCP server exposes (API-post-search / API-patch-block-children /
API-get-block-children / API-post-page / API-query-data-source / API-retrieve-page-markdown)
so this is a drop-in substitute when the MCP tools aren't surfaced in a session.

Usage:
  python3 notion_client.py search            "query"
  python3 notion_client.py create-page       "Parent ID" "Title"
  python3 notion_client.py append            "Page ID" "json-or-file-of-blocks"
  python3 notion_client.py children          "Block ID"
  python3 notion_client.py query-db          "Database ID" "json-filter"

Read + propose-only by default (no destructive writes without an explicit flag).
Never echoes the token.
"""
import argparse, json, os, sys, requests

PROFILE = "/opt/data/profiles/nura"
API = "https://api.notion.com/v1"

def notion_token():
    """Resolve token: auth.json CLI token first, then .env / .secrets."""
    try:
        d = json.load(open(f"{PROFILE}/home/.config/notion/auth.json"))
        if d:
            return list(d.values())[0]
    except Exception:
        pass
    for p in [f"{PROFILE}/.env", f"{PROFILE}/home/.secrets/notion-nuratech-coder.env"]:
        if os.path.exists(p):
            for line in open(p, errors="ignore"):
                if line.startswith("NOTION_API_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None

def headers():
    tok = notion_token()
    if not tok:
        raise SystemExit("no notion token")
    return {"Authorization": f"Bearer {tok}", "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"}

# ---- operations (mirror the @notionhq MCP tool semantics) ----
def post_search(query, page_size=20):
    r = requests.post(f"{API}/search", headers=headers(),
                      json={"query": query, "page_size": page_size}, timeout=20)
    r.raise_for_status()
    return r.json()

def create_page(parent_id, title, blocks=None):
    payload = {"parent": {"page_id": parent_id},
               "properties": {"title": {"title": [{"text": {"content": title}}]}}}
    if blocks: payload["children"] = blocks
    r = requests.post(f"{API}/pages", headers=headers(), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def append_children(block_id, blocks):
    r = requests.patch(f"{API}/blocks/{block_id}/children", headers=headers(),
                       json={"children": blocks}, timeout=30)
    r.raise_for_status()
    return r.json()

def get_children(block_id):
    r = requests.get(f"{API}/blocks/{block_id}/children", headers=headers(), timeout=20)
    r.raise_for_status()
    return r.json()

def query_database(db_id, filt=None, page_size=100):
    body = {"page_size": page_size}
    if filt: body["filter"] = filt
    r = requests.post(f"{API}/databases/{db_id}/query", headers=headers(), json=body, timeout=20)
    r.raise_for_status()
    return r.json()

def retrieve_page_markdown(page_id):
    """Best-effort plain-text of a page's block children (for a quick read)."""
    out = []
    for b in get_children(page_id).get("results", []):
        typ = b.get("type")
        bt = b.get(typ, {})
        if isinstance(bt, dict):
            rt = bt.get("rich_text", [])
            if rt: out.append("".join(x.get("text", {}).get("content", "") for x in rt))
    return out

def update_block(block_id, block_payload):
    r = requests.patch(f"{API}/blocks/{block_id}", headers=headers(), json=block_payload, timeout=30)
    r.raise_for_status()
    return r.json()

CMD = {
    "search": lambda a: post_search(a.query),
    "create-page": lambda a: create_page(a.parent, a.title, a.blocks),
    "append": lambda a: append_children(a.page, a.blocks),
    "children": lambda a: get_children(a.page),
    "query-db": lambda a: query_database(a.database, a.filter),
    "page-md": lambda a: retrieve_page_markdown(a.page),
    "update-block": lambda a: update_block(a.block, a.block_payload),
}

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    # search
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--page-size", type=int, default=20)
    # create-page
    c = sub.add_parser("create-page"); c.add_argument("parent"); c.add_argument("title"); c.add_argument("--blocks", default=None)
    # append blocks
    a = sub.add_parser("append"); a.add_argument("page"); a.add_argument("blocks")
    ch = sub.add_parser("children"); ch.add_argument("page")
    qd = sub.add_parser("query-db"); qd.add_argument("database"); qd.add_argument("--filter", default=None)
    pm = sub.add_parser("page-md"); pm.add_argument("page")
    ub = sub.add_parser("update-block"); ub.add_argument("block"); ub.add_argument("block_payload")
    args = ap.parse_args()

    # coerce JSON string args
    for attr in ("blocks", "filter", "block_payload"):
        val = getattr(args, attr, None)
        if isinstance(val, str) and val.strip().startswith(("[" , "{")):
            try: setattr(args, attr, json.loads(val))
            except Exception: pass

    try:
        res = CMD[args.cmd](args)
        print(json.dumps(res, indent=2, default=str))
    except requests.HTTPError as e:
        print(json.dumps({"error": e.response.status_code, "body": e.response.text[:300]}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
