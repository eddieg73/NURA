#!/usr/bin/env python3
"""Add the 'get a GitHub token' task to the Notion Master Tasks DB (canonical)."""
import os, json, sys
import importlib.util
sys.path.insert(0, "/opt/data/scripts")
import importlib
# load the module without running __main__
spec = importlib.util.spec_from_file_location("nte", "/opt/data/scripts/notion_exec_tools.py")
nte = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nte)

r = nte._add_task(
    title="Generate a fresh GitHub PAT (classic: repo + project scopes), set as GITHUB_TOKEN in /opt/data/profiles/nura/.env. Unblocks creating the GitHub Projects Kanban board and syncing it to Notion.",
    status="To Do",
    priority="P1",
    owner="Eddie",
    source="Decision",
    project="NURA GitHub Projects",
    commitment=True,
)
print(json.dumps(r, indent=2, default=str))
