import sys
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
import prism32, inspect

src = inspect.getsource(prism32)
# find the entry/CLI handling
for i, line in enumerate(src.splitlines()):
    if "__main__" in line or "argparse" in line or "sys.argv" in line or "config.json" in line:
        print(i, line[:100])
# config keys
import re
m = re.search(r'config.*?=.*?\{[^}]{0,300}', src, re.S)
print("---config sample---")
print(m.group(0)[:300] if m else "no inline config sample")
