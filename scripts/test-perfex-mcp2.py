#!/usr/bin/env python3
"""Perfex MCP test harness v2 — neutral identifiers."""
import sys, os

sys.path.insert(0, "/opt/data/mcp-installs/perfex")
os.chdir("/opt/data/mcp-installs/perfex")

try:
    import mcp
    print("mcp SDK:", getattr(mcp, "__version__", "unknown"))
except Exception as e:
    print("mcp import:", e)

try:
    import importlib
    mod = importlib.import_module("server")
    tools = mod.list_tools()
    names = [t.name for t in tools.tools]
    print("module loads OK | tools:", len(names))
    print("sample:", names[:10])
    from collections import Counter
    c = Counter(n.split("_")[0] for n in names)
    print("groups:", dict(c.most_common(8)))
except Exception as e:
    import traceback
    print("IMPORT FAILED:", e)
    traceback.print_exc()

for line in open("/opt/data/profiles/nura/.env"):
    if line.startswith("PERFEX_BASE_URL="):
        print("env base:", line.strip().split("=", 1)[1][:45])
    if line.startswith("PERFEX_API_TOKEN="):
        t = line.strip().split("=", 1)[1]
        print("env token:", "SET(%d chars)" % len(t) if len(t) > 8 else "EMPTY")
