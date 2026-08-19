import re
s = open("/opt/data/profiles/nura/config.yaml").read()
idx = s.find("mcp_servers:")
block = s[idx:idx+8000]
servers = re.findall(r"^  ([a-zA-Z0-9_]+):", block, re.M)
enabled = {}
for m in re.finditer(r"^  ([a-zA-Z0-9_]+):\n((?:    .*\n)*)", block, re.M):
    name = m.group(1)
    e = re.search(r"enabled: (true|false)", m.group(2))
    enabled[name] = e.group(1) if e else "?"
print("registered:", len(servers))
for name in servers:
    print(f"  {name}: enabled={enabled.get(name, '?')}")
