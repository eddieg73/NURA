import re
from pathlib import Path

root = Path("/opt/data/profiles/nura/skills/devops")
skills = []
for p in root.glob("*/SKILL.md"):
    txt = p.read_text()
    m = re.search(r"^description:\s*(.+)$", txt, re.M)
    skills.append((p.parent.name, (m.group(1) if m else "")[:100]))

# token overlap between description pairs
import difflib
pairs = []
for i in range(len(skills)):
    for j in range(i + 1, len(skills)):
        a, b = skills[i][1], skills[j][1]
        if not a or not b:
            continue
        r = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
        if r > 0.35:
            pairs.append((round(r, 2), skills[i][0], skills[j][0]))
pairs.sort(reverse=True)
print("similar pairs (ratio > 0.35):")
for r, x, y in pairs:
    print(f"  {r:.2f}  {x}  <->  {y}")
print("total devops skills:", len(skills))
