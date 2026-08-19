import sys
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
import prism32, inspect

src = inspect.getsource(prism32)
print("single file:", prism32.__file__)
print("size KB:", len(src) // 1024)
print("has harness scan:", "harness scan" in src)
print("has quantum:", "quantum" in src.lower())
print("has fenced-blocks:", "```" in src or "ask" in src)
print("stdlib only check (imports):", [l for l in src.splitlines() if l.startswith("import ") or l.startswith("from ")][:6])
