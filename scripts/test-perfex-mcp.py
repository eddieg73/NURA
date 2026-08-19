#!/usr/bin/env python3
"""Perfex MCP test harness — import + SDK + tools + live probe."""
import sys, os, json, urllib.request

sys.path.insert(0, "/opt/data/mcp-installs/perfex")
os.chdir("/opt/data/mcp-installs/perfex")

try:
    import mcp
    print("mcp SDK:", getattr(mcp, "__version__", "unknown"))
except Exception as e:
    print("mcp import:", e)

try:
    import server
    tools = server.list_tools()
    names = [t.name for t in tools.tools]
    print("server loads OK | tools:", len(names))
    print("sample tools:", names[:10])
    # count by prefix
    from collections import Counter
    c = Counter(n.split("_")[0] for n in names)
    print("tool groups:", dict(c.most_common(8)))
except Exception as e:
    import traceback
    print("SERVER IMPORT FAILED:", e)
    traceback.print_exc()

# the live probe
for line in open("/opt/data/profiles/nura/.env"):
    if line.startswith("PERFEX_BASE_URL="):
        print("env base:", line.strip().split("=", 1)[1][:40])
    if line.startswith("PERFEX_API_TOKEN="):
        print("env token:", "SET" if len(line.strip().split("=", 1)[1]) > 8 else "EMPTY")
