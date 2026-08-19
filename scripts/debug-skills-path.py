import os, glob
p = os.path.expanduser("~/profiles/nura/skills")
print("exists:", os.path.isdir(p))
if os.path.isdir(p):
    print("top-dirs:", [d for d in os.listdir(p)][:8])
    print("glob-1:", len(glob.glob(p + "/**/SKILL.md", recursive=True)))
    print("glob-2:", len(glob.glob(p + "/*/SKILL.md")))
    print("glob-3:", len(glob.glob(p + "/devops/**/SKILL.md", recursive=True)))
