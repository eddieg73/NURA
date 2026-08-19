import sys, inspect
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
import prism32
src = inspect.getsource(prism32)
lines = src.splitlines()
# print the argparse block
for i in range(8597, 8620):
    print(lines[i][:110])
# find config schema keys
for i, line in enumerate(lines):
    if "PROVIDER_REGISTRY" in line and "default" in line.lower():
        print("PROV:", line[:110])
# find CONFIG default keys near 4120
for i in range(4120, 4140):
    if "CONFIG" in lines[i] or "config" in lines[i]:
        print(i, lines[i][:110])
