#!/usr/bin/env python3
"""SKILL-TRACKER — the skill-metrics pipeline: count, sizes, ages, the growth-trend. (The founder's skill-tracking!)"""
import os, glob, datetime, json

SKILLS = "/opt/data/profiles/nura/skills"

def main():
    skills = []
    for p in glob.glob(SKILLS + "/**/SKILL.md", recursive=True):
        st = os.stat(p)
        skills.append({"name": os.path.basename(os.path.dirname(p)), "size": st.st_size, "mtime": st.st_mtime})
    total = len(skills)
    total_size = sum(s["size"] for s in skills)
    now = datetime.datetime.now().timestamp()
    recent = [s for s in skills if now - s["mtime"] < 7 * 86400]
    month = [s for s in skills if now - s["mtime"] < 30 * 86400]
    # the top-categories
    cats = {}
    for p in glob.glob(SKILLS + "/*/", recursive=False):
        n = len(glob.glob(p + "/**/SKILL.md", recursive=True))
        if n:
            cats[os.path.basename(p.rstrip("/"))] = n
    print(f"📚 SKILL-TRACKER — {datetime.datetime.now().strftime('%b %d, %Y')}")
    print(f"· Total skills: {total}")
    print(f"· Total size: {total_size/1024:.0f} KB")
    print(f"· New/changed (7d): {len(recent)} · (30d): {len(month)}")
    print(f"· Top categories: {', '.join(f'{k}={v}' for k, v in sorted(cats.items(), key=lambda x: -x[1])[:6])}")
    with open("/opt/data/profiles/nura/cron/output/skill-tracker.json", "w") as f:
        json.dump({"total": total, "size_kb": round(total_size/1024), "recent_7d": len(recent), "recent_30d": len(month)}, f)

if __name__ == "__main__":
    main()
